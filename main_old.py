import sys
import os
import threading
import asyncio
import time
import tkinter
from tkinter import messagebox
from PIL import Image
from pystray import Icon, Menu, MenuItem as item
from Last_fm_api import LastFmUser
import DiscordRPC

rpc_state = True

def toggle_rpc(Icon, item):
    global rpc_state
    rpc_state = not item.checked


def exit(Icon, item):
    icon_tray.stop()

directory = os.path.dirname(__file__)
imageDir = os.path.join(directory, "assets/icon.png")

root = tkinter.Tk()
root.withdraw()

try:
    im = Image.open(imageDir)
except FileNotFoundError as identifier:
    messagebox.showerror('Error','Assets folder not found!')

try:
    f = open('username.txt', 'r')
except FileNotFoundError as identifier:
    messagebox.showerror('Error','File "username.txt" not found!')

username = f.read()
print("Last.fm username: "+username)
User = LastFmUser(username, 2)

menu_icon = Menu(item('User: '+username, None), item('Enable Rich Presence',
                                                     toggle_rpc, checked=lambda item: rpc_state), Menu.SEPARATOR, item('Exit', exit))
icon_tray = Icon('Last.fm Discord Rich Presence', icon=im,
                 title="Last.fm Discord Rich Presence", menu=menu_icon)

def RPCFunction(loop):
    print("Starting RPC")
    asyncio.set_event_loop(loop)
    while True:
        if rpc_state == True:
            User.now_playing()
        else:
            DiscordRPC.disconnect()
            time.sleep(2)

loop = asyncio.new_event_loop()
RPCThread = threading.Thread(target=RPCFunction, args=(loop,))

RPCThread.daemon = True
RPCThread.start()

icon_tray.run()
