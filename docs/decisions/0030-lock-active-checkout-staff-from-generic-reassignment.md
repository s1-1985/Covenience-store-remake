# Decision 0030: lock active checkout staff from generic task reassignment

## Context

The generic staff-task policy is intentionally replaceable and may choose checkout, replenishment or cleaning from objective candidates. After checkout service start, however, the checkout runtime already owns an in-progress service lifecycle until explicit completion/cancellation.

Without a lock, a later generic task-policy evaluation could overwrite the cashier's task with replenishment or cleaning while the checkout runtime still considered that same staff member actively serving a customer.

## Decision

1. Let `StaffTaskPolicyCoordinator.apply_policy(...)` accept caller-supplied `locked_staff_ids`.
2. Locked staff are skipped exactly like other unavailable staff for that policy evaluation.
3. `StoreStepOrchestrator` locks every staff member currently present in a checkout station's active service set before generic task reconsideration.
4. The lock ends automatically when checkout service is explicitly completed/cancelled and the active-service record disappears.

## Evidence boundary

This is a state-machine consistency rule, not a claim that original staff can never interrupt checkout work. Known/possible stamina interruption, abandonment and emergency reassignment remain explicit future policies. The generic task selector must not silently cause those transitions.
