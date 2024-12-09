#
# This file is part of SR2Control tool.
# (c) Copyright 2024 by Domtaro
# Licensed under the LGPL-3.0; see LICENSE.txt file.
#


# ##################################################
# ===== 『Arma 3』用標準grammar =====
# ##################################################
# このファイルは、『Arma 3』向けSR2Control標準grammarです。
# ユーザーの方が、他のゲームなどのために自分でgrammarを作るときの参考になるように、細かい解説を入れながら記述してあります。
# 是非いろいろカスタマイズして使ってみてください。
# また、解説はプログラミング初学者程度を想定したレベル感で書いています。
# ある程度詳しい方は、適度に読み飛ばしてください。


# #######################
# 概説：大まかな仕組み
# #######################
# 自分の「言葉」を「操作」に変換する処理は、大まかに次の段取りで行います。
# 　①喋った言葉（ワード）に対応する命令（コマンド）を特定する
# 　②命令（コマンド）に対応する操作（キー）を特定する
# 　③特定した操作（キー）を実行する

# また、①や②の処理を行うために、"コマンド"と"ワード"、"キー"の対応付け（マッピング）を事前に定義しておく必要もあります。

# これらを踏まえて、このgrammarは大まかに次のような構造になっています。
# 　０．準備（Pythonプログラムとしてある程度お決まりの処理）
# 　１．マッピング定義
# 　２．マッピング処理
# 　３．キー入力実行


# #######################
# ０．準備
# #######################
# ライブラリ／モジュール読み込み（ここはあまり気にしなくてよいです）
import os
import sys
import time
import datetime
import re
import copy
import importlib.util
import keyboard
import mouse


# #######################
# １．マッピング定義
# #######################
# マッピング定義は、コマンドを中心に考えます。
# ・喋って発動させたいコマンドは何か
# ・そのコマンドには、どんな言い回しのパターンがあるか
# ・そのコマンドを実行するためのキーは何か
# 他のゲーム用grammarを作る際にも、まず上記の形で情報を整理するとよいでしょう。

# マッピング定義は行数が嵩張って見づらくなりがちなため、『Ready or Not』用grammarでは別のファイルに切り出して分けています。
# また、「ワードとコマンド」「コマンドとキー」のように複数の変数に分けてもいます。
# ここでは説明のために構成をシンプルにするよう、このファイル内だけで完結させ、変数としても一つにまとめています。

