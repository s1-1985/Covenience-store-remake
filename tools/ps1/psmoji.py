# Task #127: PS1 disc font table. Glyph order read off PSMOJI0/1.TIM
# (assets/raw/ps1_disc_analysis_v1/images/TIM0_PSMOJI0.png, TIM0_PSMOJI1.png).
# Glyph table of PSMOJI0/1.TIM (12x16 cells, 21 per row, 16 rows per page),
# transcribed by eye from the decoded font sheets.
ROWS0 = [
    "0123456789ABCDEFGHIJK",
    "LMNOPQRSTUVWXYZ¥%。、!/",
    ["~", ":", ",", "?", "ー", "・", "[", "]", "{L1}", "{R1}", "◁", "▷", "▽", "△", "(", ")", "「", "」", "+", "　", "　"],
    "あいうえおかきくけこさしすせそたちつてとな",
    "にぬねのはひふへほまみむめもやゆよらりるれ",
    "ろわをんがぎぐげござじずぜぞだぢづでどばび",
    "ぶべぼぱぴぷぺぽぁぃぅぇぉっゃゅょアイウエ",
    "オカキクケコサシスセソタチツテトナニヌネノ",
    "ハヒフヘホマミムメモヤユヨラリルレロワヲン",
    "ガギグゲゴザジズゼゾダヂヅデドバビブベボパ",
    "ピプペポァィゥェォッャュョ極上中初級年目月",
    "日選択都庁誘致店舗建設評価専用晴雨曇雪大回",
    "転名入力記号文字削除完了望効果音次報告終本",
    "位置決定縮小販売許可申請酒類薬扱金額足残資",
    "産内装読込自分作床員控室備機保温商冷蔵凍動",
    "観葉植物噴水駐車場現飲料弁当野菜肉魚電気製",
]
ROWS1 = [
    "菓子房具調味下着宅急便書食紙存営業方針時間",
    "格全体個別採異歳経験学歴敏捷性社交長教育補",
    "充警掃接客他費欲所持買人口詳細不明査収先新",
    "開変更何支総合顧独占率万億計宣伝聞広飛行船",
    "止比番施消防署族館遊園地住会念運幼稚祭校高",
    "門公却激無限移替楽火災発生強盗越引混雑山信",
    "夫的丈二介杉三郎森之福孝仁田夜沢達也菅原聖",
    "池秀哲朝宗司西男女透奥平康光佐々木雄秋四南",
    "洋竹百吉有紀宮千里涼浜夕花咲江忍町市川智恵",
    "村真知賞誌良清潔援助甲斐季節区役倒撤退解雇",
    "怒土道路線標届要求能単活円乏供連駅椅松杖富",
    "永幸谷今京丸昭伸愛橋募集応者前雷快台風副購",
    "品配華屋空銭湯児端働納常棚扉余裕展寄付害取",
    "値段安近切最賃焼被以渉一在敵海爺婆黒臨休件",
    "規階成済改築続始録管理画面必源容量準型出度",
    ["★", "☆", "複", "法", "促", "直", "使", "数", "均", "利", "益", "外", "累", "積", "来", "―", "注", "維", "秒", "", ""],
]
TABLE = []
for rows in (ROWS0, ROWS1):
    for row in rows:
        cells = list(row)
        assert len(cells) == 21, row
        TABLE.extend(cells)
assert len(TABLE) == 672


def decode(codes):
    out = []
    for code in codes:
        value = int(code, 16) if isinstance(code, str) else code
        if value == 0x40FF:
            break
        if value >= 0x4000:
            out.append("{%04X}" % value)
        elif value < len(TABLE) and TABLE[value]:
            out.append(TABLE[value])
        else:
            out.append("{?%X}" % value)
    return "".join(out)
