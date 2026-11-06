extends Node

# Original XA/SEQ assets are rendered offline. No disc/CPU at runtime.
# CONFIRMED_BINARY: ProgramAudio carries original settings and ID boundaries.
# REMAKE_BALANCED_DEFAULT: legacy event aliases below remain synthesized until
# each original producer is connected; offline SoundFont ADSR/reverb differs
# from the physical SPU (source_audio.json records the renderer boundaries).

const ProgramAudio := preload("res://scripts/domain/program_audio.gd")
const SoundSynthScript := preload("res://scripts/audio/sound_synth.gd")
const SoundThemesScript := preload("res://scripts/audio/sound_themes.gd")
const SETTINGS_PATH := "user://settings.cfg"
const SFX_VOICES := 4
const BGM_VOLUME_DB := -10.0
const SFX_VOLUME_DB := -6.0

signal source_settings_changed
signal source_voice_finished

var source_settings_bits := 0
var source_catalog: Dictionary = {}
var source_history: Array[int] = []
var source_bgm_id := -1
var _source_tracks: Array[AudioStreamPlayer] = []
var _source_voice: AudioStreamPlayer
var _source_remaining := 0.0
var _source_voice_id := -1
var enabled := true
var current_theme := ""
# Every effect asked for, newest last (the smoke tests read it).
var sfx_history: Array[String] = []
var _bgm_player: AudioStreamPlayer
var _sfx_players: Array[AudioStreamPlayer] = []
var _sfx_cache: Dictionary = {}
var _theme_cache: Dictionary = {}
var _rendering: Dictionary = {}


func _ready() -> void:
    process_mode = Node.PROCESS_MODE_ALWAYS
    _bgm_player = AudioStreamPlayer.new()
    _bgm_player.volume_db = BGM_VOLUME_DB
    add_child(_bgm_player)
    for i in SFX_VOICES:
        var player := AudioStreamPlayer.new()
        player.volume_db = SFX_VOLUME_DB
        add_child(player)
        _sfx_players.append(player)
    for i in 28:
        var track := AudioStreamPlayer.new()
        add_child(track)
        _source_tracks.append(track)
    _source_voice = AudioStreamPlayer.new()
    add_child(_source_voice)
    _source_voice.finished.connect(_source_finished)
    source_catalog = JSON.parse_string(FileAccess.get_file_as_string("res://data/source_audio.json"))
    var settings := ConfigFile.new()
    if settings.load(SETTINGS_PATH) == OK:
        enabled = bool(settings.get_value("audio", "enabled", true))
        source_settings_bits = int(settings.get_value("audio", "source_settings_bits", 0)) & 0x303


# The headless test runs skip the actual music rendering (it takes a few
# seconds of CPU and nobody hears it); they still see current_theme.
func _renders_music() -> bool:
    return DisplayServer.get_name() != "headless"


func play_sfx(id: String) -> void:
    sfx_history.append(id)
    if sfx_history.size() > 64:
        sfx_history.remove_at(0)
    if not enabled:
        return
    if id == "select":
        play_source(-1)
        play_source(1) # 80065000 confirmation wrapper.
        return
    if int(source_settings()["se_enabled"]) != 1:
        return
    if not _sfx_cache.has(id):
        _sfx_cache[id] = SoundSynthScript.sfx(id)
    var player := _sfx_players[0]
    for candidate in _sfx_players:
        if not candidate.playing:
            player = candidate
            break
    player.stream = _sfx_cache[id]
    player.play()


func play_theme(theme_id: String) -> void:
    if theme_id == current_theme:
        return
    current_theme = theme_id
    _bgm_player.stop()
    if source_catalog.has("bgm"):
        play_source_bgm(int(source_settings()["bgm_id"]))
        return
    if not enabled or not _renders_music():
        return
    if _theme_cache.has(theme_id):
        _start_theme(theme_id)
    elif not _rendering.has(theme_id):
        _rendering[theme_id] = WorkerThreadPool.add_task(_render_theme.bind(theme_id))


func stop_music() -> void:
    source_bgm_id = -1
    current_theme = ""
    _bgm_player.stop()


# A render still running when the game closes is waited for, so the
# worker never outlives the scripts it runs.
func _exit_tree() -> void:
    for task_id in _rendering.values():
        WorkerThreadPool.wait_for_task_completion(task_id)
    for player in _sfx_players + _source_tracks + [_bgm_player, _source_voice]:
        if is_instance_valid(player):
            player.stop()
            player.stream = null
    _sfx_cache.clear()
    _theme_cache.clear()


