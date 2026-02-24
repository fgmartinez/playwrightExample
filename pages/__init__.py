"""Page Object Model for the SauceDemo application.

Architecture
~~~~~~~~~~~~
- ``BasePage`` -- minimal base for *all* pages (navigation, URL, is_loaded)
- ``AuthenticatedPage`` -- extends BasePage with shared header components
  (``BurgerMenu``, ``CartIcon``) for every post-login page
- Individual page classes compose the components they need (SRP)
- Reusable UI components live in ``pages.components``
"""

from pages.base_page import AuthenticatedPage, BasePage
from pages.cart_page import CartPage
from pages.checkout_page import (
    CheckoutCompletePage,
    CheckoutInfoPage,
    CheckoutOverviewPage,
)
from pages.components import (
    BurgerMenu,
    CartIcon,
    CartItem,
    ErrorBanner,
    PriceSummary,
    ProductCard,
)
from pages.login_page import LoginPage
from pages.page_helpers import get_text, is_visible_safe, navigate_to, wait_for_load
from pages.products_page import ProductsPage

__all__ = [
    # Base
    "BasePage",
    "AuthenticatedPage",
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
    "BurgerMenu",
    "CartIcon",
    "CartItem",
    "ErrorBanner",
    "PriceSummary",
    "ProductCard",
]
