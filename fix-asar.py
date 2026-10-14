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

Each patched file keeps its length, so no offsets in the archive move; its
integrity hashes in the header are refreshed (hex digests, same length too).
The minified names are build-specific: a new upstream build fails loudly here.

Usage: python3 fix-asar.py path/to/app.asar
"""
import hashlib
import json
import struct
import sys

FIXES = {
    '.vite/renderer/assets/sentry-renderer-DsYx9lPP.js': [
        ('send:(t,...n)=>{window.isElectron&&window.ipcRenderer&&!e.deviceInformation.isClosing&&',
         'send:(t,...n)=>{window.ipcRenderer&&!e.deviceInformation?.isClosing&&'),
        ('invoke:async(t,...n)=>{if(window.isElectron&&window.ipcRenderer&&!e.deviceInformation.isClosing)',
         'invoke:async(t,...n)=>{if(window.ipcRenderer&&!e.deviceInformation?.isClosing)'),
    ],
    '.vite/build/main.js': [
        ('function Vc(e){let t=process.execPath;return process.env.APPIMAGE?t=`"${process.env.APPIMAGE}" --no-sandbox`:u.app.isPackaged&&(t=u.app.getPath(`exe`)),e&&(t+=` ${aA}`),t}',
         'function Vc(e){let t=`/usr/bin/exolve-messenger`;return e&&(t+=` ${aA}`),t}'),
    ],
}


def main(path):
    with open(path, 'r+b') as f:
        _, header_buf_size, _, header_size = struct.unpack('<4I', f.read(16))
        header_raw = f.read(header_size)
        header = json.loads(header_raw)
        if json.dumps(header, separators=(',', ':'), ensure_ascii=False).encode() != header_raw:
            sys.exit('asar header does not round-trip through json, refusing to patch')
        base = 8 + header_buf_size

        patched = []
        for target, fixes in FIXES.items():
            node = header
            for part in target.split('/'):
                node = node['files'][part]
            off, size = base + int(node['offset']), node['size']
            f.seek(off)
            data = f.read(size)

            for old, new in fixes:
                old, new = old.encode(), new.encode()
                if data.count(old) != 1:
                    sys.exit(f'{target}: pattern not found exactly once (new upstream build?): {old[:40]!r}')
                data = data.replace(old, new.ljust(len(old), b' '))

            integrity = node['integrity']
            block_size = integrity['blockSize']
            integrity['hash'] = hashlib.sha256(data).hexdigest()
            integrity['blocks'] = [hashlib.sha256(data[i:i + block_size]).hexdigest()
                                   for i in range(0, len(data), block_size)]
            patched.append((off, data))

        new_raw = json.dumps(header, separators=(',', ':'), ensure_ascii=False).encode()
        if len(new_raw) != len(header_raw):
            sys.exit('asar header length changed, refusing to patch')

        # Write only once every pattern matched, so a failure leaves the file intact
        for off, data in patched:
            f.seek(off)
            f.write(data)
        f.seek(16)
        f.write(new_raw)

    for target in FIXES:
        print(f'patched {target}')


if __name__ == '__main__':
    main(sys.argv[1])
