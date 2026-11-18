# Android PS UI build v0.6.2

Continue from `chatgpt/android-touch-build-20261118`, parent d20e9f90946fe1d35d0e555df9927f22f2109fbd. Latest main (688876a) and open draft PR #270 (0c15eeb) were checked before implementation; neither was overwritten/merged.

The visual baseline is the owner's 26 images under `docs/references/ps-ui-20261118`, not the former generic phone layout. Implementation and limitations are documented there. Main selects `ps1_ui.gd` for Android / `--android-preview`; desktop presentation is unchanged.

APK versionCode 62, versionName 0.6.2-ps-ui, arm64. Keep package `com.conveniremake.touchfix` and the existing touchfix signing key (persistent signing archive from v0.6.1) to preserve update compatibility/save data. Never commit signing keys. Native Android hardware behavior remains unconfirmed.

Checks: Godot rendered `ps1_ui_smoke.gd` with `--android-preview`; staff_response_smoke.gd; signed APK export, manifest/version/signature inspection. Capture directory can be supplied using `CONVENI_CAPTURE_DIR`; screenshots are test outputs, not production assets.

Known next work: store-sale backend, persistent per-store monthly graph history, reference-driven remaining stock/dialog flows, Android device visual/tap verification. This UI change does not solve every remaining source-behavior gap.
