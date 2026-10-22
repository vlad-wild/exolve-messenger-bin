"""Same-length patches of the upstream app.asar.

1. Blank white window. send() and invoke() read e.deviceInformation.isClosing
   without the e.deviceInformation&& guard their sibling functions have. When
   the calls window asks for a state sync before deviceInformation has arrived
   from the main process, send() throws inside the main component's setup(),
   Vue never mounts the UI and the window stays blank white.

2. Desktop entry bypassing the wrapper. On every start the app (re)writes
   ~/.local/share/applications/mtt-messenger.desktop with Exec pointing at the
   Electron binary itself, so launching from the menu skips /usr/bin's wrapper
   and its X11 default. Point Exec at the wrapper instead.

Bundle file names carry content hashes and minified identifiers change between
builds, so each fix is a regex searched across all of the app's own .js files
and must match exactly once overall; otherwise nothing is written.

Each patched file keeps its length, so no offsets in the archive move; its
integrity hashes in the header are refreshed (hex digests, same length too).

Usage: python3 fix-asar.py path/to/app.asar
"""
import hashlib
import json
import re
import struct
import sys

ID = rb'([\w$]+)'

FIXES = [
    ('send() guard',
     rb'send:\(' + ID + rb',\.\.\.' + ID + rb'\)=>\{window\.isElectron&&window\.ipcRenderer&&!'
     + ID + rb'\.deviceInformation\.isClosing&&',
     rb'send:(\1,...\2)=>{window.ipcRenderer&&!\3.deviceInformation?.isClosing&&'),
    ('invoke() guard',
     rb'invoke:async\(' + ID + rb',\.\.\.' + ID + rb'\)=>\{if\(window\.isElectron&&window\.ipcRenderer&&!'
     + ID + rb'\.deviceInformation\.isClosing\)',
     rb'invoke:async(\1,...\2)=>{if(window.ipcRenderer&&!\3.deviceInformation?.isClosing)'),
    ('desktop entry Exec',
     rb'function ' + ID + rb'\(' + ID + rb'\)\{let ' + ID + rb'=process\.execPath;'
     rb'return process\.env\.APPIMAGE\?\3=`"\$\{process\.env\.APPIMAGE\}" --no-sandbox`:'
     + ID + rb'\.app\.isPackaged&&\(\3=\4\.app\.getPath\(`exe`\)\),\2&&\(\3\+=` \$\{' + ID + rb'\}`\),\3\}',
     rb'function \1(\2){let \3=`/usr/bin/exolve-messenger`;return \2&&(\3+=` ${\5}`),\3}'),
]


def walk(node, prefix=''):
    for name, child in node.get('files', {}).items():
        path = f'{prefix}/{name}' if prefix else name
        if 'files' in child:
            yield from walk(child, path)
        else:
            yield path, child


def main(path):
    with open(path, 'r+b') as f:
        _, header_buf_size, _, header_size = struct.unpack('<4I', f.read(16))
        header_raw = f.read(header_size)
        header = json.loads(header_raw)
        if json.dumps(header, separators=(',', ':'), ensure_ascii=False).encode() != header_raw:
            sys.exit('asar header does not round-trip through json, refusing to patch')
        base = 8 + header_buf_size

        files = {}
        for name, node in walk(header):
            if name.startswith('node_modules/') or not name.endswith('.js') or 'offset' not in node:
                continue
            f.seek(base + int(node['offset']))
            files[name] = (node, f.read(node['size']))

        changed = {}
        for label, pattern, repl in FIXES:
            hits = [(name, m) for name, (_, data) in files.items()
                    for m in re.finditer(pattern, changed.get(name, data))]
            if len(hits) != 1:
                sys.exit(f'{label}: expected exactly 1 match, found {len(hits)} (new upstream build?)')
            name, m = hits[0]
            new = m.expand(repl)
            if len(new) > len(m.group(0)):
                sys.exit(f'{label}: replacement is longer than the original')
            data = changed.get(name, files[name][1])
            changed[name] = data[:m.start()] + new.ljust(len(m.group(0)), b' ') + data[m.end():]
            print(f'{label}: {name}')

        for name, data in changed.items():
            integrity = files[name][0]['integrity']
            block_size = integrity['blockSize']
            integrity['hash'] = hashlib.sha256(data).hexdigest()
            integrity['blocks'] = [hashlib.sha256(data[i:i + block_size]).hexdigest()
                                   for i in range(0, len(data), block_size)]
        new_raw = json.dumps(header, separators=(',', ':'), ensure_ascii=False).encode()
        if len(new_raw) != len(header_raw):
            sys.exit('asar header length changed, refusing to patch')

        # Write only once every fix matched, so a failure leaves the file intact
        for name, data in changed.items():
            f.seek(base + int(files[name][0]['offset']))
            f.write(data)
        f.seek(16)
        f.write(new_raw)


if __name__ == '__main__':
    main(sys.argv[1])
