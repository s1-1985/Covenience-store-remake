# Customer lifecycle milestone — 2026-09-05

This milestone adds the first customer-specific state machine on top of the store-grid and dynamic-traffic layers.

Implemented:

- explicit customer sessions tied to dynamic traffic agents;
- caller-supplied merchandise visit order;
- movement to merchandise interaction faces;
- explicit merchandise interaction event;
- checkout-required path;
- self-service-candidate path that can continue shopping or leave without normal checkout;
- explicit waiting-at-checkout state;
- explicit checkout completion event;
- leaving/exited states;
- selected-customer forced ejection path;
- unreachable-state propagation from layout/pathing;
- tests for normal, self-service, mixed, ejection and failure flows;
- GitHub Actions workflow for the reference-simulation unittest suite.

Not implemented:

- automatic product/destination selection;
- primary vs add-on probability;
- customer archetype/budget numbers;
- patience/anger timers;
- queue ordering/geometry;
- checkout duration/register-skill formula;
- shoplifting/robbery behavior;
- exact vending sale accounting.

Next safe candidates are a checkout queue/service interface with all timing left injectable, and data-model slots for ProductDefinition/CustomerArchetype so strategy-guide data can be loaded immediately when supplied.
