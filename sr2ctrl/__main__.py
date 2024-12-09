#
# This file is part of SR2Control tool.
# (c) Copyright 2024 by Domtaro
# Licensed under the LGPL-3.0; see LICENSE.txt file.
#
import os
import sys
import re
import datetime
import socket
import importlib.util
import requests
import winreg
import keyboard

def main(grammar_path, port, mode, test, ptt_mode, ptt_key):
	print(datetime.datetime.now().strftime(r"%Y.%m.%d %H:%M:%S"))
	print(r"(press [ctrl] + [pause/break] to exit)")
	if test:
		print("")
		print(r"(!) Test Mode Enabled")

	path = os.path.abspath(grammar_path)
	name = os.path.basename(grammar_path).split(".")[0]
	try:
		spec = importlib.util.spec_from_file_location(name, path)
		my_grammar = importlib.util.module_from_spec(spec)
		sys.modules[name] = my_grammar
		spec.loader.exec_module(my_grammar)
		my_obj = my_grammar.SR2C(test=test)
	except Exception as e:
		print("ERROR: grammar import failed!")
		print(e)
		return

	host_address = "127.0.0.1"
	local_address = (host_address, port)

	# PTT
	# grobal listening state manager object
	class ListeningState(object):
		def __init__(self):
			# -1 = off, 0 = Push To Talk, 1 = Push To Mute, 2 = Push to Toggle
			self._mode = -1
			# true = unmuted, false = muted
			self._state = False
			self.is_bt = False
		def get_mode(self):
			return self._mode
		def set_mode(self, mode):
			self._mode = mode
		def get_state(self):
			return self._state
		def set_state(self, state):
			self._state = state
		def set_switcher(self, switcher):
			# register a switch method
			self._switcher = switcher
		def get_switcher(self):
			return self._switcher
	# grobal ptt handler
	def on_press(event):
		_key = event.name
		_switcher = lsmgr.get_switcher()
		match lsmgr.get_mode():
			# push to talk - press down (to mute off)
			case 0 if keyboard.is_pressed(_key) and (not lsmgr.get_state()): _switcher(False)
			# push to talk - press up (to mute on)
			case 0 if (not keyboard.is_pressed(_key)) and lsmgr.get_state(): _switcher(True)
			# push to mute - press down (to mute on)
			case 1 if keyboard.is_pressed(_key) and lsmgr.get_state(): _switcher(True)
			# push to mute - press up (to mute off)
			case 1 if (not keyboard.is_pressed(_key)) and (not lsmgr.get_state()): _switcher(False)
			# toggle - press down (to switch mute on/off)
			case 2 if keyboard.is_pressed(_key):
				if lsmgr.get_state(): _switcher(True)
				else: _switcher(False)
	txt_mute_on = "--- Mic OFF ---"
	txt_mute_off = "--- Mic ON ---"
	# PTT setup for built-in
	def ptt_bt():
		# switcher
		def switch_mute(_flag):
			if _flag:
				# mute on
				lsmgr.set_state(False)
				print(txt_mute_on)
			else:
				# mute off
				lsmgr.set_state(True)
				print(txt_mute_off)
		lsmgr.set_switcher(switch_mute)
	# PTT setup for YNCNEO
	def ptt_ync():
		ync_port = 15520
		# get YNC receive port from registry
		with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"SOFTWARE\YukarinetteConnectorNeo") as key:
			ync_port, idx = winreg.QueryValueEx(key, "HTTP")
			del idx
		url_prefix = r"http://127.0.0.1:"
		url_mute_on = url_prefix + str(ync_port) + r"/api/mute-on"
		url_mute_off = url_prefix + str(ync_port) + r"/api/mute-off"
		# set initial state
		if lsmgr.get_mode() == 0:
			_response = requests.get(url_mute_on)
		else:
			_response = requests.get(url_mute_off)
		# switcher
		def switch_mute(_flag):
			if _flag:
				# mute on
				_response = requests.get(url_mute_on)
				lsmgr.set_state(False)
				print(txt_mute_on)
			else:
				# mute off
				_response = requests.get(url_mute_off)
				lsmgr.set_state(True)
				print(txt_mute_off)
		lsmgr.set_switcher(switch_mute)
	# setup PTT
	lsmgr = ListeningState()
	print("")
	txt_ptt_mode = "PTT MODE: "
	match ptt_mode:
		# off
		case "off":
			print(txt_ptt_mode + "Off")
		# built-in
		case "bt_0": # push to talk
			print(txt_ptt_mode + "Built-in Push-to-Talk")
			lsmgr.set_mode(0)
			lsmgr.set_state(False)
			lsmgr.is_bt = True
			ptt_bt()
		case "bt_1": # push to mute
			print(txt_ptt_mode + "Built-in Push-to-Mute")
			lsmgr.set_mode(1)
			lsmgr.set_state(True)
			lsmgr.is_bt = True
			ptt_bt()
		case "bt_2": # toggle
			print(txt_ptt_mode + "Built-in Push-to-Toggle")
			lsmgr.set_mode(2)
			lsmgr.set_state(True)
			lsmgr.is_bt = True
			ptt_bt()
		# YNC
		case "ync_0": # push to talk
			print(txt_ptt_mode + "YNC Push-to-Talk")
			lsmgr.set_mode(0)
			lsmgr.set_state(False)
			ptt_ync()
		case "ync_1": # push to mute
			print(txt_ptt_mode + "YNC Push-to-Mute")
			lsmgr.set_mode(1)
			lsmgr.set_state(True)
			ptt_ync()
		case "ync_2": # push to toggle
			print(txt_ptt_mode + "YNC Push-to-Toggle")
			lsmgr.set_mode(2)
			lsmgr.set_state(True)
			ptt_ync()
		case _: # undefined
			print(f"WARNING: invalid ptt_mode('{ptt_mode}') given! continue with default value('off')")
			print(txt_ptt_mode + "Off")
	# hooker
	if ptt_mode != "off": keyboard.hook_key(keyboard.parse_hotkey(ptt_key), on_press)

	txt_start_listen = "Start to listen..."
	txt_stop_running = "Stop running..."

	omit_chars = r"[ 　,.，．、。]*"

	# UDP mode
	def recv_udp():
		my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		my_socket.bind(local_address)
		my_socket.settimeout(0.5)
		print("")
		print(txt_start_listen)
		try:
			while True:
				try:
					message_bytes = my_socket.recv(4096)
					if (message_bytes != b""):
						message_text = message_bytes.decode(encoding="utf-8", errors="replace")
						message_text = re.sub(omit_chars, "", message_text)
						if message_text != "":
							if not lsmgr.is_bt:
								my_obj.on_recognition(message_text)
							elif lsmgr.get_state():
								my_obj.on_recognition(message_text)
				except socket.timeout:
					continue
				except KeyboardInterrupt:
					raise
				except Exception:
					raise
		except KeyboardInterrupt:
			pass
		except Exception as e:
			print(e)
		finally:
			print(txt_stop_running)
			my_socket.close()
			keyboard.unhook_all()

	# YNC Bouyomi mode
	def recv_ync_bouyomi():
		my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		my_socket.bind(local_address)
		my_socket.listen()
		print("")
		print(txt_start_listen)
		try:
			while True:
				try:
					conn, addr = my_socket.accept()
					del addr
					conn.settimeout(5)
					message_bytes = conn.recv(4096)
					if (message_bytes != b""):
						message_text = message_bytes[15:].decode(encoding="utf-8", errors="replace")
						message_text = re.sub(omit_chars, "", message_text)
						if message_text != "":
							if not lsmgr.is_bt:
								my_obj.on_recognition(message_text)
							elif lsmgr.get_state():
								my_obj.on_recognition(message_text)
					conn.close() # require to close connection in each receiving (due to bouyomi-chan spec)
				except socket.timeout:
					continue
				except KeyboardInterrupt:
					raise
				except Exception:
					raise
		except KeyboardInterrupt:
			pass
		except Exception as e:
			print(e)
		finally:
			print(txt_stop_running)
			my_socket.close()
			keyboard.unhook_all()

	# switch by mode
	txt_receive_mode = "RECEIVE MODE: "
	match mode:
		case "udp":
			print("")
			print(txt_receive_mode + "UDP")
			recv_udp()
		case "ync_bouyomi":
			print("")
			print(txt_receive_mode + "YNC Bouyomi")
			recv_ync_bouyomi()
		case _:
			print(f"ERROR: invalid receive mode('{mode}') given!")

if __name__ == "__main__":
    main()