#変数名
arma3_commands = {
	#---ユニット選択---
	#コマンド名
	#プログラム内で識別できれば何でも好きな名前でよい
	"unit_all": { #全隊員選択
		#ワード（言い回し）のリスト
		#最終的には全て"|"で連結した正規表現文字列として扱う。そのため各要素内でも正規表現を使える
		"words": (
			r"全([員隊体]|チーム|ユニット)", #要素内で正規表現を使う場合はraw文字列接頭辞rをつけることを推奨
			#よくある同音異字の認識誤りも入れておくとよい
			#正規表現についてよく分からない場合は、単純に別々の要素として羅列してもよい
			"総員",
			"僧院",
			"掃引",
		),
		#キー名（押す順に並べる）
		"keys": ("com_shift", "space",), #同時押しの場合、先に押すキー名の先頭に"com_"をつける
	},
	"unit_1": { #隊員１を選択
		"words": (
			#全て一つの要素にまとめてもよいが、見やすさ／編集しやすさのためにある程度別の要素に分けるのもよいかもしれない
			r"(わん|ワン)",
			r"[１1](?![０0])", #英数字は念の為全角半角の両方を入れておく。"10"と区別するために後に"0"が続かないことを明示する
			r"[湾椀碗王]",
		),
		"keys": ("f1",),
	},
	#以下、行数を節約して表記
	"unit_2": { #隊員２を選択
		"words": (r"(つー|ツー|つう)", r"[２2]", r"[通痛]",),
		"keys": ("f2",),
	},
	"unit_3": { #隊員３を選択
		"words": ("スリ", r"[３3]", r"[摺刷擦]",),
		"keys": ("f3",),
	},
	"unit_4": { #隊員４を選択
		"words": ("フォ", r"[４4]", "ほう",),
		"keys": ("f4",),
	},
	"unit_5": { #隊員５を選択
		"words": ("(ファイブ|ファイル)", r"[５5]", r"(ハイブ|背部|廃部)", "入る",),
		"keys": ("f5",),
	},
	"unit_6": { #隊員６を選択
		"words": ("シックス", r"[６6]",),
		"keys": ("f6",),
	},
	"unit_7": { #隊員７を選択
		"words": ("セブン", r"[７7]", r"(瀬文|世文)",),
		"keys": ("f7",),
	},
	"unit_8": { #隊員８を選択
		"words": (r"(エイト|エイ|えい)", r"[８8]", r"(栄都|英都|瑛人)",),
		"keys": ("f8",),
	},
	"unit_9": { #隊員９を選択
		"words": (r"(ナイン|ない|無い|内|ナイナー)", r"[９9]",),
		"keys": ("f9",),
	},
	"unit_10": { #隊員１０を選択
		"words": (r"(テン|てん|[xX点天展転典])", r"(１０|10)"),
		"keys": ("f10",),
	},

	#---チーム選択---
	#編制命令と区別できるようにすること
	"select_red": { #レッドチームを選択
		"words": (r"(レッド|レット|赤)(チーム)*?(?!([にへ]*?[割変編]))",),
		"keys": ("com_shift", "f1",),
	},
	"select_green": { #グリーンチームを選択
		"words": (r"[(グリーン)(クリーン)緑](チーム)*?(?!([にへ]*?[割変編]))",),
		"keys": ("com_shift", "f2",),
	},
	"select_bule": { #ブルーチームを選択
		"words": (r"[(ブル)(プル)(振るう)青](チーム)*?(?!([にへ]*?[割変編]))",),
		"keys": ("com_shift", "f3",),
	},
	"select_yellow": { #イエローチームを選択
		"words": (r"[(イエロー)黄](チーム)*?(?!([にへ]*?[割変編]))",),
		"keys": ("com_shift", "f4",),
	},
	"select_white": { #ホワイトチームを選択
		"words": (r"[(ホワイト)白](チーム)*?(?!([にへ]*?[割変編]))",),
		"keys": ("com_shift", "f5",),
	},

	#---チーム割当---
	#選択命令と区別できるようにすること
	"select_red": { #レッドチームに編制
		"words": (r"(レッド|レット|赤)(チーム)*?([にへ]*?[割変編])",),
		"keys": ("com_ctrl", "f1",),
	},
	"select_green": { #グリーンチームに編制
		"words": (r"[(グリーン)(クリーン)緑](チーム)*?([にへ]*?[割変編])",),
		"keys": ("com_ctrl", "f2",),
	},
	"select_bule": { #ブルーチームに編制
		"words": (r"[(ブル)(プル)(振るう)青](チーム)*?([にへ]*?[割変編])",),
		"keys": ("com_ctrl", "f3",),
	},
	"select_yellow": { #イエローチームに編制
		"words": (r"[(イエロー)黄](チーム)*?([にへ]*?[割変編])",),
		"keys": ("com_ctrl", "f4",),
	},
	"select_white": { #ホワイトチームに編制
		"words": (r"[(ホワイト)白](チーム)*?([にへ]*?[割変編])",),
		"keys": ("com_ctrl", "f5",),
	},

	#---メニュー番号---
	#ユニット選択と区別できるようにすること
	"menu_1": { #メニュー１を選択
		"words": (r"(いち|イチ|[一壱１1])(ばん|バン|[番版晩])",),
		"keys": ("1",),
	},
	"menu_2": { #メニュー２を選択
		"words": (r"[にニ二弐２2](ばん|バン|[番版晩])",),
		"keys": ("2",),
	},
	"menu_3": { #メニュー３を選択
		"words": (r"(さん|サン|[三参３3])(ばん|バン|[番版晩])",),
		"keys": ("3",),
	},
	"menu_4": { #メニュー４を選択
		"words": (r"(よん|ヨン|[よヨ四４4夜])(ばん|バン|[番版晩])",),
		"keys": ("4",), 
	},
	"menu_5": { #メニュー５を選択
		"words": (r"[ごゴ５5五御後語](ばん|バン|[番版晩])", "碁盤", "誤(バン|BAN|Ban|ban)",),
		"keys": ("5",), 
	},
	"menu_6": { #メニュー６を選択
		"words": (r"(ろく|ロク|[六６6禄録鹿])(ばん|バン|[番版晩])", ),
		"keys": ("6",), 
	},
	"menu_7": { #メニュー７を選択
		"words": (r"(なな|ナナ|[七７7]|奈々|菜奈|菜々)(ばん|バン|[番版晩])", ),
		"keys": ("7",), 
	},
	"menu_8": { #メニュー８を選択
		"words": (r"(はち|ハチ|[八８8鉢蜂])(ばん|バン|[番版晩])", ),
		"keys": ("8",), 
	},
	"menu_9": { #メニュー９を選択
		"words": (r"(きゅう|キュウ|[九９9急休級旧救宮ＱｑQq])(ばん|バン|[番版晩])", "(吸盤|旧盤)",),
		"keys": ("9",), 
	},
	"menu_10": { #メニュー１０（あるいは０）を選択
		"words": (r"(じゅう|ジュウ|１０|10|ぜろ|ゼロ|ZERO|Zero|zero|[拾十中重獣銃零〇])(ばん|バン|[番版晩])", "(重絆|重盤|重判)",),
		"keys": ("0",), 
	},

	#---チームへの命令---
	"cmd_formup": { #集合
		"words": ("集", "再編",),
		"keys": ("1", "1",),
	},
	"cmd_advance": { #前進
		"words": (""),
		"keys": ("1", "2",),
	},
	"cmd_fallback": { #後退
		"words": (),
		"keys": ("1", "3",),
	},
	"cmd_flankleft": { #左展開
		"words": (),
		"keys": ("1", "4",),
	},
	"cmd_flankright": { #右展開
		"words": (),
		"keys": ("1", "5",),
	},
	"cmd_stop": { #停止
		"words": (),
		"keys": ("1", "6",),
	},
	"cmd_takecover": { #カバー
		"words": (),
		"keys": ("1", "7",),
	},
	"cmd_notarget": { #目標なし
		"words": (),
		"keys": ("2", "1",),
	},
	"cmd_openfire": { #射撃許可
		"words": (),
		"keys": ("3", "1",),
	},
	"cmd_holdfire": { #射撃停止
		"words": (),
		"keys": ("3", "2",),
	},
	"cmd_infantryfire": { #射撃
		"words": (),
		"keys": ("3", "3",),
	},
	"cmd_engage": { #交戦開始
		"words": (),
		"keys": ("3", "4",),
	},
	"cmd_engagefree": { #自由に交戦
		"words": (),
		"keys": ("3", "5",),
	},
	"cmd_disengage": { #交戦中止
		"words": (),
		"keys": ("3", "6",),
	},
	"cmd_scanhorizon": { #周辺警戒
		"words": (),
		"keys": ("3", "7",),
	},
	"cmd_spfire": { #制圧射撃
		"words": (),
		"keys": ("3", "9",),
	},
	"cmd_disembark": { #降車
		"words": (),
		"keys": ("4", "1",),
	},
	"cmd_injured": { #被弾した
		"words": (),
		"keys": ("5", "4",),
	},
	"cmd_reportstatus": { #状況報告
		"words": (),
		"keys": ("5", "5",),
	},
	"cmd_stealth": { #ステルス
		"words": (),
		"keys": ("7", "1",),
	},
	"cmd_combat": { #戦闘
		"words": (),
		"keys": ("7", "2",),
	},
	"cmd_aware": { #警戒
		"words": (),
		"keys": ("7", "3",),
	},
	"cmd_safe": { #警戒解除
		"words": (),
		"keys": ("7", "4",),
	},
	"cmd_standup": { #直立
		"words": (),
		"keys": ("7", "6",),
	},
	"cmd_crouch": { #中腰
		"words": (),
		"keys": ("7", "7",),
	},
	"cmd_prone": { #伏せ
		"words": (),
		"keys": ("7", "8",),
	},
	"cmd_autostance": { #任意の姿勢
		"words": (),
		"keys": ("7", "9",),
	},
	"cmd_form_column": { #一列縦隊
		"words": (),
		"keys": ("8", "1",),
	},
	"cmd_form_staggeredcol": { #千鳥縦隊
		"words": (),
		"keys": ("8", "2",),
	},
	"cmd_form_wedge": { #楔形隊形
		"words": (),
		"keys": ("8", "3",),
	},
	"cmd_form_echelonleft": { #左梯形陣
		"words": (),
		"keys": ("8", "4",),
	},
	"cmd_form_echelonright": { #右梯形陣
		"words": (),
		"keys": ("8", "5",),
	},
	"cmd_form_vee": { #Ｖ字隊形
		"words": (),
		"keys": ("8", "6",),
	},
	"cmd_form_line": { #一列横隊
		"words": (),
		"keys": ("8", "7",),
	},
	"cmd_form_file": { #一列短縦隊
		"words": (),
		"keys": ("8", "8",),
	},
	"cmd_form_diamond": { #菱形隊形
		"words": (),
		"keys": ("8", "9",),
	},

	#---車両への命令---
	#未実装
    # "cmd_vehicle_fire": {
	# 	"words": (),
	# 	"keys": ("com_ctrl", "mouse_left",),
	# },
    # "cmd_vehicle_target": {
	# 	"words": (),
	# 	"keys": ("com_ctrl", "t",),
	# },
    # "cmd_vehicle_switch_weapon": {
	# 	"words": (),
	# 	"keys": ("com_ctrl", "f",),
	# },
    # "cmd_vehicle_manual_fire": {
	# 	"words": (),
	# 	"keys": ("colon",),
	# },
    # "cmd_vehicle_fast": {
	# 	"words": (),
	# 	"keys": ("e",),
	# },
    # "cmd_vehicle_slow": {
	# 	"words": (),
	# 	"keys": ("q",),
	# },

	#---ラジオコマンド---
	"cmd_radio_alpha": { #アルファ
		"words": (),
		"keys": ("0", "0", "1",),
	},
	"cmd_radio_bravo": { #ブラボー
		"words": (),
		"keys": ("0", "0", "2",),
	},
	"cmd_radio_charlie": { #チャーリー
		"words": (),
		"keys": ("0", "0", "3",),
	},
	"cmd_radio_delta": { #デルタ
		"words": (),
		"keys": ("0", "0", "4",),
	},
	"cmd_radio_echo": { #エコー
		"words": (),
		"keys": ("0", "0", "5",),
	},
	"cmd_radio_foxtrot": { #フォックストロット
		"words": (),
		"keys": ("0", "0", "6",),
	},
	"cmd_radio_golf": { #ゴルフ
		"words": (),
		"keys": ("0", "0", "7",),
	},
	"cmd_radio_hotel": { #ホテル
		"words": (),
		"keys": ("0", "0", "8",),
	},
	"cmd_radio_india": { #インディア
		"words": (),
		"keys": ("0", "0", "9",),
	},
	"cmd_radio_juliet": { #ジュリエット
		"words": (),
		"keys": ("0", "0", "0",),
	},
}




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
