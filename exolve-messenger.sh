#!/bin/sh
# Under native Wayland the bundled Electron 44 crashes on startup with SIGTRAP
# most of the time (reproduced on niri), so default to X11 via XWayland.
# Put your own flags, one per line, in ~/.config/exolve-messenger-flags.conf
# to override the default (e.g. --ozone-platform=wayland to try native Wayland).

flags_file="${XDG_CONFIG_HOME:-$HOME/.config}/exolve-messenger-flags.conf"

if [ -r "$flags_file" ]; then
  # Word splitting is intended: one flag per line, '#' starts a comment
  # shellcheck disable=SC2046
  set -- $(sed 's/#.*//' "$flags_file") "$@"
else
  set -- --ozone-platform=x11 "$@"
fi

exec /usr/lib/exolve-messenger/exolve-messenger "$@"
