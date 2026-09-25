class_name SoundSynth
extends RefCounted

# Task #96: every sound in this client is synthesized here at run time --
# no audio file ships with the game.
#
# Evidence: the original has background music (the V03 gameplay video is
# itself titled "【作業用BGM】ザ・コンビニ") and sound effects (a clear/ending
# effect, advanced-evaluation-ending §4; a car horn when parking runs short,
# quick-reference-guide part 1 §2.3). No recording, score or sound list of
# the original was recovered, and its music could not be copied anyway.
# REMAKE_BALANCED_DEFAULT: every melody, chord progression and effect below
# (and which game event plays which effect, vertical_slice.json "sound") is
# this project's own composition, not the original's.

const MIX_RATE := 22050
const NOTE_OFFSETS := {"C": -9, "D": -7, "E": -5, "F": -4, "G": -2, "A": 0, "B": 2}

# Effect ids and what they sound like (all this project's own).
const SFX_IDS := [
    "door_chime",  # ピンポーン: two falling sine tones
    "register",  # ピッ: one short scanner beep
    "purchase",  # チャリーン: coin-like two-note ring
    "place",  # a short low knock
    "select",  # a tiny cursor blip
    "anger",  # a falling buzz
    "settlement",  # a rising four-note arpeggio
    "fanfare",  # a short major fanfare
    "game_over",  # a slow falling minor figure
    "error",  # two low beeps
]


# "A4" -> 440 Hz; sharps as "C#5", flats as "Bb4".
static func note_hz(note: String) -> float:
    var semitones: int = NOTE_OFFSETS[note[0]]
    var octave_text := note.substr(1)
    if octave_text.begins_with("#"):
        semitones += 1
        octave_text = octave_text.substr(1)
    elif octave_text.begins_with("b"):
        semitones -= 1
        octave_text = octave_text.substr(1)
    semitones += (int(octave_text) - 4) * 12
    return 440.0 * pow(2.0, semitones / 12.0)


static func _wave(kind: String, phase: float, rng: RandomNumberGenerator) -> float:
    match kind:
        "square":
            return 1.0 if phase < 0.5 else -1.0
        "pulse":
            return 1.0 if phase < 0.25 else -1.0
        "triangle":
            return 4.0 * absf(phase - 0.5) - 1.0
        "noise":
            return rng.randf_range(-1.0, 1.0)
    return sin(TAU * phase)


# Adds one tone into `out` starting at sample `start`: frequency slides
# linearly from hz to hz_end, volume decays exponentially by `decay` per
# second, with a 4 ms fade in and out so notes do not click.
static func add_tone(
    out: PackedFloat32Array, start: int, seconds: float, hz: float, hz_end: float,
    kind: String, volume: float, decay: float, rng: RandomNumberGenerator
) -> void:
    var count := int(seconds * MIX_RATE)
    var fade := int(0.004 * MIX_RATE)
    var phase := 0.0
    var end := mini(start + count, out.size())
    for i in range(start, end):
        var k := i - start
        var t := float(k) / MIX_RATE
        var hz_now := hz + (hz_end - hz) * float(k) / count
        phase += hz_now / MIX_RATE
        phase -= floorf(phase)
        var envelope := volume * exp(-decay * t)
        if k < fade:
            envelope *= float(k) / fade
        elif count - k < fade:
            envelope *= float(count - k) / fade
        out[i] += _wave(kind, phase, rng) * envelope


static func to_wav(samples: PackedFloat32Array, loop := false) -> AudioStreamWAV:
    var bytes := PackedByteArray()
    bytes.resize(samples.size() * 2)
    for i in samples.size():
        bytes.encode_s16(i * 2, int(clampf(samples[i], -1.0, 1.0) * 32767.0))
    var stream := AudioStreamWAV.new()
    stream.format = AudioStreamWAV.FORMAT_16_BITS
    stream.mix_rate = MIX_RATE
    stream.stereo = false
    stream.data = bytes
    if loop:
        stream.loop_mode = AudioStreamWAV.LOOP_FORWARD
        stream.loop_begin = 0
        stream.loop_end = samples.size()
    return stream


# Each step: [note or Hz, seconds, wave, volume, decay, slide-to note/Hz or null].
static func _render_steps(steps: Array, rng: RandomNumberGenerator) -> PackedFloat32Array:
    var total := 0.0
    for step in steps:
        total += float(step[1])
    var out := PackedFloat32Array()
    out.resize(int((total + 0.05) * MIX_RATE))
    var at := 0
    for step in steps:
        var seconds := float(step[1])
        if step[0] != null:
            var hz := note_hz(step[0]) if step[0] is String else float(step[0])
            var slide = step[5] if step.size() > 5 else null
            var hz_end := hz
            if slide != null:
                hz_end = note_hz(slide) if slide is String else float(slide)
            add_tone(out, at, seconds, hz, hz_end, str(step[2]), float(step[3]), float(step[4]), rng)
        at += int(seconds * MIX_RATE)
    return out


