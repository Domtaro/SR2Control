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

def main(grammar_path, port, mode, test):
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
			print("ERROR: invalid mode given! (-m option)")

if __name__ == "__main__":
    main()
