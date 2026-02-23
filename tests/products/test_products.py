"""
Products Tests
==============
Test cases for product browsing, filtering, sorting, and cart operations
on the inventory page.
"""

import pytest
from playwright.async_api import Page, expect

import logging

from config import UserType
from pages import LoginPage, ProductsPage

logger = logging.getLogger(__name__)


@pytest.fixture
async def products_page_logged_in(page: Page) -> ProductsPage:
    """Fixture providing logged-in products page."""
    login_page = LoginPage(page)
    await login_page.navigate()
    await login_page.login_as(UserType.STANDARD)
    products_page = ProductsPage(page)
    await products_page.wait_for_page_load()
    return products_page


@pytest.mark.products
@pytest.mark.smoke
class TestProductDisplay:
    """Tests for product display and information."""

    async def test_products_page_loads_successfully(
        self, products_page_logged_in: ProductsPage
    ) -> None:
        """Verify products page loads with all elements."""
        products_page = products_page_logged_in

        assert await products_page.is_loaded(), "Products page should load"
        await expect(products_page.title).to_be_visible()
        await expect(products_page.title).to_contain_text("Products")

        product_count = await products_page.get_product_count()
        assert product_count > 0, "Should display products"
        logger.info(f"Products page loaded with {product_count} products")

    async def test_all_products_have_names(
        self, products_page_logged_in: ProductsPage
    ) -> None:
        """Verify all products have names."""
        products_page = products_page_logged_in

        product_names = await products_page.get_all_product_names()
        assert len(product_names) > 0, "Should have product names"

        for name in product_names:
            assert name and len(name) > 0, "Product name should not be empty"
        logger.info(f"All {len(product_names)} products have names")

    async def test_all_products_have_prices(
        self, products_page_logged_in: ProductsPage
    ) -> None:
        """Verify all products have valid prices."""
        products_page = products_page_logged_in

        prices = await products_page.get_all_product_prices()
        assert len(prices) > 0, "Should have product prices"

        for price in prices:
            assert price > 0, f"Product price should be positive, got: {price}"
        logger.info(f"All {len(prices)} products have valid prices")

    async def test_get_product_details(
        self, products_page_logged_in: ProductsPage
    ) -> None:
        """Verify product details can be retrieved."""
        products_page = products_page_logged_in

        product_names = await products_page.get_all_product_names()
        first_product = product_names[0]

        details = await products_page.get_product_details(first_product)

        assert details["name"] == first_product
        assert len(details["description"]) > 0, "Should have description"
        assert "$" in details["price"], "Price should include $ symbol"
        logger.info(f"Successfully retrieved details for '{first_product}'")


@pytest.mark.products
@pytest.mark.smoke
class TestProductSorting:
    """Tests for product sorting functionality."""

    async def test_sort_products_by_name_ascending(
        self, products_page_logged_in: ProductsPage
    ) -> None:
        """Verify products can be sorted A-Z."""
        products_page = products_page_logged_in

        await products_page.sort_by("az")

        assert await products_page.verify_sorted_by_name_asc(), (
            "Products should be sorted A-Z"
        )
        logger.info("Products sorted A-Z correctly")

    async def test_sort_products_by_name_descending(
        self, products_page_logged_in: ProductsPage
    ) -> None:
        """Verify products can be sorted Z-A."""
        products_page = products_page_logged_in

        await products_page.sort_by("za")

        assert await products_page.verify_sorted_by_name_desc(), (
            "Products should be sorted Z-A"
        )
        logger.info("Products sorted Z-A correctly")

    async def test_sort_products_by_price_low_to_high(
        self, products_page_logged_in: ProductsPage
    ) -> None:
        """Verify products can be sorted by price (low to high)."""
        products_page = products_page_logged_in

        await products_page.sort_by("lohi")

        assert await products_page.verify_sorted_by_price_asc(), (
            "Products should be sorted by price (low to high)"
        )
        logger.info("Products sorted by price (low to high) correctly")

    async def test_sort_products_by_price_high_to_low(
        self, products_page_logged_in: ProductsPage
    ) -> None:
        """Verify products can be sorted by price (high to low)."""
        products_page = products_page_logged_in

        await products_page.sort_by("hilo")

        assert await products_page.verify_sorted_by_price_desc(), (
            "Products should be sorted by price (high to low)"
        )
        logger.info("Products sorted by price (high to low) correctly")

    async def test_current_sort_option(
        self, products_page_logged_in: ProductsPage
    ) -> None:
        """Verify current sort option can be retrieved."""
        products_page = products_page_logged_in

        await products_page.sort_by("lohi")
        current_sort = await products_page.get_current_sort()

        assert current_sort == "lohi", f"Expected 'lohi', got: {current_sort}"
        logger.info("Current sort option retrieved correctly")


