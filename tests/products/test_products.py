"""Products tests -- display, sorting, and cart operations on the inventory page."""

import pytest
from playwright.sync_api import expect

from pages import ProductsPage

import logging

logger = logging.getLogger(__name__)


@pytest.mark.products
@pytest.mark.smoke
class TestProductDisplay:
    """Verify the product catalogue is rendered correctly."""

    def test_page_loads_with_products(self, products_page: ProductsPage) -> None:
        """Page loads and shows a non-empty product list."""
        assert products_page.is_loaded()
        expect(products_page.title).to_contain_text("Products")
        assert products_page.get_product_count() > 0

    def test_products_have_valid_data(self, products_page: ProductsPage) -> None:
        """Every product has a non-empty name and a positive price."""
        names = products_page.get_all_product_names()
        prices = products_page.get_all_product_prices()

        assert all(name for name in names), "All products must have names"
        assert all(price > 0 for price in prices), "All prices must be positive"

    def test_product_details(self, products_page: ProductsPage) -> None:
        """A specific product's details dict contains name, description, price."""
        names = products_page.get_all_product_names()
        details = products_page.get_product_details(names[0])

        assert details["name"] == names[0]
        assert details["description"]
        assert "$" in details["price"]


@pytest.mark.products
@pytest.mark.smoke
class TestProductSorting:
    """Sorting the product list by name or price."""

    @pytest.mark.parametrize(
        "option",
        ["az", "za", "lohi", "hilo"],
        ids=["name-asc", "name-desc", "price-asc", "price-desc"],
    )
    def test_sort_products(self, products_page: ProductsPage, option: str) -> None:
        """Products are reordered correctly after selecting a sort option."""
        products_page.sort_by(option)
        assert products_page.is_sorted(option)


@pytest.mark.products
@pytest.mark.smoke
class TestCartFromProducts:
    """Adding and removing products from the inventory page."""

    def test_add_and_remove_product(self, products_page: ProductsPage) -> None:
        """A product can be added to the cart and then removed."""
        names = products_page.get_all_product_names()
        product = names[0]

        products_page.add_to_cart(product)
        assert products_page.is_product_in_cart(product)
        assert products_page.get_cart_count() == 1

        products_page.remove_from_cart(product)
        assert not products_page.is_product_in_cart(product)
        assert not products_page.has_cart_items()

    def test_cart_badge_reflects_count(self, products_page: ProductsPage) -> None:
        """The cart badge increments as products are added."""
        names = products_page.get_all_product_names()
        for i, name in enumerate(names[:3], 1):
            products_page.add_to_cart(name)
            assert products_page.get_cart_count() == i


@pytest.mark.products
class TestProductsNavigation:
    """Navigation away from the products page."""

    def test_navigate_to_cart(self, products_page: ProductsPage) -> None:
        """Cart link navigates to the cart page."""
        products_page.go_to_cart()
        assert "/cart.html" in products_page.current_url

    def test_logout(self, products_page: ProductsPage) -> None:
        """Logout via the burger menu returns to the login page."""
        products_page.logout()
        assert "inventory" not in products_page.current_url
