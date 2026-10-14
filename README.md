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

- **Исправлен белый экран при запуске.** В коде приложения есть гонка: `send()` обращается к `deviceInformation.isClosing` до того, как `deviceInformation` загружен. Исключение падает в `setup()` главного компонента, и интерфейс не монтируется (у меня так было в 6 запусках из 8). [`fix-asar.py`](fix-asar.py) при сборке добавляет недостающую проверку прямо в `app.asar`. Если в новой сборке МТС код поменяется, скрипт явно упадёт, и `makepkg` не соберёт пакет без патча.
- **Пункт меню ведёт на обёртку.** При каждом запуске приложение перезаписывает `~/.local/share/applications/mtt-messenger.desktop`, указывая в `Exec` сам бинарник Electron, то есть в обход обёртки и X11. Тот же патч подставляет туда `/usr/bin/exolve-messenger`. Системный `.desktop` переименован в `mtt-messenger.desktop`, чтобы в меню не было двух пунктов.
- **`chrome-sandbox` без setuid.** Ядра Arch разрешают непривилегированные user namespaces, и песочнице Chromium setuid-помощник не нужен.
- **Автообновление выключено самим приложением**: оно проверяет обновления, только если в `resources/package-type` записано не `deb`. Файл оставлен как есть, обновления приходят через этот PKGBUILD.
- Иконка перенесена в `hicolor`, удалены `lintian` и `doc`.

## Обновление версии

У сервера Exolve нет ссылок на конкретные версии: по адресу `latest` всегда лежит последняя сборка. Поэтому после выхода новой версии старая контрольная сумма перестаёт совпадать и `makepkg` падает на проверке. Чтобы обновить пакет:

```sh
./bump          # узнаёт версию на сервере, обновляет pkgver, sha256sums и .SRCINFO
makepkg -si
```

Для `bump` нужен `pacman-contrib` (`updpkgsums`).

## Лицензия

Файлы сборки — [0BSD](LICENSE). Само приложение проприетарное (© МТС Exolve / ITooLabs).
