#
# This file is part of SR2Control tool.
# (c) Copyright 2024 by Domtaro
# Licensed under the LGPL-3.0; see LICENSE.txt file.
#
import os
import argparse
import configparser

import keyboard
import mouse

from sr2ctrl.__main__ import main as sr2ctrl_main
from multiprocessing import freeze_support

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config", action="store", default=r".\sr2ctrl\settings\SR2Control_settings.ini",
                        help="config file")
    parser.add_argument("-t", "--test", action="store_true", default=False,
                        help="start as test mode. the behavior depends on implementation of grammar.")
    args = parser.parse_args()

    config_path = args.config
    drive, directory = os.path.splitdrive(config_path)
    if drive != "":
        config_path = os.path.normcase(config_path).replace(os.path.normcase(os.getcwd()), r".")
    if not os.path.isfile(config_path):
        print(f"ERROR: invalid file name('{args.config}') given as config file!")
        print("exit...")
        return

    config = configparser.ConfigParser()
    try:
        config.read(args.config, encoding="utf-8")
    except Exception as e:
        print(e)
    user_config = config["USERS"]

    print("")
    print(" -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-")
    print("         SR2Control tool        ")
    print(" -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-")
    print("  (c) Copyright 2024 by Domtaro")
    print("")

    mode = user_config.get("mode").lower()

    # Get-Key-Name mode
    if (mode == "getkeyname"):
        print("press any keys which you want to check the key name.")
        print(r"input [ctrl] + [c] to exit.")
        def on_press_kb(event):
            print(event.name)
        keyboard.on_press(on_press_kb)
        def on_press_mb(event):
            if isinstance(event, mouse.ButtonEvent):
                if event.event_type == "down": print(event.button)
        mouse.hook(on_press_mb)
        keyboard.wait(hotkey="ctrl+c", suppress=False, trigger_on_release=False)
        keyboard.unhook_all_hotkeys()
        mouse.unhook_all()
        print(r"[ctrl] + [c] pressed. exit...")
        return # end the program

    # extract values in the config file
    grammar_path = user_config.get("grammar")
    port = user_config.getint("port")
    ptt_mode = user_config.get("ptt_mode").lower()
    ptt_key = user_config.get("ptt_key")

    # normalize and check the grammar file path
    drive, directory = os.path.splitdrive(grammar_path)
    del directory
    if drive != "":
        grammar_path = os.path.normcase(grammar_path).replace(os.path.normcase(os.getcwd()), r".")
    if not os.path.isfile(grammar_path):
        print(f"ERROR: invalid file name('{user_config.get("grammar")}') given as grammar!")
        print("exit...")
        return

    # main process
    sr2ctrl_main(grammar_path=grammar_path, port=port, mode=mode, test=args.test, ptt_mode=ptt_mode, ptt_key=ptt_key)
    print("exit...")

if __name__ == "__main__":
    freeze_support()
    main()
