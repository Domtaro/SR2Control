#
# This file is part of SR2Control tool.
# (c) Copyright 2024 by Domtaro
# Licensed under the LGPL-3.0; see LICENSE.txt file.
#
# ===============================
#     キーワード設定ファイル
# ===============================
# コマンドを発動するためのキーワードを好きに設定できます。
# 以下に設定サンプルを用いて、設定時の考え方を説明します。
# （このサンプル変数kw_sampleは実際には参照されないので、不要になったら削除してもよいです）

# *** ↓ サンプルここから ↓ ***
kw_sample = {		# 大まかにコマンドの種類ごとのグループに変数が分かれています。
					# この変数名を変えたり、内容を分けて新しく作ったりはできません。（grammar側も一緒に変えるなら可）

	"base": (		# 一つの「言葉」ごとに、その言い換えのバリエーションを定義します。
					# この「言葉」の名前を変えたり、追加削除したりすることはできません。（grammar側も一緒に変えるなら可）

					# "base"は特別な言葉で、主に他のコマンドとの区別のために使います。
					# →以下、"ベースワード"と呼びます。
					# 例：ドアの突破手段の「開けろ」と、ただ開くだけの「開けろ」は、
					# 　　それぞれ"ベースワード"にある言葉（「突入」と「ドア」など）を使うことで区別できます。
					# "ベースワード"が無いコマンドも有ります。（例えば「ミラー」など、その言葉だけでコマンドまで特定できるもの）
 
		"サンプル",	# 「言葉」の言い換えのパターンを並べます。
		"テスト",	# なるべく他の「言葉」やコマンドで使われているワードと被らないことが望ましいです。
		"試験",
		"ピストル", # "オプションワード"のワードを"ベースワード"にも入れることで、"ベースワード"を省略するような言い方もできます。
					# （ただし、他のコマンドの"ベースワード"と区別できるワードである必要があります。）
	),
	"rifle": (		# "ベースワード"以外の「言葉」を、"オプションワード"と呼びます。
		"ライフル",	# "アサルトライフル" と "バトルライフル" のような似た言葉は、複数並べてもよいですが、
		"小銃",		# 例えば"ライフル"と書くだけでも両方にヒットさせられます。
		"長物",		# ただし"スナイパーライフル"など、他にヒットさせたくない言葉もある場合は注意が必要です。
	),
	"handgun": (
		"ハンドガン",
		"ピストル",
		"拳銃",
		"チャカ",
		"茶か",		# ワードによっては、同音異字の言葉として認識されてしまうこともよくあります。
					# そういった場合は、よくある誤認識も一緒に登録してしまうことをオススメします。
	),
	"prone":(
		"伏",		# 例えば "伏せろ" "伏せて" "伏して" のように、活用や送り仮名のパターンが多いワードは、
					# 漢字の部分だけ登録すれば幅広くヒットできます。
					# ただし、短くしすぎると他のワードと被りやすくなるので注意が必要です。
		r"伏[しすせ]",	# また、ここでは正規表現も使えます。
						# （「言葉」に対応するワードたちは、後の処理でさらに"|"で連結されます。）
		"匍匐",
		"ホフク",
		"プローン",	# 各コマンド内や「言葉」内の、最後の要素の後のカンマを削除する必要はありません。（Pythonの仕様）
	),
	"no_use_word": (
		"，",		# ある「言葉」にどんなワードもヒットしてほしくない場合、
					# （例えば、「"interact"は使わないので、どんな言葉にも反応してほしくない」という場合など）
					# その「言葉」のバリエーションを「絶対ヒットしないであろうワードのみ」にしてください。
					# （例えば記号の羅列や、意味のない外国語の文字列など）
					# 特に 句読点"、。" や カンマ"，," は、認識結果テキストから除外しているためオススメです。
					# ※ 空文字"" は逆にあらゆる言葉にヒットしてしまうため、使わないでください。
		# "不要ワード",	# 使わない言葉は、行頭に"#"を付けることでコメントアウトできます。
	),
}
# --- その他のTips ---
# このファイルにあるキーワードたちは、上から「チェックされる順」に並べてあります。
# 複数のコマンドやオプションで同じワードを使いたい場合に参考にしてください。
# （例えば"execute"の「行け行け」と"default"の「行け」は、"execute"が先にチェックされることで両者を区別できています。）
# ※ 実際のチェック順序は「ReadyOrNot.py」に定義されています。このファイル内で並べ替えても処理には反映されません。
# このファイル自体の名前や置き場所を変えたい場合は、「ReadyOrNot.py」も合わせて編集する必要があります。
# *** ↑ サンプルここまで ↑ ***


# **********************************
# *** ↓ 実際の設定値ここから ↓ ***
# **********************************

