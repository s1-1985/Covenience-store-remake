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

This Python package is not a commitment to ship the Android game in Python. It is a small, testable compatibility oracle that can later be ported to the chosen production engine.
