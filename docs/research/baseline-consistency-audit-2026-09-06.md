# Baseline consistency audit — 2026-09-06

Scope: cross-check executable baseline values against already-merged first-title research notes. This is a consistency pass only; no new original-game value is invented here.

## University population observation regression

The executable baseline still carried the older provisional range `700..800` for the PS university population effect.

Already-merged research documents state that the PS long-play observation should be treated as approximately `500..800`:

- `docs/research/university-population-and-induction-timing-2026-09-05.md`
- `docs/research/ss-operation-town-event-delta-2026-09-05.md`

The baseline is therefore corrected to `500..800`, still with `PROVISIONAL` evidence. This is an observed range, not a guidebook fixed value and not an exact formula.

## Large-store orientation evidence boundary

The first-title Wiki reports that the large store is asymmetric (`13 x 14`) and that the upper/vertical choice in the construction list has more editable floor area; it also reports a cursor-reach bug on that vertical variant. The current executable model does not yet know the exact mapping between list position and canonical orientation labels for all six variants, so this audit does **not** assign `vertical`/`horizontal` names or invent the second large-store dimensions.

Source: https://wikiwiki.jp/theconveni1/%E5%86%85%E8%A3%85

## Staff cap relationships

The first-title Wiki reports common relationships between hiring-screen stats and runtime caps:

- academic background / education -> register and security caps in many cases
- agility -> replenishment cap
- sociability -> cleaning and service caps
- exceptions exist

Because exceptions are explicitly reported and the full 35-row numeric master is not yet recovered, these relationships remain research rules and are not converted into hard automatic caps in the executable staff runtime yet.

Source: https://wikiwiki.jp/theconveni1/%E5%BA%97%E5%93%A1