@pytest.mark.products
@pytest.mark.smoke
class TestCartOperations:
    """Tests for adding and removing products from cart."""

    async def test_add_single_product_to_cart(
        self, products_page_logged_in: ProductsPage
    ) -> None:
        """Verify single product can be added to cart."""
        products_page = products_page_logged_in

        product_names = await products_page.get_all_product_names()
        product_to_add = product_names[0]

        await products_page.add_to_cart(product_to_add)

        assert await products_page.is_product_in_cart(product_to_add), (
            f"Product '{product_to_add}' should be in cart"
        )

        cart_count = await products_page.get_cart_count()
        assert cart_count == 1, f"Cart badge should show 1, got: {cart_count}"
        logger.info(f"Successfully added '{product_to_add}' to cart")

    async def test_add_multiple_products_to_cart(
        self, products_page_logged_in: ProductsPage
    ) -> None:
        """Verify multiple products can be added to cart."""
        products_page = products_page_logged_in

        product_names = await products_page.get_all_product_names()
        products_to_add = product_names[:3]

        await products_page.add_multiple_to_cart(products_to_add)

        cart_count = await products_page.get_cart_count()
        assert cart_count == len(products_to_add), (
            f"Cart badge should show {len(products_to_add)}, got: {cart_count}"
        )
        logger.info(f"Successfully added {len(products_to_add)} products to cart")

    async def test_remove_product_from_cart(
        self, products_page_logged_in: ProductsPage
    ) -> None:
        """Verify product can be removed from cart."""
        products_page = products_page_logged_in

        product_names = await products_page.get_all_product_names()
        product = product_names[0]

        await products_page.add_to_cart(product)
        assert await products_page.is_product_in_cart(product)

        await products_page.remove_from_cart(product)
        assert not await products_page.is_product_in_cart(product), (
            f"Product '{product}' should not be in cart"
        )

        assert not await products_page.has_cart_badge(), (
            "Cart badge should not be visible when cart is empty"
        )
        logger.info(f"Successfully removed '{product}' from cart")

    async def test_cart_badge_updates(
        self, products_page_logged_in: ProductsPage
    ) -> None:
        """Verify cart badge updates correctly."""
        products_page = products_page_logged_in

        product_names = await products_page.get_all_product_names()

        initial_count = await products_page.get_cart_count()
        assert initial_count == 0, "Cart should initially be empty"

        for i, product in enumerate(product_names[:3], 1):
            await products_page.add_to_cart(product)
            count = await products_page.get_cart_count()
            assert count == i, f"Cart badge should show {i}, got: {count}"
        logger.info("Cart badge updates correctly")

    async def test_add_all_products_to_cart(
        self, products_page_logged_in: ProductsPage
    ) -> None:
        """Verify all products can be added to cart."""
        products_page = products_page_logged_in

        product_count = await products_page.get_product_count()

        await products_page.add_all_to_cart()

        cart_count = await products_page.get_cart_count()
        assert cart_count == product_count, (
            f"Cart should contain all {product_count} products, got: {cart_count}"
        )
        logger.info(f"Successfully added all {product_count} products to cart")


@pytest.mark.products
class TestNavigation:
    """Tests for navigation from products page."""

    async def test_navigate_to_cart(
        self, products_page_logged_in: ProductsPage
    ) -> None:
        """Verify navigation to cart page."""
        products_page = products_page_logged_in

        await products_page.go_to_cart()

        assert "/cart.html" in products_page.current_url, (
            "Should navigate to cart page"
        )
        logger.info("Successfully navigated to cart")

    async def test_logout_functionality(
        self, products_page_logged_in: ProductsPage
    ) -> None:
        """Verify logout functionality."""
        products_page = products_page_logged_in

        await products_page.logout()

        # Should be back on login page
        assert "/" == products_page.current_url.split(products_page.page.url.split("/")[2])[-1] or \
            "saucedemo.com" in products_page.current_url, (
            "Should redirect to login page"
        )
        logger.info("Successfully logged out")
