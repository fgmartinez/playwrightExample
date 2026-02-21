"""
Pages Module - Page Object Model
================================
Page objects and reusable components for the SauceDemo application.

Design Principles:
- Composition over inheritance: page objects hold a PageNavigator rather
  than extending a base class
- Elements defined as Locators (not strings) for cleaner interactions
- Semantic locators (get_by_test_id, get_by_role) preferred
- Reusable components for repeated UI patterns
- Minimal abstraction - leverage Playwright's native API

Usage:
    from pages import LoginPage, ProductsPage, ProductCard

    async def test_add_to_cart(page):
        login = LoginPage(page)
        await login.navigate()
        await login.login("user", "pass")

        products = ProductsPage(page)
        await products.add_to_cart("Sauce Labs Backpack")

        # Or use component directly
        card = ProductCard.by_name(page, "Sauce Labs Backpack")
        await card.add_to_cart()
"""

from pages.cart_page import CartPage
from pages.checkout_page import (
    CheckoutCompletePage,
    CheckoutInfoPage,
    CheckoutOverviewPage,
)
from pages.components import CartItem, PriceSummary, ProductCard
from pages.login_page import LoginPage
from pages.navigator import PageNavigator, get_text, is_visible_safe
from pages.products_page import ProductsPage

__all__ = [
    # Navigation
    "PageNavigator",
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
