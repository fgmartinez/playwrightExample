"""Price summary dataclass used by the checkout overview page."""

from dataclasses import dataclass


@dataclass
class PriceSummary:
    """Subtotal, tax, and total for a checkout order."""

    subtotal: float
    tax: float
    total: float

    def verify_calculation(self) -> bool:
        """Return True when ``total == subtotal + tax`` (to 2 dp)."""
        return round(self.subtotal + self.tax, 2) == round(self.total, 2)