func _render_theme(theme_id: String) -> void:
    var samples := SoundSynthScript.render_song(SoundThemesScript.theme(theme_id))
    var stream := SoundSynthScript.to_wav(samples, true)
    call_deferred("_theme_rendered", theme_id, stream)


func _theme_rendered(theme_id: String, stream: AudioStreamWAV) -> void:
    WorkerThreadPool.wait_for_task_completion(_rendering[theme_id])
    _rendering.erase(theme_id)
    _theme_cache[theme_id] = stream
    if theme_id == current_theme and enabled:
        _start_theme(theme_id)


func _start_theme(theme_id: String) -> void:
    _bgm_player.stream = _theme_cache[theme_id]
    _bgm_player.play()


func set_enabled(on: bool) -> void:
    enabled = on
    var settings := ConfigFile.new()
    settings.load(SETTINGS_PATH)
    settings.set_value("audio", "enabled", on)
    settings.save(SETTINGS_PATH)
    if not on:
        _bgm_player.stop()
        stop_source_voice()
        for player in _sfx_players + _source_tracks:
            player.stop()
    else:
        var theme_id := current_theme
        current_theme = ""
        if not theme_id.is_empty():
            play_theme(theme_id)


func _process(delta: float) -> void:
    # Dummy audio has no physical playback clock. Keep the decoded source
    # duration for automated/headless UI execution; real audio uses finished.
    if not _renders_music() and _source_remaining > 0.0:
        _source_remaining = maxf(0.0, _source_remaining - delta)
        if _source_remaining == 0.0:
            _source_finished()


func source_voice_active() -> bool:
    return _source_remaining > 0.0 if not _renders_music() else _source_voice.playing


func _source_finished() -> void:
    _source_remaining = 0.0
    _source_voice_id = -1
    source_voice_finished.emit()


func stop_source_voice() -> void:
    _source_voice.stop()
    _source_remaining = 0.0
    _source_voice_id = -1


func play_source(identifier: int, guard: int = -999) -> bool:
    source_history.append(identifier)
    if source_history.size() > 64:
        source_history.pop_front()
    var plan: Dictionary = ProgramAudio.dispatch(identifier, source_bgm_id if guard == -999 else guard, int(source_settings()["se_enabled"]))
    if plan["kind"] == "stop":
        for i in 16:
            _source_tracks[i].stop()
        stop_source_voice()
        return true
    if not enabled or plan["kind"] in ["none", "invalid"]:
        return false
    var kind: String = plan["kind"]
    var index: int = plan["index"]
    if not source_catalog.has(kind) or index < 0 or index >= source_catalog[kind].size():
        return false # never synthesize an invented substitute for missing ID130.
    var entry: Dictionary = source_catalog[kind][index]
    var stream := load("res://assets/audio/source/" + str(entry["file"])) as AudioStream
    if stream == null:
        return false
    if kind == "xa":
        stop_source_voice()
        _source_voice.stream = stream
        _source_voice_id = identifier
        _source_remaining = float(entry["duration"])
        if _renders_music():
            _source_voice.play()
    else:
        var player := _source_tracks[index + (16 if kind == "vos" else 0)]
        player.stream = stream
        if _renders_music():
            player.play()
    return true


func source_settings() -> Dictionary:
    return ProgramAudio.settings(source_settings_bits)


func set_source_settings(bits: int) -> void:
    # The three original controls generate highbyte0..2 and lowbits0..3.
    source_settings_bits = bits & 0x303
    var settings := ConfigFile.new()
    settings.load(SETTINGS_PATH)
    settings.set_value("audio", "source_settings_bits", source_settings_bits)
    settings.save(SETTINGS_PATH)
    if current_theme in ["town", "store"]:
        play_source_bgm(int(source_settings()["bgm_id"]))
    source_settings_changed.emit()


func play_source_bgm(index: int, loop: bool = true) -> bool:
    if index == source_bgm_id and (_bgm_player.playing or not _renders_music()):
        return index >= 0
    source_bgm_id = index
    _bgm_player.stop()
    if index < 0 or not enabled or not source_catalog.has("bgm") or index >= source_catalog["bgm"].size():
        return false
    var stream := load("res://assets/audio/source/" + str(source_catalog["bgm"][index]["file"])) as AudioStreamOggVorbis
    if stream == null:
        return false
    stream.loop = loop
    _bgm_player.stream = stream
    if _renders_music():
        _bgm_player.play()
    return true
