extends Node

# Task #96: plays the synthesized music and effects (autoload
# "SoundManager"). Everything it plays comes from SoundSynth/SoundThemes --
# REMAKE_BALANCED_DEFAULT, this project's own sounds (see sound_synth.gd).
# Music is rendered once per tune on a worker thread, so starting a scene
# never waits for it. The on/off choice is kept in user://settings.cfg.

const SoundSynthScript := preload("res://scripts/audio/sound_synth.gd")
const SoundThemesScript := preload("res://scripts/audio/sound_themes.gd")
const SETTINGS_PATH := "user://settings.cfg"
const SFX_VOICES := 4
const BGM_VOLUME_DB := -10.0
const SFX_VOLUME_DB := -6.0

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
    var settings := ConfigFile.new()
    if settings.load(SETTINGS_PATH) == OK:
        enabled = bool(settings.get_value("audio", "enabled", true))


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
    if not enabled or not _renders_music():
        return
    if _theme_cache.has(theme_id):
        _start_theme(theme_id)
    elif not _rendering.has(theme_id):
        _rendering[theme_id] = WorkerThreadPool.add_task(_render_theme.bind(theme_id))


# A render still running when the game closes is waited for, so the
# worker never outlives the scripts it runs.
func _exit_tree() -> void:
    for task_id in _rendering.values():
        WorkerThreadPool.wait_for_task_completion(task_id)


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
        for player in _sfx_players:
            player.stop()
    else:
        var theme_id := current_theme
        current_theme = ""
        if not theme_id.is_empty():
            play_theme(theme_id)
