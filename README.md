# exolve-messenger-bin

PKGBUILD для Arch Linux: [Мессенджер Exolve](https://vpbxdocs.exolve.ru/messenger_overview) (клиент виртуальной АТС МТС Exolve), перепакованный из официального `.deb` для Astra Linux.

В репозитории только скрипты сборки. Сам `.deb` при сборке скачивается с сервера Exolve, бинарники здесь не хранятся и не распространяются.

## Установка

```sh
git clone https://github.com/vlad-wild/exolve-messenger-bin.git
cd exolve-messenger-bin
makepkg -si
```

## Отличия от .deb

- **X11 по умолчанию.** Встроенный Electron 44 под нативным Wayland почти всегда падает при запуске с `SIGTRAP` (проверено на niri, в том числе с Electron 44.6.0 и с `--disable-gpu`). Поэтому `/usr/bin/exolve-messenger` — обёртка, которая запускает приложение с `--ozone-platform=x11` через XWayland. Чтобы задать свои флаги, положите их по одному на строку в `~/.config/exolve-messenger-flags.conf`; тогда флаг по умолчанию не добавляется:

  ```text
  # попробовать нативный Wayland
  --ozone-platform=wayland
  ```

- **`chrome-sandbox` без setuid.** Ядра Arch разрешают непривилегированные user namespaces, и песочнице Chromium setuid-помощник не нужен.
- **Автообновление выключено самим приложением**: оно проверяет обновления, только если в `resources/package-type` записано не `deb`. Файл оставлен как есть, обновления приходят через этот PKGBUILD.
- Иконка перенесена в `hicolor`, удалены `lintian` и `doc`.

## Обновление версии

У сервера Exolve нет ссылок на конкретные версии: по адресу `latest` всегда лежит последняя сборка. Поэтому после выхода новой версии старая контрольная сумма перестаёт совпадать и `makepkg` падает на проверке.

Раз в сутки GitHub Actions ([update.yml](.github/workflows/update.yml)) проверяет сервер, собирает новую версию и коммитит обновлённые `PKGBUILD` и `.SRCINFO`. Так что обычно достаточно `git pull && makepkg -si`. Вручную:

```sh
./bump          # узнаёт версию на сервере, обновляет pkgver, sha256sums и .SRCINFO
makepkg -si
```

Для `bump` нужен `pacman-contrib` (`updpkgsums`).

## Лицензия

Файлы сборки — [0BSD](LICENSE). Само приложение проприетарное (© МТС Exolve / ITooLabs).
