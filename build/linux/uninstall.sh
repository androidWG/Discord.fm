#!/bin/bash

set -e

PID=$(pidof discord_fm)
if [ -n "$PID" ]; then
  echo "Waiting for Discord.fm to finish running"
  tail --pid="$PID" -f /dev/null
fi

if [[ $* == *--all-users* ]]; then
	PREFIX=/usr/local
else
  PREFIX=~/.local
fi

rm -rf "$PREFIX"/lib/discord_fm
rm -rf "$PREFIX"/bin/discord_fm
rm -rf "$PREFIX"/share/applications/discord_fm.desktop
rm -rf "$PREFIX"/share/icons/hicolor/scalable/apps/discord_fm.png

echo "Uninstall complete."
