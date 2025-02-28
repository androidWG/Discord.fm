#!/bin/bash

set -e

if [ "$(dirname "$(realpath "$0")")" != "$(realpath "$PWD")" ]; then
  echo "Please run from the folder uninstall.sh is in."
  exit 1
fi

if [[ $(pidof discord_fm) ]]; then
  echo "Waiting for Discord.fm to finish running"
  tail --pid="$PID" -f /dev/null
fi

if [[ $* == *--all-users* ]]; then
	PREFIX=/usr/local
else
  PREFIX=~/.local
fi

rm -rf "$PREFIX"/share/discord_fm
rm -f "$PREFIX"/bin/discord_fm
rm -f "$PREFIX"/share/applications/discord_fm.desktop
rm -f "$PREFIX"/share/icons/hicolor/scalable/apps/discord_fm.svg

echo "Uninstall complete."
