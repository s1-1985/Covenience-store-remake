# Direct observations from user-provided first-title play videos — 2026-09-05

Scope: first-title footage supplied directly in the project conversation. This note stores only factual readings and measured observations from the footage; no video frames or copyrighted assets are committed.

## Source videos

1. `【作業用BGM】ザ・コンビニ　1時間【プレイ動画】_HD_60fps.mp4`
   - about 1 hour
   - 1280x720
   - about 59.94 fps
   - continuous in-game footage suitable for timing observations
2. `ザ・コンビニ ～あの町を独占せよ～ コンソールアーカイブス [PS5]_HD(1).mp4`
   - about 1h33m36s
   - 1280x720
   - 30 fps
   - starts from a new game and shows store construction/configuration and fixture-selection UI clearly
3. `【レトロゲーム】ザ・コンビニ  さくさくクリア目指すプレイ.mp4`
   - about 1h41m45s
   - 640x360
   - 30 fps
   - long-run play covering roughly year 1 through at least year 4, useful for staff/town/monthly progression observations

## Evidence labels

- `DIRECT-VIDEO-VISUAL`: numeric value read directly from an in-game UI in supplied footage.
- `DIRECT-VIDEO-MEASURED`: timing/state change measured from continuous supplied footage.
- `DIRECT-VIDEO-RUNTIME-STATE`: a staff/store/town value observed at a later game date; do not treat as an initial master-table value.

## 1. Copier fixture UI values — Console Archives / PS-based footage

The fixture-selection UI visibly shows two copier variants with the following values:

| Fixture | Capacity | Attention | Purchase price | Maintenance/day | Evidence |
|---|---:|---:|---:|---:|---|
| Copier A | 20 | 10 | ¥1,500 | ¥1,200 | DIRECT-VIDEO-VISUAL |
| Copier B | 40 | 15 | ¥2,000 | ¥1,440 | DIRECT-VIDEO-VISUAL |

The footage is high enough resolution that these four numeric fields are readable directly. Footprint, interaction side, compatible-product/service mapping and any other effects are not established by this observation alone.

Implementation consequence: these fields may populate the first-title fixture master with `CONFIRMED_VISUAL`; unknown fields remain `None`.

## 2. Town-facility inducement aid values — long-run footage

Around the 70m48s area, the facility-inducement UI directly displays at least these aid amounts:

| Facility | Aid amount | Evidence |
|---|---:|---|
| Police box | ¥400,000 | DIRECT-VIDEO-VISUAL |
| Company | ¥5,400,000 | DIRECT-VIDEO-VISUAL |
| Vocational school | ¥4,800,000 | DIRECT-VIDEO-VISUAL |
| University | ¥9,800,000 | DIRECT-VIDEO-VISUAL |

These are UI-labeled aid amounts. Do not reinterpret them as land price, construction cost, monthly upkeep or population gain.

## 3. Staff runtime snapshot — do not convert to starting master stats

Around the 69-minute area, the staff-transfer/status UI shows:

`長沢達也`, age 36, male, with runtime values:

- stamina 85
- education 80
- register 75
- replenishment 65
- security 69
- cleaning 62
- service 75

Evidence: `DIRECT-VIDEO-RUNTIME-STATE`.

Important: the long-run video is already several game years into the scenario. These values may include growth, event changes, age progression and/or transfer history. Therefore they MUST NOT be written into `StaffDefinition` as first-title starting values without an earlier hiring-screen observation or guidebook confirmation.

This snapshot is still valuable for future growth-model fitting when the same staff member can be identified at an earlier timestamp or in another source.

## 4. Scenario-objective visual cross-check

The long-run footage ends with a scenario-selection screen that visibly restates:

- Beginner: induce the metropolitan government building
- Intermediate: build 10 stores
- Advanced: achieve owner rating ★★★★★

This is a direct visual cross-check of already-known first-title scenario objectives; no model change is required because the repo already stores equivalent objective semantics.

## 5. Game-time progression measurement anchor

In the one-hour continuous 60-fps video, a sampled normal-operation interval around video 2:00–2:03 showed the in-game clock advancing approximately:

- 13:16
- 13:24
- 13:32
- 13:40

at roughly one-second video intervals.

Observed local scale in that interval: approximately **8 in-game minutes per 1 real/video second**.

Evidence: `DIRECT-VIDEO-MEASURED`, but `PROVISIONAL` for global implementation because the game may expose speed modes, pauses, menus or context-dependent stepping. Do not yet hard-code this as the universal simulation clock rate.

## 6. What is now safe to measure from these videos

The footage quality/continuity is sufficient to extract empirical distributions for:

- checkout service duration;
- queue waiting/patience duration;
- customer arrivals per in-game time window;
- customer in-store dwell time;
- staff movement and task-switch timing;
- replenishment/cleaning action timing;
- day/month boundary state transitions;
- observed cash changes around known actions.

For stamina consumption per work action, an exact delta requires status-screen snapshots bracketing known work sequences. A later runtime stamina value alone is insufficient.

## 7. Rules for turning video observations into implementation values

1. One isolated event = observation only.
2. Repeated events in one continuous video = measured distribution.
3. Replication in an independent video = corroborated observation.
4. Guide/manual/Wiki agreement = promote confidence where appropriate.
5. Never infer an initial staff stat from a late-game runtime screen.
6. Never treat a local timing scale as global until speed-mode/context is ruled out.
7. Store raw timestamps and sample counts when a timing coefficient is eventually committed.
