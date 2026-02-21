"""
Pages Module - Page Object Model
================================
Page objects and reusable components for the SauceDemo application.

Design Principles:
- Composition over inheritance: shared behaviour lives in page_helpers
- Elements defined as Locators for clean, chainable interactions
- Semantic locators (get_by_test_id, get_by_role) preferred
- Reusable components for repeated UI patterns
- Minimal abstraction — leverage Playwright's native API
"""

from pages.cart_page import CartPage
from pages.checkout_page import (
    CheckoutCompletePage,
    CheckoutInfoPage,
    CheckoutOverviewPage,
)
from pages.components import CartItem, PriceSummary, ProductCard
from pages.login_page import LoginPage
from pages.page_helpers import BasePage, get_text, is_visible_safe, navigate_to, wait_for_load
from pages.products_page import ProductsPage

__all__ = [
    # Base
    "BasePage",
    # Helpers
    "navigate_to",
    "wait_for_load",
    "get_text",
    "is_visible_safe",
    # Pages
    "LoginPage",
    "ProductsPage",
    "CartPage",
    "CheckoutInfoPage",
    "CheckoutOverviewPage",
    "CheckoutCompletePage",
    # Components
    "ProductCard",
    "CartItem",
    "PriceSummary",
]
