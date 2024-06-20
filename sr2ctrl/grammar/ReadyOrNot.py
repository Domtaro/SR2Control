#
# This file is part of SR2Control tool.
# (c) Copyright 2024 by Domtaro
# Licensed under the LGPL-3.0; see LICENSE.txt file.
#
import os
import sys
import time
import datetime
import re
import copy
import importlib.util

import keyboard
import mouse

# ##################################################
# User params. REQUIRED. define keywords.
# ##################################################
params_path = r"sr2ctrl\grammar\ReadyOrNot_params.py"
# path = os.path.abspath(params_path)
path = os.path.join(os.getcwd(), params_path)
name = os.path.basename(params_path).split(".")[0]
try:
	spec = importlib.util.spec_from_file_location(name, path)
	params = importlib.util.module_from_spec(spec)
	sys.modules[name] = params
	spec.loader.exec_module(params)
except Exception as e:
	print("ERROR: params module import failed!")
	print(e)

# import sr2ctrl.grammar.ReadyOrNot_params as params

# ##################################################
# General class. REQUIRED. must has on_recognition method.
# ##################################################
class SR2C:

	# ##################################################
	# Constructor. REQUIRED.
	# ##################################################
	def __init__(self, test):
		# set test mode
		self._test_mode = test

		# compile re patterns
		self._reobj_yell = {
			"base": re.compile(r"|".join(params.kw_yell["base"])),
		}
		self._reobj_colors = {
			"gold": re.compile(r"|".join(params.kw_colors["gold"])),
			"red": re.compile(r"|".join(params.kw_colors["red"])),
			"blue": re.compile(r"|".join(params.kw_colors["blue"])),
		}
		self._reobj_hold = {
			"base": re.compile(r"|".join(params.kw_hold["base"])),
		}
		self._reobj_trapped = {
			"base": re.compile(r"|".join(params.kw_door_trapped["base"])),
		}
		self._reobj_interact = {
			"base": re.compile(r"|".join(params.kw_interact["base"])),
		}
		self._reobj_execute = {
			"execute": re.compile(r"|".join(params.kw_execute_cancel["execute"])),
			"cancel": re.compile(r"|".join(params.kw_execute_cancel["cancel"])),
		}
		self._reobj_stackup = {
			"base": re.compile(r"|".join(params.kw_stack_sides["base"])),
			"auto": re.compile(r"|".join(params.kw_stack_sides["auto"])),
			"split": re.compile(r"|".join(params.kw_stack_sides["split"])),
			"right": re.compile(r"|".join(params.kw_stack_sides["right"])),
			"left": re.compile(r"|".join(params.kw_stack_sides["left"])),
		}
		self._reobj_breach = {
			"base": re.compile(r"|".join(params.kw_breach_tools["base"])),
			"open": re.compile(r"|".join(params.kw_breach_tools["open"])),
			"kick": re.compile(r"|".join(params.kw_breach_tools["kick"])),
			"shotgun": re.compile(r"|".join(params.kw_breach_tools["shotgun"])),
			"c2": re.compile(r"|".join(params.kw_breach_tools["c2"])),
			"ram": re.compile(r"|".join(params.kw_breach_tools["ram"])),
			"leader": re.compile(r"|".join(params.kw_breach_tools["leader"])),
		}
		self._reobj_grenades = {
			"flash": re.compile(r"|".join(params.kw_grenades["flash"])),
			"stinger": re.compile(r"|".join(params.kw_grenades["stinger"])),
			"gas": re.compile(r"|".join(params.kw_grenades["gas"])),
			"launcher": re.compile(r"|".join(params.kw_grenades["launcher"])),
			"leader": re.compile(r"|".join(params.kw_grenades["leader"])),
		}
		self._reobj_npc = {
			"base": re.compile(r"|".join(params.kw_npc_movements["base"])),
			"here": re.compile(r"|".join(params.kw_npc_movements["here"])),
			"me": re.compile(r"|".join(params.kw_npc_movements["me"])),
			"stop": re.compile(r"|".join(params.kw_npc_movements["stop"])),
			"turn": re.compile(r"|".join(params.kw_npc_movements["turn"])),
			"exit": re.compile(r"|".join(params.kw_npc_movements["exit"])),
		}
		self._reobj_formations = {
			"base": re.compile(r"|".join(params.kw_formations["base"])),
			"single": re.compile(r"|".join(params.kw_formations["single"])),
			"double": re.compile(r"|".join(params.kw_formations["double"])),
			"diamond": re.compile(r"|".join(params.kw_formations["diamond"])),
			"wedge": re.compile(r"|".join(params.kw_formations["wedge"])),
		}
		self._reobj_door = {
			"mirror": re.compile(r"|".join(params.kw_door_options["mirror"])),
			"disarm": re.compile(r"|".join(params.kw_door_options["disarm"])),
			"wedge": re.compile(r"|".join(params.kw_door_options["wedge"])),
		}
		self._reobj_door2 = {
			"base": re.compile(r"|".join(params.kw_door_options2["base"])),
			"cover": re.compile(r"|".join(params.kw_door_options2["cover"])),
			"open": re.compile(r"|".join(params.kw_door_options2["open"])),
			"close": re.compile(r"|".join(params.kw_door_options2["close"])),
		}
		self._reobj_picking = {
			"base": re.compile(r"|".join(params.kw_picking["base"])),
		}
		self._reobj_scan = {
			"pie": re.compile(r"|".join(params.kw_door_scan["pie"])),
			"slide": re.compile(r"|".join(params.kw_door_scan["slide"])),
			"peak": re.compile(r"|".join(params.kw_door_scan["peak"])),
		}
		self._reobj_ground = {
			"move": re.compile(r"|".join(params.kw_ground_options["move"])),
			"cover": re.compile(r"|".join(params.kw_ground_options["cover"])),
			"halt": re.compile(r"|".join(params.kw_ground_options["halt"])),
			"resume": re.compile(r"|".join(params.kw_ground_options["resume"])),
			"search": re.compile(r"|".join(params.kw_ground_options["search"])),
		}
		self._reobj_deployables = {
			"flash": re.compile(r"|".join(params.kw_deployables["flash"])),
			"stinger": re.compile(r"|".join(params.kw_deployables["stinger"])),
			"gas": re.compile(r"|".join(params.kw_deployables["gas"])),
			"chemlight": re.compile(r"|".join(params.kw_deployables["chemlight"])),
			"shield": re.compile(r"|".join(params.kw_deployables["shield"])),
		}
		self._reobj_restrain = {
			"base": re.compile(r"|".join(params.kw_npc_restrain["base"])),
		}
		self._reobj_gadgets = {
			"taser": re.compile(r"|".join(params.kw_team_gadgets["taser"])),
			"spray": re.compile(r"|".join(params.kw_team_gadgets["spray"])),
			"ball": re.compile(r"|".join(params.kw_team_gadgets["ball"])),
			"beanbag": re.compile(r"|".join(params.kw_team_gadgets["beanbag"])),
			"melee": re.compile(r"|".join(params.kw_team_gadgets["melee"])),
		}
		self._reobj_actions = {
			"move": re.compile(r"|".join(params.kw_team_actions["move"])),
			"focus": re.compile(r"|".join(params.kw_team_actions["focus"])),
			"unfocus": re.compile(r"|".join(params.kw_team_actions["unfocus"])),
			"swap": re.compile(r"|".join(params.kw_team_actions["swap"])),
			"search": re.compile(r"|".join(params.kw_team_actions["search"])),
		}
		self._reobj_movements = {
			"there": re.compile(r"|".join(params.kw_team_movements["there"])),
			"back": re.compile(r"|".join(params.kw_team_movements["back"])),
		}
		self._reobj_focus = {
			"here": re.compile(r"|".join(params.kw_team_focus["here"])),
			"me": re.compile(r"|".join(params.kw_team_focus["me"])),
			"door": re.compile(r"|".join(params.kw_team_focus["door"])),
			"target": re.compile(r"|".join(params.kw_team_focus["target"])),
			"unfocus": re.compile(r"|".join(params.kw_team_focus["unfocus"])),
		}
		self._reobj_default = {
			"base": re.compile(r"|".join(params.kw_default_order["base"])),
		}
		# this is not used so far
		# self._reobj_members = {
		# 	"alpha": re.compile(r"|".join(params.kw_team_members["alpha"])),
		# 	"bravo": re.compile(r"|".join(params.kw_team_members["bravo"])),
		# 	"charlie": re.compile(r"|".join(params.kw_team_members["charlie"])),
		# 	"delta": re.compile(r"|".join(params.kw_team_members["delta"])),
		# }

		# mapping of key name in RoN and keyboard module except for case-difference only pattern
		# don't edit!
		self._map_ron_module_keynames = {
			"None": "",
			"LeftMouseButton": "mouse_left",
			"MiddleMouseButton": "mouse_middle",
			"RightMouseButton": "mouse_right",
			"ThumbMouseButton": "mouse_x",
			"ThumbMouseButton2": "mouse_x2",
			"MouseScrollUp": "",	# unknown mapping
			"MouseScrollDown": "",	# unknown mapping
			"Zero": "0",
			"One": "1",
			"Two": "2",
			"Three": "3",
			"Four": "4",
			"Five": "5",
			"Six": "6",
			"Seven": "7",
			"Eight": "8",
			"Nine": "9",
			"Zero": "0",
			"NumPadOne": "num 1",
			"NumPadTwo": "num 2",
			"NumPadThree": "num 3",
			"NumPadFour": "num 4",
			"NumPadFive": "num 5",
			"NumPadSix": "num 6",
			"NumPadSeven": "num 7",
			"NumPadEight": "num 8",
			"NumPadNine": "num 9",
			"Divide": "/",
			"SpaceBar": "space",
			"LeftShift": "left shift",
			"LeftControl": "left ctrl",
			"LeftAlt": "left alt",
			"RightShift": "right shift",
			"RightControl": "right ctrl",
			"RightAlt": "right alt",
		}

		# map of action name Tacspeak to RoN
		# don't edit!
		self._map_sr2c_ron_actionnames = {
			"gold" : "SelectElementGold",
			"blue": "SelectElementBlue",
			"red": "SelectElementRed",
			"cmd_1": "SwatInputKeyOne",
			"cmd_2": "SwatInputKeyTwo",
			"cmd_3": "SwatInputKeyThree",
			"cmd_4": "SwatInputKeyFour",
			"cmd_5": "SwatInputKeyFive",
			"cmd_6": "SwatInputKeySix",
			"cmd_7": "SwatInputKeySeven",
			"cmd_8": "SwatInputKeyEight",
			"cmd_9": "SwatInputKeyNine",
			"cmd_back": "SwatInputKeyBack",
			"cmd_hold": "HoldGoCode",
			"cmd_default": "IssueDefaultCommand",
			"cmd_menu": "OpenSwatCommand",
			"interact_and_yell": "Use",	# attention! this action has special post process, need to be placed earlier than "interact" and "yell"
			"interact": "UseOnly",		# attention! this action has special post process
			"yell": "Yell",				# attention! this action has special post process
		}

		# default key bindings, use when failed to set automatically
		# you can edit
		self._ingame_key_bindings = {
			"gold": "f5",
			"blue": "f6",
			"red": "f7",
			"alpha": "f13",
			"bravo": "f14",
			"charlie": "f15",
			"delta": "f16",
			"cmd_1": "1",
			"cmd_2": "2",
			"cmd_3": "3",
			"cmd_4": "4",
			"cmd_5": "5",
			"cmd_6": "6",
			"cmd_7": "7",
			"cmd_8": "8",
			"cmd_9": "9",
			"cmd_back": "tab",
			"cmd_hold": "left shift",
			"cmd_default": "z",
			"cmd_menu": "mouse_middle",
			"interact": "f",
			"yell": "f",
		}

		# get list of RoN in-game key settings from ini file, and make action-keyname map
		# edit the path if it's not along with your environment
		_inifile_name = os.path.expandvars(r"%LOCALAPPDATA%\ReadyOrNot\Saved\Config\WindowsNoEditor\Input.ini")
		if os.path.isfile(_inifile_name):
			with open(_inifile_name, "rt", encoding="utf-8") as _inifile:
				try:
					_ron_key_bindings = {}
					_key_setting_pattern = re.compile(r'^ActionMappings=\(ActionName="(\w+)".+Key=(\w+)')
					for inifile_line in _inifile:
						_match_result = re.match(_key_setting_pattern, inifile_line)
						if _match_result:
							_ron_action_name = _match_result.group(1)
							_ron_key_name = _match_result.group(2)
							# convert the specific key names to python module key names
							if _ron_key_name in self._map_ron_module_keynames:
								_ron_key_bindings[_ron_action_name] = self._map_ron_module_keynames[_ron_key_name]
							else:
								_ron_key_bindings[_ron_action_name] = _ron_key_name.lower()

					# make ingame_key_bindings automatically
					for tacspeak_action in self._map_sr2c_ron_actionnames.keys():
						_ron_action = self._map_sr2c_ron_actionnames[tacspeak_action]
						if _ron_action in _ron_key_bindings:
							if _ron_action == "Use":	# special case
								self._ingame_key_bindings["interact"] = copy.deepcopy(_ron_key_bindings[_ron_action])
								self._ingame_key_bindings["yell"] = copy.deepcopy(_ron_key_bindings[_ron_action])
							else:
								self._ingame_key_bindings[tacspeak_action] = copy.deepcopy(_ron_key_bindings[_ron_action])
						else:
							continue

				except Exception:
					print(f"Failed to open `{_inifile_name}`. Using default key-bindings")
		else:
			print(f"Invalid File name `{_inifile_name}` was ignored. Using default key-bindings")

		# override key-bindings manually if you need
		self._ingame_key_bindings.update({
			# "gold": "f5",
			# "blue": "f6",
			# "red": "f7",
			"alpha": "f13",
			"bravo": "f14",
			"charlie": "f15",
			"delta": "f16",
			# "cmd_1": "1",
			# "cmd_2": "2",
			# "cmd_3": "3",
			# "cmd_4": "4",
			# "cmd_5": "5",
			# "cmd_6": "6",
			# "cmd_7": "7",
			# "cmd_8": "8",
			# "cmd_9": "9",
			# "cmd_back": "tab",
			# "cmd_hold": "shift",
			# "cmd_default": "z",
			# "cmd_menu": "mouse_middle",
			# "interact": "f",
			# "yell": "f",
		})

		print("")
		print(" ---------------")
		print("Current In-Game Key Bindings:")
		for x in self._ingame_key_bindings.keys():
			print(" " + x + " : " + self._ingame_key_bindings[x])
		print(" ---------------")

		self._txt_label_keys = r"KEYS :"

	# ##################################################
	# Main method. REQUIRED. be called by main program.
	# ##################################################
	def on_recognition(self, text):
		# _txt = re.sub(r"[ ,.，．、。]*", "", text)
		_txt = text
		_order = self._do_check(_txt)
		print("--------------------")
		print(r"TIME :" + datetime.datetime.now().strftime(r"%Y.%m.%d %H:%M:%S"))
		print(r"WORD :" + _txt)		# debug
		print(r"ORDER:" + str(_order))	# debug
		self._do_action(_order)

	# ##################################################
	# Sub method. OPTIONAL. be called by main method.
	# ##################################################
	def _do_check(self, text):
		_txt = text
		_order = {
			"action": "none",
			"option": "none",
			"color": "none",
			"hold": False,
			"trapped": False,
		}

		# yell
		if self._reobj_yell["base"].search(_txt):
			_order["action"] = "yell"
			return _order

		# colors
		if self._reobj_colors["gold"].search(_txt):
			_order["color"] = "gold"
		elif self._reobj_colors["red"].search(_txt):
			_order["color"] = "red"
		elif self._reobj_colors["blue"].search(_txt):
			_order["color"] = "blue"

		# hold
		if self._reobj_hold["base"].search(_txt):
			_order["hold"] = True

		# trapped
		if self._reobj_trapped["base"].search(_txt):
			_order["trapped"] = True

		# trapped
		if self._reobj_interact["base"].search(_txt):
			_order["action"] = "interact"

		# execute
		elif self._reobj_execute["execute"].search(_txt):
			_order["action"] = "execute"
		elif self._reobj_execute["cancel"].search(_txt):
			_order["action"] = "cancel"

		# stack
		elif self._reobj_stackup["base"].search(_txt):
			_order["action"] = "stack"
			if self._reobj_stackup["auto"].search(_txt):
				_order["option"] = "auto"
			elif self._reobj_stackup["split"].search(_txt):
				_order["option"] = "split"
			elif self._reobj_stackup["right"].search(_txt):
				_order["option"] = "right"
			elif self._reobj_stackup["left"].search(_txt):
				_order["option"] = "left"
			else:
				_order["option"] = "auto"

		# breach
		elif self._reobj_breach["base"].search(_txt):
			_order["action"] = "breach"
			_order["breacher"] = "none"
			_order["grenade"] = "none"
			# breach tool
			if self._reobj_breach["leader"].search(_txt):
				_order["breacher"] = "leader"
			elif self._reobj_breach["kick"].search(_txt):
				_order["breacher"] = "kick"
			elif self._reobj_breach["shotgun"].search(_txt):
				_order["breacher"] = "shotgun"
			elif self._reobj_breach["c2"].search(_txt):
				_order["breacher"] = "c2"
			elif self._reobj_breach["ram"].search(_txt):
				_order["breacher"] = "ram"
			elif self._reobj_breach["open"].search(_txt):
				_order["breacher"] = "open"
			# breach grenade
			if self._reobj_grenades["leader"].search(_txt):
				_order["grenade"] = "leader"
			elif self._reobj_grenades["flash"].search(_txt):
				_order["grenade"] = "flash"
			elif self._reobj_grenades["stinger"].search(_txt):
				_order["grenade"] = "stinger"
			elif self._reobj_grenades["gas"].search(_txt):
				_order["grenade"] = "gas"
			elif self._reobj_grenades["launcher"].search(_txt):
				_order["grenade"] = "launcher"

		# npc
		elif self._reobj_npc["base"].search(_txt):
			_order["action"] = "npc"
			if self._reobj_npc["me"].search(_txt):
				_order["option"] = "me"
			elif self._reobj_npc["stop"].search(_txt):
				_order["option"] = "stop"
			elif self._reobj_npc["turn"].search(_txt):
				_order["option"] = "turn"
			elif self._reobj_npc["exit"].search(_txt):
				_order["option"] = "exit"
			elif self._reobj_npc["here"].search(_txt):
				_order["option"] = "here"
			else:
				_order["option"] = "me"

		# formation
		elif self._reobj_formations["base"].search(_txt):
			_order["action"] = "fallin"
			if self._reobj_formations["single"].search(_txt):
				_order["option"] = "single"
			elif self._reobj_formations["double"].search(_txt):
				_order["option"] = "double"
			elif self._reobj_formations["diamond"].search(_txt):
				_order["option"] = "diamond"
			elif self._reobj_formations["wedge"].search(_txt):
				_order["option"] = "wedge"
			else:
				_order["option"] = "single"

		# door
		elif self._reobj_door["wedge"].search(_txt):
			_order["action"] = "door"
			_order["option"] = "wedge"
		elif self._reobj_door["mirror"].search(_txt):
			_order["action"] = "door"
			_order["option"] = "mirror"
		elif self._reobj_door["disarm"].search(_txt):
			_order["action"] = "door"
			_order["option"] = "disarm"

		# door2
		elif self._reobj_door2["base"].search(_txt):
			_order["action"] = "door"
			if self._reobj_door2["cover"].search(_txt):
				_order["option"] = "cover"
			elif self._reobj_door2["open"].search(_txt):
				_order["option"] = "open"
			elif self._reobj_door2["close"].search(_txt):
				_order["option"] = "close"
			else:
				_order["option"] = "cover"

		# picking
		elif self._reobj_picking["base"].search(_txt):
			_order["action"] = "pick"

		# scan
		elif self._reobj_scan["pie"].search(_txt):
			_order["action"] = "scan"
			_order["option"] = "pie"
		elif self._reobj_scan["slide"].search(_txt):
			_order["action"] = "scan"
			_order["option"] = "slide"
		elif self._reobj_scan["peak"].search(_txt):
			_order["action"] = "scan"
			_order["option"] = "peak"

		# ground
		elif self._reobj_ground["move"].search(_txt):
			_order["action"] = "ground"
			_order["option"] = "move"
		elif self._reobj_ground["cover"].search(_txt):
			_order["action"] = "ground"
			_order["option"] = "cover"
		elif self._reobj_ground["halt"].search(_txt):
			_order["action"] = "ground"
			_order["option"] = "halt"
		elif self._reobj_ground["resume"].search(_txt):
			_order["action"] = "ground"
			_order["option"] = "resume"
		elif self._reobj_ground["search"].search(_txt):
			_order["action"] = "ground"
			_order["option"] = "search"

		# deployables
		elif self._reobj_deployables["flash"].search(_txt):
			_order["action"] = "deploy"
			_order["option"] = "flash"
		elif self._reobj_deployables["stinger"].search(_txt):
			_order["action"] = "deploy"
			_order["option"] = "stinger"
		elif self._reobj_deployables["gas"].search(_txt):
			_order["action"] = "deploy"
			_order["option"] = "gas"
		elif self._reobj_deployables["chemlight"].search(_txt):
			_order["action"] = "deploy"
			_order["option"] = "chemlight"
		elif self._reobj_deployables["shield"].search(_txt):
			_order["action"] = "deploy"
			_order["option"] = "shield"

		# restrain
		elif self._reobj_restrain["base"].search(_txt):
			_order["action"] = "restrain"

		# gadget
		elif self._reobj_gadgets["taser"].search(_txt):
			_order["action"] = "gadget"
			_order["option"] = "taser"
		elif self._reobj_gadgets["spray"].search(_txt):
			_order["action"] = "gadget"
			_order["option"] = "spray"
		elif self._reobj_gadgets["ball"].search(_txt):
			_order["action"] = "gadget"
			_order["option"] = "ball"
		elif self._reobj_gadgets["beanbag"].search(_txt):
			_order["action"] = "gadget"
			_order["option"] = "beanbag"
		elif self._reobj_gadgets["melee"].search(_txt):
			_order["action"] = "gadget"
			_order["option"] = "melee"

		# action
		elif self._reobj_actions["move"].search(_txt):
			_order["action"] = "team_action"
			# movement
			if self._reobj_movements["there"].search(_txt):
				_order["option"] = "move_there"
			elif self._reobj_movements["back"].search(_txt):
				_order["option"] = "move_back"
			else:
				_order["option"] = "move_there"
		elif self._reobj_actions["focus"].search(_txt):
			_order["action"] = "team_action"
			# focus
			if self._reobj_focus["here"].search(_txt):
				_order["option"] = "focus_here"
			elif self._reobj_focus["me"].search(_txt):
				_order["option"] = "focus_me"
			elif self._reobj_focus["door"].search(_txt):
				_order["option"] = "focus_door"
			elif self._reobj_focus["target"].search(_txt):
				_order["option"] = "focus_target"
			elif self._reobj_focus["unfocus"].search(_txt):
				_order["option"] = "focus_unfocus"
			else:
				_order["option"] = "focus_me"
		elif self._reobj_actions["unfocus"].search(_txt):
			_order["action"] = "team_action"
			_order["option"] = "unfocus"
		elif self._reobj_actions["swap"].search(_txt):
			_order["action"] = "team_action"
			_order["option"] = "swap"
		elif self._reobj_actions["search"].search(_txt):
			_order["action"] = "team_action"
			_order["option"] = "search"

		# default
		elif self._reobj_default["base"].search(_txt):
			_order["action"] = "default"

		# member
		# it's not used so far.

		return _order

	# ##################################################
	# Sub method. OPTIONAL. be called by main method.
	# ##################################################
	def _do_action(self, order):
		_order = order
		_action = _order["action"]
		_option = _order["option"]
		_color = _order["color"]
		_hold = _order["hold"]
		_trapped = _order["trapped"]
		_command = []

		# --- build key command ---

		# yell
		if _action == "yell":
			_command.append("yell")
			self._push_command(_command)
			return

		# interact
		if _action == "interact":
			_command.append("interact")
			self._push_command(_command)
			return

		# hold
		if _hold:
			_command.append("cmd_hold")

		# color
		if _color != "none":
			_command.append(_color)

		# menu
		_command.append("cmd_menu")

		# execute
		if _action == "execute":
			_command.append("cmd_1")
		elif _action == "cancel":
			_command.append("cmd_2")

		# stack
		elif _action == "stack":
			_command.append("cmd_1")
			match _option:
				case "split":
					_command.append("cmd_1")
				case "left":
					_command.append("cmd_2")
				case "right":
					_command.append("cmd_3")
				case "auto":
					_command.append("cmd_4")
				case _:
					_command.append("cmd_4")

		# breach
		elif _action == "breach":
			if _order["breacher"] == "open":
				_command.append("cmd_2")
			elif _order["breacher"] == "none":
				_command.append("cmd_2")
			else:
				_command.append("cmd_3")
				match _order["breacher"]:
					case "kick":
						_command.append("cmd_1")
					case "shotgun":
						_command.append("cmd_2")
					case "c2":
						_command.append("cmd_3")
					case "ram":
						_command.append("cmd_4")
					case "leader":
						_command.append("cmd_5")
					case _:
						_command.append("cmd_1")
			match _order["grenade"]:
				case "none":
					_command.append("cmd_1")
				case "flash":
					_command.append("cmd_2")
				case "stinger":
					_command.append("cmd_3")
				case "gas":
					_command.append("cmd_4")
				case "launcher":
					_command.append("cmd_5")
				case "leader":
					_command.append("cmd_6")
				case _:
					_command.append("cmd_1")

		# npc
		elif _action == "npc":
			match _option:
				case "here":
					_command.append("cmd_2")
					_command.append("cmd_1")
				case "me":
					_command.append("cmd_2")
					_command.append("cmd_2")
				case "stop":
					_command.append("cmd_2")
					_command.append("cmd_3")
				case "turn":
					_command.append("cmd_4")
				case "exit":
					_command.append("cmd_5")
				case _:
					_command.append("cmd_3")

		# formation
		elif _action == "fallin":
			_command.append("cmd_2")
			match _option:
				case "single":
					_command.append("cmd_1")
				case "double":
					_command.append("cmd_2")
				case "diamond":
					_command.append("cmd_3")
				case "wedge":
					_command.append("cmd_4")
				case _:
					_command.append("cmd_1")

		# door
		elif _action == "door":
			match _option:
				case "mirror":
					_command.append("cmd_5")
				case "disarm":
					_command.append("cmd_6")
				case "wedge":
					if _trapped:
						_command.append("cmd_7")
					else:
						_command.append("cmd_6")
				case "cover":
					if _trapped:
						_command.append("cmd_8")
					else:
						_command.append("cmd_7")
				case "open":
					if _trapped:
						_command.append("cmd_9")
					else:
						_command.append("cmd_8")
				case "close":
					if _trapped:
						_command.append("cmd_9")
					else:
						_command.append("cmd_8")
				case _:
					_command.append("cmd_5")

		# picking
		elif _action == "pick":
			_command.append("cmd_2")

		# scan
		elif _action == "scan":
			match _option:
				case "slide":
					_command.append("cmd_4")
					_command.append("cmd_1")
				case "pie":
					_command.append("cmd_4")
					_command.append("cmd_2")
				case "peak":
					_command.append("cmd_4")
					_command.append("cmd_3")
				case _:
					_command.append("cmd_4")
					_command.append("cmd_2")

		# ground
		elif _action == "ground":
			match _option:
				case "move":
					_command.append("cmd_1")
				case "cover":
					_command.append("cmd_3")
				case "halt":
					_command.append("cmd_4")
				case "resume":
					_command.append("cmd_4")
				case "search":
					_command.append("cmd_6")
				case _:
					_command.append("cmd_1")

		# deployables
		elif _action == "deploy":
			_command.append("cmd_5")
			match _option:
				case "flash":
					_command.append("cmd_1")
				case "stinger":
					_command.append("cmd_2")
				case "gas":
					_command.append("cmd_3")
				case "chemlight":
					_command.append("cmd_4")
				case "shield":
					_command.append("cmd_5")
				case _:
					_command.append("cmd_4")

		# restrain
		elif _action == "restrain":
			_command.append("cmd_1")

		# gadget
		elif _action == "gadget":
			_command.append("cmd_3")
			match _option:
				case "taser":
					_command.append("cmd_1")
				case "spray":
					_command.append("cmd_2")
				case "ball":
					_command.append("cmd_3")
				case "beanbag":
					_command.append("cmd_4")
				case "melee":
					_command.append("cmd_5")

		# team action
		elif _action == "team_action":
			match _option:
				case "move_there":
					_command.append("cmd_1")
					_command.append("cmd_1")
				case "move_back":
					_command.append("cmd_1")
					_command.append("cmd_2")
				case "focus_here":
					_command.append("cmd_2")
					_command.append("cmd_1")
				case "focus_me":
					_command.append("cmd_2")
					_command.append("cmd_2")
				case "focus_door":
					_command.append("cmd_2")
					_command.append("cmd_3")
				case "focus_target":
					_command.append("cmd_2")
					_command.append("cmd_4")
				case "focus_unfocus":
					_command.append("cmd_2")
					_command.append("cmd_5")
				case "swap":
					_command.append("cmd_3")
				case "search":
					_command.append("cmd_4")

		# default
		elif _action == "default":
			_command.append("cmd_default")

		# --- execute to push keys ---
		if _action != "none":
			if self._test_mode:
				print(self._txt_label_keys + str(_command))
			else:
				self._push_command(_command)
		else:
			if _color != "none":
				_command = [_color]
				if self._test_mode:
					print(self._txt_label_keys + str(_command))
				else:
					self._push_command(_command)
			else:
				print(self._txt_label_keys + str(["no action"]))		# debug

	# a part of _do_action method
	def _push_command(self, command):
		_hold_key = ""
		_hold_is_mouse = False
		for cmd in command:
			_key = self._ingame_key_bindings[cmd]
			_is_hold = False
			_is_mouse = False
			if "mouse_" in _key:
				_is_mouse = True
				_key = _key.replace("mouse_", "")
			if cmd == "cmd_hold":
				_is_hold = True
				_hold_key = _key
				if _is_mouse:
					_hold_is_mouse = True
			self._push_key(_key, _is_mouse, _is_hold, up=False)
			time.sleep(0.06)
		if _hold_key != "":
			self._push_key(_hold_key, _hold_is_mouse, True, up=True)
		print(self._txt_label_keys + str(command))	# debug

	# a part of _push_command method
	def _push_key(self, key, is_mouse, is_hold, up):
		if is_mouse:
			if is_hold:
				if up:
					mouse.release(button=key)
				else:
					mouse.press(button=key)
			else:
				mouse.click(button=key)
		else:
			if is_hold:
				if up:
					keyboard.send(hotkey=key, do_press=False, do_release=True)
				else:
					keyboard.send(hotkey=key, do_press=True, do_release=False)
			else:
				keyboard.send(hotkey=key, do_press=True, do_release=True)
