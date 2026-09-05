# Decision 0006 — Keep checkout service and staff task switching explicit

Date: 2026-09-05

## Decision

Implement a logical checkout waiting/service layer and a minimal per-store staff roster now, but do **not** invent the original automatic dispatch, queue ordering, service-time or stamina formulas.

## Evidence driving the decision

First-title FAQ/staff evidence says:
- at most 3 staff are assigned to one store;
- staff autonomously perform register, replenishment, cleaning and rest-related work;
- waiting customers do not always cause immediate register dispatch when other work exists;
- later-arriving customers can sometimes be served before earlier customers;
- simultaneous register dispatch by two staff can cause one to return to the break room;
- at least one two-person checkout/register variant exists;
- register skill can change checkout speed dramatically.

Therefore a strict FIFO queue plus a guessed `register_skill -> N ticks` function would prematurely lock in behavior contradicted or unsupported by current evidence.

## Runtime boundary

Implement now:

```text
StoreStaffRoster
- max_staff = 3
- optional manager identity
- explicit current task

StaffTask
- IDLE
- CHECKOUT
- REPLENISH
- CLEAN
- REST

CheckoutStationRuntime
- recorded arrival order
- configurable simultaneous staff capacity
- explicit customer selection for service
- explicit begin service
- explicit finish service
- service history
```

Do not implement yet:
- automatic task priority;
- strict FIFO as an invariant;
- checkout service duration;
- impatience timer;
- stamina drain/recovery timing;
- loser-to-break-room behavior when two staff contest a register;
- automatic staff movement to the register.

## Why explicit service selection is useful

It permits tests and later observation replay to reproduce both FIFO and non-FIFO service sequences without changing the core data model. When video/guide evidence identifies the actual selection rule, that rule can become a policy layered above this runtime.

## Staff master separation

`StaffDefinition` stores evidence-tagged hiring/runtime statistics. `StaffRuntimeState` stores only the current operational state. This prevents the implementation from deriving operational starting values from hiring-screen values where the first-title staff page explicitly reports exceptions.

Primary research note:
- `docs/research/checkout-staff-dispatch-evidence-2026-09-05.md`
