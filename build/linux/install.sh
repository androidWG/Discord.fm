#!/bin/bash

set -e

if [ "$(dirname "$(realpath "$0")")" != "$(realpath "$PWD")" ]; then
  echo "Please run from the folder install.sh is in."
  exit 1
fi

if [[ $(pidof discord_fm) ]]; then
  echo "Waiting for Discord.fm to finish running"
  tail --pid="$(pidof discord_fm)" -f /dev/null
fi

if [[ $* == *--all-users* ]]; then
	PREFIX=/usr/local
else
  PREFIX=~/.local
fi

rm -rf "$PREFIX"/share/discord_fm "$PREFIX"/bin/discord_fm
mkdir -p "$PREFIX"/share/discord_fm
cp -av --no-preserve=owner,context -- * "$PREFIX"/share/discord_fm/
mkdir -p "$PREFIX"/bin
ln -sf "$PREFIX"/share/discord_fm/discord_fm "$PREFIX"/bin/discord_fm
mkdir -p "$PREFIX"/share/icons/hicolor/scalable/apps
mkdir -p "$PREFIX"/share/applications
cd "$PREFIX"/share/discord_fm && (\
mv -Z discord_fm.svg "$PREFIX"/share/icons/hicolor/scalable/apps/;\
mv -Z discord_fm.desktop "$PREFIX"/share/applications/)

rm install.sh

if [[ $* == *--self-start* ]]; then
  echo "Install complete. Running Discord.fm"
  "$PREFIX"/bin/discord_fm &
else
  echo "Install complete. Type 'discord_fm' to run."
fi
