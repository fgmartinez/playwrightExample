"""
============================================================================
Pages Module - Page Object Model (POM)
============================================================================
This module contains all Page Object classes representing pages and
components in the application under test.

The Page Object Model (POM) pattern:
- Encapsulates page structure and behavior
- Provides a clear API for test interactions
- Improves test maintainability
- Reduces code duplication
- Makes tests more readable

Key Components:
- BasePage: Base class with common page functionality
- LoginPage: Login and authentication
- ProductsPage: Product browsing and filtering
- CartPage: Shopping cart operations
- CheckoutPage: Checkout flow
- Components: Reusable page components

Usage:
    from pages import LoginPage, ProductsPage

    async def test_login(page):
        login_page = LoginPage(page)
        await login_page.login("user", "pass")

Author: Your Name
Created: 2026-01-23
============================================================================
"""

from pages.base_page import BasePage
from pages.cart_page import CartPage
from pages.checkout_page import CheckoutInformationPage, CheckoutOverviewPage, CheckoutCompletePage
from pages.login_page import LoginPage
from pages.products_page import ProductsPage

__all__ = [
    "BasePage",
    "LoginPage",
    "ProductsPage",
    "CartPage",
    "CheckoutInformationPage",
    "CheckoutOverviewPage",
    "CheckoutCompletePage",
]
