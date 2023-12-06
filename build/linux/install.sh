#!/bin/bash

set -e

if [ "$(dirname "$(realpath "$0")")" != "$(realpath "$PWD")" ]; then
  echo "Please run from the folder install.sh is in."
  exit 1
fi

if [[ $* == *--all-users* ]]; then
	PREFIX=/usr/local
else
  PREFIX=~/.local
fi

rm -rf "$PREFIX"/lib/discord_fm "$PREFIX"/bin/discord_fm
mkdir -p "$PREFIX"/lib/discord_fm
cp -av --no-preserve=owner,context -- * "$PREFIX"/lib/discord_fm/
mkdir -p "$PREFIX"/bin
ln -sf "$PREFIX"/lib/discord_fm/discord_fm "$PREFIX"/bin/discord_fm
mkdir -p "$PREFIX"/share/applications
mv -Z "$PREFIX"/lib/discord_fm/discord_fm.desktop "$PREFIX"/share/applications/

rm "$PREFIX"/lib/discord_fm/install.sh

echo "Install complete. Type 'discord_fm' to run."
