# Checkout / staff-dispatch evidence delta — 2026-09-05

Scope: first-title PS/SS Wiki evidence for register dispatch, waiting behavior and staff runtime structure.

Primary sources:
- https://wikiwiki.jp/theconveni1/FAQ
- https://wikiwiki.jp/theconveni1/%E5%BA%97%E5%93%A1

## 1. Checkout waiting is not safely modeled as strict FIFO

The first-title FAQ reports a case where, after register work begins, a customer who joined later can be checked out before someone who had already been waiting.

Evidence level: `CONFIRMED-COMMUNITY / FIRST-TITLE-SPECIFIC` for the observed behavior.

Implementation consequence:

```text
checkout_waiting_pool
- record arrival order for observation/debugging
- do NOT make FIFO a hard invariant
- service selection policy = UNKNOWN / replaceable
```

This does not prove the exact internal selection rule. It only proves that a strict FIFO implementation would be too strong.

## 2. Staff do not necessarily abandon other work immediately for a waiting customer

The FAQ reports that customers may already be waiting at the register while staff continue tasks such as replenishment, with the staff going to the register only very late.

Evidence level: `CONFIRMED-COMMUNITY / BEHAVIORAL`.

Implementation consequence:

```text
StaffTaskPriority
- checkout vs replenishment priority threshold = UNKNOWN
- do not auto-preempt replenishment merely because waiting_count > 0
```

The runtime layer should expose task assignment/switching without yet inventing the original priority function.

## 3. Simultaneous cashier dispatch has special/weird behavior

The FAQ reports that when two staff head to a register at the same time, one may return to the break room and remain there for a while. If the staff member who actually starts register work is nearly out of stamina, that staff member may also leave soon, creating an unmanned register.

Evidence level: `CONFIRMED-COMMUNITY / FIRST-TITLE-FAQ-OBSERVATION`.

Implementation consequence:
- do not assume `waiting customer -> nearest two free staff both work register`;
- do not invent the exact loser-to-break-room timing yet;
- checkout station capacity and staff dispatch must remain separate concepts.

## 4. At least one two-person checkout variant exists

The first-title staff page explicitly recommends introducing a `2人打ちのレジ` before considering extremely slow-register staff.

Evidence level: `CONFIRMED-COMMUNITY / FIRST-TITLE-SPECIFIC`.

Safe structural requirement:

```text
CheckoutStationRuntime
- simultaneous_staff_capacity: configurable
```

Do not yet assign the capacity to a named fixture row until the complete fixture master is recovered.

## 5. Register skill has a very large service-time effect

The staff page reports that the lowest register skill can be so slow that one customer may effectively take a whole game day to process, while high-skill staff can become extremely fast.

Evidence level: `CONFIRMED-COMMUNITY / QUALITATIVE`.

This supports a strong dependency:

```text
checkout_duration = strongly dependent on staff.register_skill
```

but does not provide a numeric function. No seconds/ticks-per-skill formula should be invented yet.

## 6. Staff master/runtime separation remains required

The staff page confirms:
- 35 total staff candidates;
- at most 3 staff assigned per store;
- hiring-screen values and runtime operational values are separate;
- runtime values include education, register, replenishment, security, cleaning and service;
- education commonly bounds register/security;
- agility bounds replenishment and appears related to rest recovery;
- sociability bounds cleaning/service;
- manager education affects subordinate growth.

Implementation consequence:
- keep `StaffDefinition` (master values) separate from `StaffRuntimeState` (current task/state);
- preserve unknown numeric values as `None` until guidebook extraction;
- do not derive runtime starting skills mechanically from hiring values because explicit exceptions exist.

## Current implementation boundary

Safe now:
- three-person roster cap;
- explicit manager identity;
- explicit staff tasks: checkout / replenish / clean / rest / idle;
- non-FIFO-capable waiting pool;
- configurable simultaneous cashier capacity;
- explicit begin/finish checkout events.

Still unknown:
- automatic task priority function;
- register dispatch threshold;
- queue geometry and impatience thresholds;
- exact checkout duration formula;
- exact two-person register behavior;
- exact break-room fallback timing;
- exact stamina consumption/recovery rates.
