from __future__ import annotations

from .checkout_anger_timing import CheckoutAngerTimingContext


class ServiceElapsedScenarioAngerPolicy:
    """Scenario-only trigger after an explicit active-service duration.

    The supplied duration is test/input data. This class is not evidence that
    the original game used this threshold or service-only timing.
    """

    def __init__(self, required_game_minutes: int) -> None:
        if required_game_minutes < 0:
            raise ValueError("required_game_minutes must be >= 0")
        self.required_game_minutes = required_game_minutes

    def should_trigger(self, context: CheckoutAngerTimingContext) -> bool:
        elapsed = context.service_elapsed_game_minutes
        return elapsed is not None and elapsed >= self.required_game_minutes


class TotalCheckoutElapsedScenarioAngerPolicy:
    """Scenario-only trigger after explicit total checkout elapsed time."""

    def __init__(self, required_game_minutes: int) -> None:
        if required_game_minutes < 0:
            raise ValueError("required_game_minutes must be >= 0")
        self.required_game_minutes = required_game_minutes

    def should_trigger(self, context: CheckoutAngerTimingContext) -> bool:
        return context.total_checkout_elapsed_game_minutes >= self.required_game_minutes
