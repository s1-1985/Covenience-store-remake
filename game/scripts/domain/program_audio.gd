extends RefCounted

# CONFIRMED_BINARY: audio_dispatch.py 80064E4C, settings_menu.py,
# save_load_control.settings 800625C4, main fragment 80023A14..23BBC.
static func settings(bits: int) -> Dictionary:
    bits &= 65535
    var choice := (bits >> 8) & 3
    return {"se_enabled": 0 if bits & 1 else 1,
        "monthly_enabled": 0 if bits & 2 else 1,
        "bgm_choice": choice,
        "bgm_id": [2, 3, 4][choice] if choice < 3 else -1}

static func pack_settings(se_off: int, bgm_choice: int, monthly_off: int) -> int:
    return (se_off & 1) | ((bgm_choice & 3) << 8) | ((monthly_off & 1) << 1)

static func dispatch(identifier: int, guard: int, enabled: int) -> Dictionary:
    if guard == 6:
        return {"kind": "none"}
    if identifier == -1:
        return {"kind": "stop"}
    if identifier < 0:
        return {"kind": "invalid"} # native negative table reads are not assets.
    if identifier < 16:
        return {"kind": "se" if enabled == 1 else "none", "index": identifier}
    if identifier < 28:
        return {"kind": "vos" if enabled == 1 else "none", "index": identifier - 16}
    return {"kind": "xa", "index": identifier - 28}

static func main_requests(flags: int, enabled: int, selected: bool, month: int, extra: int, tones: Array) -> Dictionary:
    if enabled == 0 or not selected:
        return {"requests": [], "flags": flags & 65535}
    var requests: Array = []
    for bit in 16:
        if flags & (1 << bit):
            requests.append(int({0: 50, 1: 49, 2: month + 36, 3: extra + 51}.get(bit, tones[bit])))
    return {"requests": requests, "flags": 0}
