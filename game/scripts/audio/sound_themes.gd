class_name SoundThemes
extends RefCounted

# Task #96: the two background tunes. REMAKE_BALANCED_DEFAULT: both are this
# project's own compositions (see sound_synth.gd's header for why nothing of
# the original's music is reproduced). Each bar is 8 eighth notes; see
# SoundSynth._render_line for the token format.

# While the store is open: a bright shop tune, C major, 132 bpm, 16 bars.
const STORE := {
    "bpm": 132,
    "lead_voice": {"wave": "pulse", "volume": 0.12, "decay": 1.2},
    "bass_voice": {"wave": "triangle", "volume": 0.3, "decay": 0.5},
    "drums": "khshkhsh",
    "lead": [
        "E5 . G5 . C6 - B5 A5",
        "A5 - E5 - C5 - E5 .",
        "F5 . A5 . C6 - A5 F5",
        "G5 - - - D5 - . .",
        "E5 . G5 . C6 - D6 E6",
        "C6 - A5 - E5 - A5 .",
        "D5 F5 A5 D6 C6 - A5 F5",
        "G5 - B5 - D6 - . .",
        "A5 - C6 - A5 G5 F5 .",
        "G5 - B5 - D6 - B5 .",
        "E5 G5 B5 E6 D6 - B5 G5",
        "A5 - - - E5 - . .",
        "F5 . A5 . C6 . F6 -",
        "E6 - D6 - B5 - G5 .",
        "C6 - G5 - E5 - G5 -",
        "C6 - - - . . . .",
    ],
    "bass": [
        "C3 C3 G3 C3 C3 C3 G3 C3",
        "A2 A2 E3 A2 A2 A2 E3 A2",
        "F2 F2 C3 F2 F2 F2 C3 F2",
        "G2 G2 D3 G2 G2 G2 D3 G2",
        "C3 C3 G3 C3 C3 C3 G3 C3",
        "A2 A2 E3 A2 A2 A2 E3 A2",
        "D3 D3 A3 D3 D3 D3 A3 D3",
        "G2 G2 D3 G2 G2 G2 D3 G2",
        "F2 F2 C3 F2 F2 F2 C3 F2",
        "G2 G2 D3 G2 G2 G2 D3 G2",
        "E3 E3 B3 E3 E3 E3 B3 E3",
        "A2 A2 E3 A2 A2 A2 E3 A2",
        "F2 F2 C3 F2 F2 F2 C3 F2",
        "G2 G2 D3 G2 G2 G2 D3 G2",
        "C3 C3 G3 C3 C3 C3 G3 C3",
        "C3 C3 G3 C3 G2 - . .",
    ],
}

# Title screen and choosing the site on the town map: a calm tune, 100 bpm,
# 8 bars.
const TOWN := {
    "bpm": 100,
    "lead_voice": {"wave": "triangle", "volume": 0.3, "decay": 0.8},
    "bass_voice": {"wave": "sine", "volume": 0.3, "decay": 0.6},
    "lead": [
        "A4 - - C5 E5 - - .",
        "F5 - E5 - C5 - - .",
        "G4 - - C5 E5 - D5 C5",
        "D5 - - - - - . .",
        "A4 - - C5 E5 - A5 -",
        "G5 - F5 - E5 - C5 -",
        "E5 - D5 - C5 - G4 -",
        "C5 - - - - - . .",
    ],
    "bass": [
        "A2 - - - E3 - - -",
        "F2 - - - C3 - - -",
        "C3 - - - G2 - - -",
        "G2 - - - D3 - - -",
        "A2 - - - E3 - - -",
        "F2 - - - C3 - - -",
        "C3 - - - G2 - - -",
        "G2 - - - G2 - . .",
    ],
}


static func theme(theme_id: String) -> Dictionary:
    return STORE if theme_id == "store" else TOWN
