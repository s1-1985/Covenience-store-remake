# Reference tests

Run all reference checks with:

```bash
cd reference_sim
PYTHONPATH=. python -m unittest discover -s tests -v
```

The store-grid tests deliberately distinguish **implementation representation** from **original-game evidence**. In particular, two subcells per tile is a configurable compatibility choice that allows 0.5-tile observations to be represented; it is not asserted as the original executable's internal grid format.
