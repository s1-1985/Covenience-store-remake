# Decision 0028: explicit staff work completion boundary

## Context

The first-title evidence confirms that replenishment and floor cleaning are staff work events and that they can affect stamina and skill growth. The current runtime can already discover objective work candidates and assign them through a replaceable staff-task policy.

What remains unresolved is equally important: exact work duration, replenishment quantity, stamina cost, movement timing, and whether/how often a staff member reconsiders the task before completion.

## Decision

1. Keep task assignment and task completion as separate transitions.
2. Add `StaffWorkCompletionCoordinator` for non-checkout work only.
3. Replenishment completion requires an explicit quantity; the runtime never infers "fill to full" or a reorder amount.
4. Cleaning completion acts only on the exact dirty floor-cell target that was assigned.
5. Completion reuses the existing inventory/cash/cleaning/staff-growth/stamina bookkeeping.
6. If explicit stamina consumption reaches zero, preserve the existing transition toward the break room instead of forcing the staff member back to idle.
7. Checkout remains outside this coordinator because its customer selection and service-duration lifecycle is distinct.

## Not decided

- replenishment quantity policy
- replenishment/cleaning duration
- staff movement duration
- stamina cost per action
- cleaning route/area-of-effect
- task interruption or reassignment cadence
- whether multiple stock units are one work event or several in the original engine

These remain replaceable policy or observation inputs.