# エール（手を上げろ！などの警告、シャウト）
kw_yell = {
	"base": (
		"動くな",
		"警察",
		"LSPD",
		"lspリーダー",
		"武器",
		"捨",
		"跪",
		"手",
		"伏",
		"附",
	),
}

# チームカラー選択
kw_colors = {
	"gold": (
		"ゴールド",
		"全員",
		"全チーム",
	),
	"red": (
		"レッド",
		"ベッド",
		"ベット",
		"別途",
	),
	"blue": (
		"ブル",
	),
}

# コマンドのホールド実行のホールド指示
kw_hold = {
	"base": (
		"合図",
		"会津",
	),
}

# トラップ付きドアへの指示は番号がずれるのでその区別用
kw_door_trapped = {
	"base": (
		"罠",
		"トラップ",
	),
}

# インタラクト（無線報告、手錠、証拠回収など）
kw_interact = {
	"base": (
		"作戦",
		"本部",
		"TOC",
		"特区",
		"HQ",
		"報告",
		"突入班",		# ブリーチングと区別できるように
		"突入犯",
		"エントリー",
		"エレメント",
		"本部",
		# （！）長押しインタラクションは未対応（！）
		# "回収",
		# "改修",
		# "じっと",
		# "大人しく",
		# "おとなしく",
		# "拘束する",		# メンバーへの逮捕指示と区別できるように
		# "高速する",
		# "光速する",
		# "校則する",
		# "逮捕する",
		# "確保する",
	),
}

# コマンドのホールド実行の実行指示
kw_execute_cancel = {
	"execute": (		# デフォルト命令と競合注意
		"ゴーゴー",		# "ゴー"だと"ゴールド"と被る
		"55",
		"行け行け",
		"いけいけ",
		"行けいけ",
		"いけ行け",
		"イケイケ",
		"実行",
		"やれ",
	),
	"cancel": (
		"中止",
		"やめ",
		"止め",
		"キャンセル",
	),
}

# スタックアップ指示
kw_stack_sides = {
	"base": (
		"スタック",
		"配置",
		"位置",
		"展開",
		"つけ",
		"右",		# 単に「右だ」でも認識できるように
		"左",		# 単に「左だ」でも認識できるように
		"左右",		# 単に「左右」でも認識できるように
		"白湯",
		"さゆ",
		"両",
	),
	"auto": (
		"任せ",
		"まかせ",
	),
	"split": (
		"左右",
		"白湯",
		"さゆ",
		"両",
	),
	"right": (
		"右",
		"みぎ",
	),
	"left": (
		"左",
		"ひだり",
	),
}

# ブリーチング、突破方法の指示
kw_breach_tools = {
	"base": (			# ただの「開けろ」と区別するために必要
		"突破",
		"突入",
		"侵入",
		"進入",
		"潜入",
		"制圧",
		"クリア",
		r"入[りるれろ(って)]",
		r"進[みむめん]",
	),
	"leader": (			# グレネードの"リーダー"と区別が必要
		"俺が",
		"オレが",
	),
	"kick": (
		"蹴",
		"キック",
	),
	"shotgun": (
		"ショットガン",
		"マスターキー",
		"散弾",
	),
	"c2": (
		"c2",
		"C2",
		"シーツ",
		"爆",
	),
	"ram": (
		"ラム",
		"らむ",
		"破城槌",
	),
	"open": (
		"開",
		"静",
	),
}

# ブリーチング用グレネードの指示
kw_grenades = {
	"leader": (			# ブリーチ方法の"リーダー"と区別が必要
		"俺に",
		"オレに",
		"俺の",
		"オレの",
	),
	"flash": (
		"フラッシュ",
		"バン",
		"BAN",
		"閃光",
	),
	"stinger": (
		"スティンガー",
		"ゴム",
	),
	"gas": (
		"ガス",
		"催涙",
	),
	"launcher": (
		"ランチャー",
	),
}

# 降伏NPCへの指示
kw_npc_movements = {
	"base": (		# チームメンバーへの指示と区別するために必要
		"おい",
		"お前",
		"おまえ",
		"君",
		"きみ",
		"あんた",
		"そこで",
		"その場",
		"ゆっくり",
	),
	"me": (
		"ここ",
		"こっち",
	),
	"stop": (
		"止",
	),
	"turn": (
		"回",
		"まわれ",
		"向",
		"振",
	),
	"exit": (
		"出",
		"逃",
		"脱",
	),
	"here": (
		"そこ",
		"そっち",
	),
}

