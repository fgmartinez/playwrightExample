"""Backward-compatible re-export for checkout page objects.

New code should import from ``pages.checkout``.
"""

from pages.checkout import CheckoutCompletePage, CheckoutInfoPage, CheckoutOverviewPage

__all__ = ["CheckoutInfoPage", "CheckoutOverviewPage", "CheckoutCompletePage"]
