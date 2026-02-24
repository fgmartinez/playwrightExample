"""Reusable UI components that are composed into page objects.

Each component encapsulates a single, well-defined piece of the UI.
Pages *compose* the components they need rather than inheriting behaviour
they might not use.
"""

from pages.components.burger_menu import BurgerMenu
from pages.components.cart_icon import CartIcon
from pages.components.cart_item import CartItem
from pages.components.error_banner import ErrorBanner
from pages.components.price_summary import PriceSummary
from pages.components.product_card import ProductCard

__all__ = [
    "BurgerMenu",
    "CartIcon",
    "CartItem",
    "ErrorBanner",
    "PriceSummary",
    "ProductCard",
]