# 集合、隊形指示
kw_formations = {
	"base": (		# ドアウェッジと区別するために必要
		"隊形",
		"体型",
		"体形",
		"隊列",
		"フォーメーション",
		"フォーム",
		"集まれ",
		"あつまれ",
		"集合",
		"集結",
		"終結",
		"付いて",
		"ついて",
		"編成",
	),
	"single": (
		"シングル",
		"一列",
		"1列",
	),
	"double": (
		"ダブル",
		"二列",
		"2列",
	),
	"diamond": (
		"ダイア",
		"ダイヤ",
	),
	"wedge": (
		"ウェッジ",
		"楔",
	),
}

# ドアへの指示１（"base"が不要なもの）
kw_door_options = {
	"wedge": (
		"ウェッジ",
		"ジャマ",
		"邪魔",
		"ブロック",
		"封鎖",
		"閉鎖",
		"塞",
	),
	"mirror": (
		"ミラー",
		"ワンド",
	),
	"disarm": (
		"解除",
		"外",
	),
}

# ドアへの指示２（"base"が必要なもの）
kw_door_options2 = {
	"base": (		# 地面への「カバー」、ブリーチングの「開け」と区別するために必要
		"ドア",
		"扉",
		"通路",
		"部屋",
		"胴",
		"堂",
		"銅",
	),
	"cover": (
		"カバー",
		"援護",
	),
	"open": (
		"開け",
		"開く",
		"あけ",
		"ひら",
	),
	"close": (
		"閉",
		"とじ",
		"しめ",
	),
}

# ピッキング指示
kw_picking = {
	"base": (
		"ピック",
		"ピッキング",
		"開錠",
		"解錠",
	),
}

# ドアのスキャン指示
kw_door_scan = {
	"pie": (
		"パイ",
		"カッティング",
		"スキャン",
	),
	"slide": (
		"スライド",
	),
	"peak": (
		"ピーク",
		"覗",
	),
}

# 地面への指示
kw_ground_options = {
	"move": (
		"移動",
	),
	"cover": (
		"見",
		"視",
		"カバー",
	),
	"halt": (
		"待",
		"止",
	),
	"resume": (
		"再開",
	),
	"search": (
		"捜",
		"探",
	),
}

# その場で展開する系の指示
kw_deployables = {
	"flash": (
		"フラッシュ",
		"バン",
		"閃光",
	),
	"stinger": (
		"スティンガー",
		"ゴム",
	),
	"gas": (
		"ガス",
		"催涙",
	),
	"chemlight": (
		"ライト",
		"スティック",
	),
	"shield": (
		"盾",
		"シールド",
	),
}

# 降伏NPCの逮捕指示
kw_npc_restrain = {
	"base": (
		"逮捕",
		"拘束",
		"高速",
		"光速",
		"校則",
		"確保",
		"縛",
		"手錠",
		"タイ",
	),
}

# 反抗的なNPCへの制圧指示
kw_team_gadgets = {
	"taser": (
		"テーザー",
		"電",
	),
	"spray": (
		"スプレー",
	),
	"ball": (
		"ボール",
	),
	"beanbag": (
		"ビーン",
		"バッグ",
	),
	"melee": (
		"メレー",
		"殴",
	),
}

# 隊員個別に視点を合わせて行う指示
# ※特性上、機能できないものもある
kw_team_actions = {
	"move": (
		"動",
	),
	"focus": (
		"見",
		"視",
	),
	"unfocus": (
		"見るな",
		"視るな",
		"止め",
		"やめ",
	),
	"swap": (
		"代",
		"替",
		"変",
	),
	"search": (
		"捜",
		"探",
	),
}

# 隊員個別指示の"move"派生
kw_team_movements = {
	"there": (
		"行",
	),
	"back": (
		"戻",
	),
}

# 隊員個別指示の"focus"派生
kw_team_focus = {
	"here": (
		"ここ",
		"そこ",
	),
	"me": (
		"俺",
		"オレ",
		"こっち",
	),
	"door": (
		"ドア",
		"扉",
	),
	"target": (
		"ターゲット",
		"目標",
		"あいつ",
		"奴",
		"やつ",
		"ヤツ",
	),
	"unfocus": (
		"見るな",
		"視るな",
		"止め",
		"やめ",
	),
}

# デフォルト命令（標準でZキー）
kw_default_order = {
	"base": (			# ホールド実行、集合命令と競合注意
		"デフォルト",
		"対応",
		"行け",
		"いけ",
		"来い",
		"恋",
		"故意",
		"あれ",
		"それ",
	),
}

# 隊員個人選択（ゲーム側で未実装。現状未使用）
kw_team_members = {
	"alpha": (
		"アルファ",
	),
	"bravo": (
		"ブラボー",
	),
	"charlie": (
		"チャーリー",
	),
	"delta": (
		"デルタ",
	),
}