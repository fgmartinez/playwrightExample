"""
============================================================================
Products Page Object
============================================================================
This module defines the ProductsPage class for the SauceDemo inventory page
where users can browse, filter, sort, and add products to their cart.

Page URL: https://www.saucedemo.com/inventory.html
Features:
- Product browsing
- Sorting (name, price)
- Adding/removing items from cart
- Product details navigation
- Cart badge management

Usage:
    products_page = ProductsPage(page)
    await products_page.navigate()
    products = await products_page.get_all_product_names()
    await products_page.add_product_to_cart("Sauce Labs Backpack")

Author: Your Name
Created: 2026-01-23
============================================================================
"""

from playwright.async_api import Locator, Page

from pages.base_page import BasePage
from utils.exceptions import ElementNotFoundError
from utils.logger import get_logger

logger = get_logger(__name__)


class ProductsPage(BasePage):
    """
    Page Object for SauceDemo Products/Inventory Page.

    This class provides methods to interact with the products page,
    including browsing products, sorting, filtering, and cart operations.

    Attributes:
        url: Products page URL path
        page_title: Page title selector
        product_items: All product item containers
        product_sort_dropdown: Sort dropdown selector
        cart_badge: Shopping cart badge (item count)
        cart_link: Shopping cart link
        menu_button: Hamburger menu button
        logout_link: Logout link in menu
    """

    def __init__(self, page: Page) -> None:
        """
        Initialize the ProductsPage.

        Args:
            page: Playwright page instance
        """
        super().__init__(page)
        self.url = "/inventory.html"

        # Page elements
        self.page_title = ".title"
        self.product_items = ".inventory_item"
        self.product_sort_dropdown = '[data-test="product_sort_container"]'
        self.cart_badge = ".shopping_cart_badge"
        self.cart_link = ".shopping_cart_link"
        self.menu_button = "#react-burger-menu-btn"
        self.logout_link = "#logout_sidebar_link"

        # Product card elements (relative to product item)
        self.product_name = ".inventory_item_name"
        self.product_description = ".inventory_item_desc"
        self.product_price = ".inventory_item_price"
        self.product_image = ".inventory_item_img"
        self.add_to_cart_button = "button[id^='add-to-cart']"
        self.remove_from_cart_button = "button[id^='remove']"

        logger.debug("ProductsPage initialized")

    # ========================================================================
    # Navigation Actions
    # ========================================================================

    async def navigate_to_cart(self) -> None:
        """
        Navigate to the shopping cart page.

        Example:
            >>> await products_page.navigate_to_cart()
        """
        logger.info("Navigating to cart")
        await self.click(self.cart_link)

    async def open_menu(self) -> None:
        """
        Open the hamburger menu.

        Example:
            >>> await products_page.open_menu()
        """
        logger.info("Opening menu")
        await self.click(self.menu_button)

    async def logout(self) -> None:
        """
        Logout from the application.

        Example:
            >>> await products_page.logout()
        """
        logger.info("Logging out")
        await self.open_menu()
        await self.wait_for_selector(self.logout_link, state="visible")
        await self.click(self.logout_link)

    # ========================================================================
    # Product Discovery
    # ========================================================================

    async def get_all_product_names(self) -> list[str]:
        """
        Get names of all products on the page.

        Returns:
            list[str]: List of product names

        Example:
            >>> names = await products_page.get_all_product_names()
            >>> print(names)
            ['Sauce Labs Backpack', 'Sauce Labs Bike Light', ...]
        """
        elements = await self.page.locator(self.product_name).all()
        names = [await elem.text_content() for elem in elements]
        cleaned_names = [name.strip() for name in names if name]
        logger.debug(f"Found {len(cleaned_names)} products")
        return cleaned_names

    async def get_all_product_prices(self) -> list[float]:
        """
        Get prices of all products on the page.

        Returns:
            list[float]: List of product prices

        Example:
            >>> prices = await products_page.get_all_product_prices()
            >>> print(prices)
            [29.99, 9.99, 15.99, ...]
        """
        elements = await self.page.locator(self.product_price).all()
        price_texts = [await elem.text_content() for elem in elements]

        prices = []
        for price_text in price_texts:
            if price_text:
                # Remove $ and convert to float
                clean_price = price_text.strip().replace("$", "")
                prices.append(float(clean_price))

        logger.debug(f"Found {len(prices)} product prices")
        return prices

    async def get_product_count(self) -> int:
        """
        Get the total number of products displayed.

        Returns:
            int: Number of products

        Example:
            >>> count = await products_page.get_product_count()
            >>> assert count == 6
        """
        count = await self.get_elements_count(self.product_items)
        logger.debug(f"Product count: {count}")
        return count

    async def get_product_details(self, product_name: str) -> dict[str, str]:
        """
        Get detailed information about a specific product.

        Args:
            product_name: Name of the product

        Returns:
            dict[str, str]: Product details (name, description, price)

        Raises:
            ElementNotFoundError: If product not found

        Example:
            >>> details = await products_page.get_product_details("Sauce Labs Backpack")
            >>> print(details['price'])
            '$29.99'
        """
        try:
            # Find the product item containing this product name
            product_item = self.page.locator(self.product_items).filter(
                has_text=product_name
            ).first

            name = await product_item.locator(self.product_name).text_content()
            description = await product_item.locator(self.product_description).text_content()
            price = await product_item.locator(self.product_price).text_content()

            details = {
                "name": name.strip() if name else "",
                "description": description.strip() if description else "",
                "price": price.strip() if price else "",
            }

            logger.debug(f"Retrieved details for product: {product_name}")
            return details

        except Exception as e:
            logger.error(f"Product '{product_name}' not found: {e}")
            raise ElementNotFoundError(
                f"Product '{product_name}' not found",
                product_name=product_name,
            )

    # ========================================================================
    # Cart Operations
    # ========================================================================

    async def add_product_to_cart(self, product_name: str) -> None:
        """
        Add a specific product to the cart by name.

        Args:
            product_name: Name of the product to add

        Raises:
            ElementNotFoundError: If product not found

        Example:
            >>> await products_page.add_product_to_cart("Sauce Labs Backpack")
        """
        logger.info(f"Adding product to cart: {product_name}")
        try:
            product_item = self.page.locator(self.product_items).filter(
                has_text=product_name
            ).first

            add_button = product_item.locator(self.add_to_cart_button)
            await add_button.click()
            logger.debug(f"Product added to cart: {product_name}")

        except Exception as e:
            logger.error(f"Failed to add product to cart: {e}")
            raise ElementNotFoundError(
                f"Could not add product '{product_name}' to cart",
                product_name=product_name,
            )

    async def remove_product_from_cart(self, product_name: str) -> None:
        """
        Remove a specific product from the cart by name.

        Args:
            product_name: Name of the product to remove

        Raises:
            ElementNotFoundError: If product not found or not in cart

        Example:
            >>> await products_page.remove_product_from_cart("Sauce Labs Backpack")
        """
        logger.info(f"Removing product from cart: {product_name}")
        try:
            product_item = self.page.locator(self.product_items).filter(
                has_text=product_name
            ).first

            remove_button = product_item.locator(self.remove_from_cart_button)
            await remove_button.click()
            logger.debug(f"Product removed from cart: {product_name}")

        except Exception as e:
            logger.error(f"Failed to remove product from cart: {e}")
            raise ElementNotFoundError(
                f"Could not remove product '{product_name}' from cart",
                product_name=product_name,
            )

    async def add_multiple_products_to_cart(self, product_names: list[str]) -> None:
        """
        Add multiple products to the cart.

        Args:
            product_names: List of product names to add

        Example:
            >>> await products_page.add_multiple_products_to_cart([
            >>>     "Sauce Labs Backpack",
            >>>     "Sauce Labs Bike Light"
            >>> ])
        """
        logger.info(f"Adding {len(product_names)} products to cart")
        for product_name in product_names:
            await self.add_product_to_cart(product_name)

    async def add_all_products_to_cart(self) -> None:
        """
        Add all available products to the cart.

        Example:
            >>> await products_page.add_all_products_to_cart()
        """
        logger.info("Adding all products to cart")
        product_names = await self.get_all_product_names()
        await self.add_multiple_products_to_cart(product_names)

    async def is_product_in_cart(self, product_name: str) -> bool:
        """
        Check if a product is currently in the cart.

        Args:
            product_name: Name of the product

        Returns:
            bool: True if product is in cart (Remove button is visible)

        Example:
            >>> in_cart = await products_page.is_product_in_cart("Sauce Labs Backpack")
        """
        try:
            product_item = self.page.locator(self.product_items).filter(
                has_text=product_name
            ).first

            remove_button = product_item.locator(self.remove_from_cart_button)
            is_in_cart = await remove_button.is_visible()

            logger.debug(f"Product '{product_name}' in cart: {is_in_cart}")
            return is_in_cart

        except Exception:
            return False

    # ========================================================================
    # Cart Badge
    # ========================================================================

    async def get_cart_badge_count(self) -> int:
        """
        Get the number displayed on the cart badge.

        Returns:
            int: Number of items in cart (0 if badge not visible)

        Example:
            >>> count = await products_page.get_cart_badge_count()
            >>> assert count == 2
        """
        try:
            if await self.is_visible(self.cart_badge):
                badge_text = await self.get_text(self.cart_badge)
                count = int(badge_text)
                logger.debug(f"Cart badge count: {count}")
                return count
            else:
                logger.debug("Cart badge not visible (cart is empty)")
                return 0
        except Exception as e:
            logger.error(f"Error getting cart badge count: {e}")
            return 0

    async def is_cart_badge_visible(self) -> bool:
        """
        Check if the cart badge is visible.

        Returns:
            bool: True if cart badge is visible

        Example:
            >>> visible = await products_page.is_cart_badge_visible()
        """
        return await self.is_visible(self.cart_badge)

    # ========================================================================
    # Sorting
    # ========================================================================

    async def sort_products(self, sort_option: str) -> None:
        """
        Sort products using the sort dropdown.

        Args:
            sort_option: Sort option value
                - "az": Name (A to Z)
                - "za": Name (Z to A)
                - "lohi": Price (low to high)
                - "hilo": Price (high to low)

        Example:
            >>> await products_page.sort_products("lohi")
        """
        logger.info(f"Sorting products by: {sort_option}")
        await self.select_option(self.product_sort_dropdown, sort_option)

        # Wait for sort to take effect
        await self.wait_for_timeout(500)

    async def get_current_sort_option(self) -> str:
        """
        Get the currently selected sort option.

        Returns:
            str: Current sort option value

        Example:
            >>> option = await products_page.get_current_sort_option()
        """
        option = await self.get_attribute(self.product_sort_dropdown, "value")
        return option or "az"

    # ========================================================================
    # Verification Methods
    # ========================================================================

    async def is_page_loaded(self) -> bool:
        """
        Verify that the products page is fully loaded.

        Returns:
            bool: True if page is loaded

        Example:
            >>> await products_page.navigate()
            >>> assert await products_page.is_page_loaded()
        """
        try:
            await self.wait_for_selector(self.page_title, state="visible", timeout=5000)
            await self.wait_for_selector(self.product_items, state="visible", timeout=5000)
            logger.debug("Products page fully loaded")
            return True
        except Exception as e:
            logger.error(f"Products page not fully loaded: {e}")
            return False

    async def verify_products_sorted_alphabetically_asc(self) -> bool:
        """
        Verify that products are sorted alphabetically (A-Z).

        Returns:
            bool: True if sorted correctly

        Example:
            >>> await products_page.sort_products("az")
            >>> assert await products_page.verify_products_sorted_alphabetically_asc()
        """
        names = await self.get_all_product_names()
        sorted_names = sorted(names)
        is_sorted = names == sorted_names

        if is_sorted:
            logger.debug("Products are sorted alphabetically (A-Z)")
        else:
            logger.warning(f"Products NOT sorted alphabetically. Expected: {sorted_names}, Got: {names}")

        return is_sorted

    async def verify_products_sorted_alphabetically_desc(self) -> bool:
        """
        Verify that products are sorted alphabetically (Z-A).

        Returns:
            bool: True if sorted correctly

        Example:
            >>> await products_page.sort_products("za")
            >>> assert await products_page.verify_products_sorted_alphabetically_desc()
        """
        names = await self.get_all_product_names()
        sorted_names = sorted(names, reverse=True)
        is_sorted = names == sorted_names

        if is_sorted:
            logger.debug("Products are sorted alphabetically (Z-A)")
        else:
            logger.warning(f"Products NOT sorted alphabetically (Z-A)")

        return is_sorted

    async def verify_products_sorted_by_price_asc(self) -> bool:
        """
        Verify that products are sorted by price (low to high).

        Returns:
            bool: True if sorted correctly

        Example:
            >>> await products_page.sort_products("lohi")
            >>> assert await products_page.verify_products_sorted_by_price_asc()
        """
        prices = await self.get_all_product_prices()
        sorted_prices = sorted(prices)
        is_sorted = prices == sorted_prices

        if is_sorted:
            logger.debug("Products are sorted by price (low to high)")
        else:
            logger.warning(f"Products NOT sorted by price. Expected: {sorted_prices}, Got: {prices}")

        return is_sorted

    async def verify_products_sorted_by_price_desc(self) -> bool:
        """
        Verify that products are sorted by price (high to low).

        Returns:
            bool: True if sorted correctly

        Example:
            >>> await products_page.sort_products("hilo")
            >>> assert await products_page.verify_products_sorted_by_price_desc()
        """
        prices = await self.get_all_product_prices()
        sorted_prices = sorted(prices, reverse=True)
        is_sorted = prices == sorted_prices

        if is_sorted:
            logger.debug("Products are sorted by price (high to low)")
        else:
            logger.warning(f"Products NOT sorted by price (high to low)")

        return is_sorted

    # ========================================================================
    # Assertions
    # ========================================================================

    async def assert_products_page_displayed(self) -> None:
        """
        Assert that the products page is displayed correctly.

        Raises:
            AssertionError: If products page is not displayed

        Example:
            >>> await products_page.assert_products_page_displayed()
        """
        await self.assert_element_visible(self.page_title)
        await self.assert_text_content(self.page_title, "Products")
        logger.debug("Products page is displayed correctly")

    async def assert_cart_badge_count(self, expected_count: int) -> None:
        """
        Assert that the cart badge shows the expected count.

        Args:
            expected_count: Expected number of items in cart

        Raises:
            AssertionError: If count doesn't match

        Example:
            >>> await products_page.assert_cart_badge_count(2)
        """
        actual_count = await self.get_cart_badge_count()
        assert actual_count == expected_count, (
            f"Expected cart badge count to be {expected_count}, "
            f"but got {actual_count}"
        )
        logger.debug(f"Cart badge count is correct: {expected_count}")

    async def assert_product_in_cart(self, product_name: str) -> None:
        """
        Assert that a product is in the cart.

        Args:
            product_name: Name of the product

        Raises:
            AssertionError: If product is not in cart

        Example:
            >>> await products_page.assert_product_in_cart("Sauce Labs Backpack")
        """
        is_in_cart = await self.is_product_in_cart(product_name)
        assert is_in_cart, f"Product '{product_name}' should be in cart"
        logger.debug(f"Product '{product_name}' is in cart")
