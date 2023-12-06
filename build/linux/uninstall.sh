#!/bin/bash

set -e

if [[ $* == *--all-users* ]]; then
	PREFIX=/usr/local
else
  PREFIX=~/.local
fi

rm -rf "$PREFIX"/lib/discord_fm
rm -rf "$PREFIX"/bin/discord_fm
rm -rf "$PREFIX"/share/applications/discord_fm.desktop

echo "Uninstall complete."
