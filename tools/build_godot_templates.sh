#!/usr/bin/env bash
# Builds this project's slimmed-down Godot 4.3 export templates (task #116,
# decision 0187). The stock Android template's engine library was 20.8 MiB
# of the 26-30 MiB APK; this game only uses 2D nodes, GUI controls,
# GDScript, PNG/WebP textures, one TTF font and synthesized AudioStreamWAV,
# so everything else is left out of the engine.
#
# Usage:
#   tools/build_godot_templates.sh <godot-4.3-stable source dir> android|linux
#
#   android  needs ANDROID_HOME with NDK 23.2.8568313 (Godot 4.3's NDK).
#            Writes build/templates/android_release.apk: the stock 4.3
#            android_release.apk template with its engine library replaced.
#   linux    writes build/templates/godot.linuxbsd.template_debug.x86_64,
#            the same engine configuration for the desktop smoke tests.
set -euo pipefail

SRC="$(cd "$1" && pwd)"
PLATFORM="$2"
REPO="$(cd "$(dirname "$0")/.." && pwd)"
OUT="$REPO/build/templates"
mkdir -p "$OUT"

# The engine configuration. Keep in sync with decision 0187 and with the
# contract test that reads this list.
SLIM_FLAGS=(
  production=yes
  optimize=size
  deprecated=no
  disable_3d=yes
  vulkan=no
  opengl3=yes
  brotli=no
  modules_enabled_by_default=no
  module_gdscript_enabled=yes
  module_freetype_enabled=yes
  module_text_server_fb_enabled=yes
  module_webp_enabled=yes
  module_svg_enabled=yes
)

cd "$SRC"
case "$PLATFORM" in
  android)
    scons -j"$(nproc)" platform=android target=template_release arch=arm64 "${SLIM_FLAGS[@]}"
    LIB="$SRC/platform/android/java/lib/libs/release/arm64-v8a/libgodot_android.so"
    STRIP="$(ls -d "$ANDROID_HOME"/ndk/23.2.8568313/toolchains/llvm/prebuilt/*/bin | head -1)/llvm-strip"
    STOCK="${GODOT_STOCK_TEMPLATES:-$HOME/.local/share/godot/export_templates/4.3.stable}/android_release.apk"
    WORK="$(mktemp -d)"
    mkdir -p "$WORK/lib/arm64-v8a"
    "$STRIP" --strip-unneeded -o "$WORK/lib/arm64-v8a/libgodot_android.so" "$LIB"
    cp "$STOCK" "$OUT/android_release.apk"
    # Only arm64 is exported (export_presets.cfg); drop the other ABIs.
    zip -q -d "$OUT/android_release.apk" 'lib/armeabi-v7a/*' 'lib/x86/*' 'lib/x86_64/*' || true
    (cd "$WORK" && zip -q "$OUT/android_release.apk" lib/arm64-v8a/libgodot_android.so)
    rm -rf "$WORK"
    ls -l "$OUT/android_release.apk"
    ;;
  linux)
    scons -j"$(nproc)" platform=linuxbsd target=template_debug arch=x86_64 "${SLIM_FLAGS[@]}"
    cp "$SRC/bin/godot.linuxbsd.template_debug.x86_64" "$OUT/"
    ls -l "$OUT/godot.linuxbsd.template_debug.x86_64"
    ;;
  *)
    echo "unknown platform: $PLATFORM" >&2
    exit 2
    ;;
esac
