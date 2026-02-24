"""Shared test fixtures for all test modules.

Centralises the login + navigation boilerplate so individual test files
stay focused on assertions.
"""

import pytest
from playwright.sync_api import Page

from config import UserType
from pages import CartPage, CheckoutInfoPage, LoginPage, ProductsPage
from utils.helpers import generate_test_user_data


@pytest.fixture
def login_page(page: Page) -> LoginPage:
    """A ``LoginPage`` that has already navigated to the login URL."""
    lp = LoginPage(page)
    lp.navigate()
    return lp


@pytest.fixture
def products_page(page: Page) -> ProductsPage:
    """Logged-in ``ProductsPage`` ready for interaction."""
    lp = LoginPage(page)
    lp.navigate()
    lp.login_as(UserType.STANDARD)
    pp = ProductsPage(page)
    pp.wait_for_page_load()
    return pp


@pytest.fixture
def cart_with_items(page: Page) -> CartPage:
    """``CartPage`` with two products already added."""
    lp = LoginPage(page)
    lp.navigate()
    lp.login_as(UserType.STANDARD)

    pp = ProductsPage(page)
    pp.wait_for_page_load()
    names = pp.get_all_product_names()
    pp.add_multiple_to_cart(names[:2])
    pp.go_to_cart()

    cp = CartPage(page)
    cp.wait_for_page_load()
    return cp


@pytest.fixture
def checkout_info_page(page: Page) -> CheckoutInfoPage:
    """``CheckoutInfoPage`` reached after adding items and proceeding."""
    lp = LoginPage(page)
    lp.navigate()
    lp.login_as(UserType.STANDARD)

    pp = ProductsPage(page)
    names = pp.get_all_product_names()
    pp.add_multiple_to_cart(names[:2])
    pp.go_to_cart()

    cp = CartPage(page)
    cp.proceed_to_checkout()

    return CheckoutInfoPage(page)


@pytest.fixture
def user_data() -> dict[str, str]:
    """Random user data generated via Faker."""
    return generate_test_user_data()
