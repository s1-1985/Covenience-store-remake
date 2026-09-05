# Reference simulation core

This directory is the **executable research/reference model** for the 1997 PS/SS baseline. It is intentionally separate from the future Android rendering/game client.

Why start here:

- the gameplay/data model is already much better understood than the final art pipeline;
- strategy-guide pages can fill missing values without rewriting rendering code;
- unresolved formulas must remain visibly unresolved instead of being silently guessed;
- tests can lock confirmed behavior before the production engine is chosen.

Run:

```bash
cd reference_sim
PYTHONPATH=. python -m unittest discover -s tests -v
```

Rules:

1. `None` means **unknown**, not zero.
2. Do not copy values from The Conveni 2/3/200X/DS/SP.
3. Every recovered value carries an evidence label/source.
4. `remake_balanced_default` may be introduced only after reasonable research fails.
5. The month-end accounting formula, customer-share formula and AI priorities are deliberately not invented yet.

## Current executable layers

- `baseline_data.py` — evidence-tagged store/fixture/promotion/permit/scenario/town anchors.
- `clock.py` — the representative day 1–4 month clock.
- `store_grid.py` — rectangular store space, fixture footprint/rotation, interaction side, obstacles and deterministic shortest-path queries.
- `traffic.py` — dynamic occupancy, blocking/wait counters, interaction-edge goals and configurable rerouting experiments.
- `customer.py` — explicit customer lifecycle from supplied merchandise goals through checkout/self-service-candidate and exit/ejection, without inventing purchase probabilities or service timing.
- `staff.py` — per-store roster cap, optional manager identity, explicit work/rest task state, work-event counters, and the confirmed stamina->break-room->full-recovery lifecycle without guessed rates.
- `checkout.py` — logical register waiting/service runtime with configurable simultaneous cashier capacity, non-FIFO-capable service selection and explicit service completion.
- `master_audit.py` — field-level completeness audit for guide-derived fixture/product/customer/staff masters; only evidence-tagged values count as known.

`store_grid.py` defaults to **2 internal subcells per researched tile** so a half-tile contact/gap can be represented. This is a compatibility representation, not a claim that the original executable literally used a 0.5-tile navigation grid. The scale remains configurable until stronger evidence is recovered.

Pathfinding in `store_grid.py` is intentionally simple 4-neighbor BFS. `traffic.py` adds moving entities, but one harness tick/step is **not** mapped to an original frame, second or movement speed. The default reroute threshold remains `None` because the original collision retry/reroute timing is still unknown.

`customer.py` also avoids hidden assumptions: merchandise visit order and checkout-vs-self-service flow are provided explicitly by the caller, checkout completion is explicit, and no patience/purchase-choice formula exists yet.

`checkout.py` records waiting arrival order but does not force FIFO, because first-title FAQ evidence reports later-arriving customers sometimes being served first. Checkout service has no built-in duration; callers must explicitly finish it until the register-skill timing formula is recovered.

`staff.py` similarly has no default stamina cost or recovery-per-tick constant. A known stamina value may be supplied, explicit work/recovery events can mutate it, and reaching zero enters a separate return-to-break-room state before resting until full recovery.

The product/customer/fixture/staff schema is intentionally sparse until strategy-guide data is supplied. `master_audit.py` makes missing fields measurable without converting unknowns into zeros or guesses.

This Python package is not a commitment to ship the Android game in Python. It is a small, testable compatibility oracle that can later be ported to the chosen production engine.
