extends SceneTree

func _initialize() -> void:
    var scene: Node = load("res://scenes/main.tscn").instantiate()
    root.add_child(scene)
    await process_frame
    scene.set_process(false)
    for i in range(300):
        scene.simulation.tick()
    scene._refresh_ui()
    await process_frame
    await process_frame
    root.get_texture().get_image().save_png("/tmp/claude-0/-home-user-Covenience-store-remake/2f549f4c-3dea-5a11-864d-00b38be333b2/scratchpad/cap_ja_desktop.png")
    var scroll: ScrollContainer = scene.get_node("UI/Panel/Margin/Scroll")
    for k in range(1, 8):
        scroll.scroll_vertical = k * 520
        await process_frame
        await process_frame
        root.get_texture().get_image().save_png("/tmp/claude-0/-home-user-Covenience-store-remake/2f549f4c-3dea-5a11-864d-00b38be333b2/scratchpad/cap_ja_desktop_%d.png" % k)
    quit()