static func sfx_samples(id: String) -> PackedFloat32Array:
    var rng := RandomNumberGenerator.new()
    rng.seed = 7
    match id:
        "door_chime":
            var out := _render_steps([["E6", 0.42, "sine", 0.5, 3.0], ["C6", 0.9, "sine", 0.5, 3.0]], rng)
            # a soft octave overtone on each strike
            add_tone(out, 0, 0.42, note_hz("E7"), note_hz("E7"), "sine", 0.08, 6.0, rng)
            add_tone(out, int(0.42 * MIX_RATE), 0.9, note_hz("C7"), note_hz("C7"), "sine", 0.08, 6.0, rng)
            return out
        "register":
            return _render_steps([[2400.0, 0.09, "square", 0.22, 0.0]], rng)
        "purchase":
            return _render_steps([["B5", 0.07, "square", 0.2, 0.0], ["E6", 0.45, "square", 0.2, 6.0]], rng)
        "place":
            return _render_steps([[320.0, 0.08, "triangle", 0.5, 20.0, 140.0]], rng)
        "select":
            return _render_steps([[1320.0, 0.035, "pulse", 0.15, 0.0]], rng)
        "anger":
            return _render_steps([[420.0, 0.3, "square", 0.2, 2.0, 180.0]], rng)
        "settlement":
            return _render_steps([
                ["C5", 0.08, "pulse", 0.2, 0.0], ["E5", 0.08, "pulse", 0.2, 0.0],
                ["G5", 0.08, "pulse", 0.2, 0.0], ["C6", 0.35, "pulse", 0.2, 5.0],
            ], rng)
        "fanfare":
            return _render_steps([
                ["C5", 0.12, "square", 0.2, 0.0], ["E5", 0.12, "square", 0.2, 0.0],
                ["G5", 0.12, "square", 0.2, 0.0], ["C6", 0.3, "square", 0.2, 0.0],
                ["G5", 0.12, "square", 0.2, 0.0], ["C6", 0.8, "square", 0.2, 2.0],
            ], rng)
        "game_over":
            return _render_steps([
                ["G4", 0.3, "triangle", 0.4, 0.0], ["Eb4", 0.3, "triangle", 0.4, 0.0],
                ["C4", 1.0, "triangle", 0.4, 1.5],
            ], rng)
        "error":
            return _render_steps([
                [196.0, 0.09, "square", 0.2, 0.0], [null, 0.05], [196.0, 0.12, "square", 0.2, 0.0],
            ], rng)
    push_error("unknown sound effect: %s" % id)
    return PackedFloat32Array()


static func sfx(id: String) -> AudioStreamWAV:
    return to_wav(sfx_samples(id))


# One pass through a song (see sound_themes.gd for the format); `bars`
# limits it to the first N bars (for tests). Loops seamlessly.
static func render_song(song: Dictionary, bars := -1) -> PackedFloat32Array:
    var rng := RandomNumberGenerator.new()
    rng.seed = 11
    var step_seconds := 60.0 / float(song["bpm"]) / 2.0
    var bar_count: int = song["lead"].size() if bars < 0 else mini(bars, song["lead"].size())
    var out := PackedFloat32Array()
    out.resize(int(bar_count * 8 * step_seconds * MIX_RATE))
    var lead: Dictionary = song["lead_voice"]
    var bass: Dictionary = song["bass_voice"]
    for bar in bar_count:
        _render_line(out, song["lead"][bar], bar * 8, step_seconds, lead, rng)
        _render_line(out, song["bass"][bar], bar * 8, step_seconds, bass, rng)
        if song.has("drums"):
            var pattern: String = song["drums"]
            for step in 8:
                var at := int((bar * 8 + step) * step_seconds * MIX_RATE)
                match pattern[step]:
                    "k":
                        add_tone(out, at, 0.12, 150.0, 45.0, "sine", 0.45, 18.0, rng)
                    "s":
                        add_tone(out, at, 0.1, 0.0, 0.0, "noise", 0.16, 25.0, rng)
                    "h":
                        add_tone(out, at, 0.03, 0.0, 0.0, "noise", 0.05, 60.0, rng)
    return out


# A bar is 8 eighth-note tokens: a note name starts a note, "-" holds the
# previous one, "." is a rest.
static func _render_line(
    out: PackedFloat32Array, bar_text: String, first_step: int, step_seconds: float,
    voice: Dictionary, rng: RandomNumberGenerator
) -> void:
    var tokens := bar_text.split(" ", false)
    assert(tokens.size() == 8)
    var index := 0
    while index < 8:
        var token: String = tokens[index]
        var length := 1
        while index + length < 8 and tokens[index + length] == "-":
            length += 1
        if token != "." and token != "-":
            var hz := note_hz(token)
            var at := int((first_step + index) * step_seconds * MIX_RATE)
            add_tone(
                out, at, length * step_seconds * 0.92, hz, hz, str(voice["wave"]),
                float(voice["volume"]), float(voice["decay"]), rng
            )
        index += length
