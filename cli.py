#
# This file is part of SR2Control tool.
# (c) Copyright 2024 by Domtaro
# Licensed under the LGPL-3.0; see LICENSE.txt file.
#
import os
import argparse

import keyboard
import mouse

from sr2ctrl.__main__ import main as sr2ctrl_main
from multiprocessing import freeze_support

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-g", "--grammar", action="store", default=r"",
                        help="grammar file, rules of actions.")
    parser.add_argument("-m", "--mode", action="store", default=r"UDP",
                        help="mode of SR result receiving, case-insensitive."
                            + " 'UDP':default."
                            + " 'YNC_bouyomi':bouyomi plugin of Yukarinette Connector NEO."
                        )
    parser.add_argument("-p", "--port", action="store", default=25555,
                        help="listening port to recieve SR result. default is 25555.")
    parser.add_argument("-t", "--test", action="store_true",
                        help="start as test mode. keys will not pressed actually.")
    parser.add_argument("-k", "--get_key_name", action="store_true",
                        help="check the keys name you pressed.")
    args = parser.parse_args()

    print("")
    print(" -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-")
    print("         SR2Control tool        ")
    print(" -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-")
    print("  (c) Copyright 2024 by Domtaro")
    print("")

    if args.get_key_name:
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
        return
    grammar_path = args.grammar
    drive, directory = os.path.splitdrive(args.grammar)
    if drive != "":
        grammar_path = os.path.normcase(args.grammar).replace(os.path.normcase(os.getcwd()), r".")
    if not os.path.isfile(grammar_path):
        print("ERROR: invalid file name given as grammar! (-g option)")
        print("exit...")
        return

    sr2ctrl_main(grammar_path=grammar_path, port=int(args.port), mode=(args.mode).lower(), test=args.test)
    print("exit...")

if __name__ == "__main__":
    freeze_support()
    main()
