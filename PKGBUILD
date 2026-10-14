# Maintainer: Vlad Wild <ya.vlash1 at yandex dot ru>

pkgname=exolve-messenger-bin
_pkgname=exolve-messenger
pkgver=4.6.0
pkgrel=1
pkgdesc="Corporate messenger for MTS Exolve virtual PBX (repackaged official Astra Linux .deb)"
arch=('x86_64')
url="https://vpbxdocs.exolve.ru/messenger_overview"
license=('LicenseRef-proprietary')
depends=(
  'alsa-lib'
  'at-spi2-core'
  'gtk3'
  'libcups'
  'libnotify'
  'libxcomposite'
  'libxdamage'
  'libxkbcommon'
  'libxrandr'
  'mesa'
  'nss'
  'xdg-utils'
)
optdepends=(
  'xorg-xwayland: default X11 mode under a Wayland compositor (xwayland-satellite on niri)'
  'xdg-desktop-portal: file dialogs and screen sharing'
)
provides=("$_pkgname")
conflicts=("$_pkgname")
options=('!strip' '!debug')
# The server has no per-version URLs: any path serves the latest build,
# so the checksum breaks as soon as a new version ships. Run ./bump then.
source=("$_pkgname-$pkgver.deb::https://communicator.vats.exolve.ru/communicator4/linux_x64/latest?filetype=deb"
        "$_pkgname.sh")
noextract=("$_pkgname-$pkgver.deb")
sha256sums=('0b5d6df83e95de7a45c681753de174cbd3afac79a8d07d98ec1817535f24e33b'
            '709af67db75efb175d020709143cfd091348e97de1a707ab1f75c8c4cb20fedd')

prepare() {
  mkdir -p deb
  bsdtar -xOf "$_pkgname-$pkgver.deb" data.tar.xz | bsdtar -xf - -C deb
}

package() {
  cp -a deb/usr "$pkgdir/"

  # Debian leftovers
  rm -r "$pkgdir/usr/share/lintian"

  # Arch kernels allow unprivileged user namespaces, so Chromium's
  # namespace sandbox works without the setuid helper.
  chmod 755 "$pkgdir/usr/lib/$_pkgname/chrome-sandbox"

  # /usr/bin/exolve-messenger was a symlink to the Electron binary
  rm "$pkgdir/usr/bin/$_pkgname"
  install -Dm755 "$srcdir/$_pkgname.sh" "$pkgdir/usr/bin/$_pkgname"

  install -Dm644 "$pkgdir/usr/share/pixmaps/$_pkgname.png" \
    "$pkgdir/usr/share/icons/hicolor/256x256/apps/$_pkgname.png"
  rm -r "$pkgdir/usr/share/pixmaps"

  # The .deb ships only Electron's MIT notice; the app itself is proprietary
  install -Dm644 "$pkgdir/usr/share/doc/$_pkgname/copyright" \
    "$pkgdir/usr/share/licenses/$pkgname/LICENSE.electron"
  rm -r "$pkgdir/usr/share/doc"
}
