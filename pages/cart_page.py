"""
============================================================================
Cart Page Object
============================================================================
This module defines the CartPage class for the SauceDemo shopping cart page
where users can review items, adjust quantities, and proceed to checkout.

Page URL: https://www.saucedemo.com/cart.html
Features:
- View cart items
- Remove items from cart
- Continue shopping
- Proceed to checkout

Usage:
    cart_page = CartPage(page)
    await cart_page.navigate()
    items = await cart_page.get_cart_item_names()
    await cart_page.proceed_to_checkout()

Author: Your Name
Created: 2026-01-23
============================================================================
"""

from playwright.async_api import Page

from pages.base_page import BasePage
from utils.logger import get_logger

logger = get_logger(__name__)


class CartPage(BasePage):
    """
    Page Object for SauceDemo Shopping Cart Page.

    This class provides methods to interact with the shopping cart,
    including reviewing items, removing items, and proceeding to checkout.

    Attributes:
        url: Cart page URL path
        page_title: Page title selector
        cart_items: Cart item containers
        checkout_button: Checkout button
        continue_shopping_button: Continue shopping button
    """

    def __init__(self, page: Page) -> None:
        """
        Initialize the CartPage.

        Args:
            page: Playwright page instance
        """
        super().__init__(page)
        self.url = "/cart.html"

        # Page elements
        self.page_title = ".title"
        self.cart_items = ".cart_item"
        self.checkout_button = '[data-test="checkout"]'
        self.continue_shopping_button = '[data-test="continue-shopping"]'

        # Cart item elements (relative to cart item)
        self.item_name = ".inventory_item_name"
        self.item_description = ".inventory_item_desc"
        self.item_price = ".inventory_item_price"
        self.item_quantity = ".cart_quantity"
        self.remove_button = "button[id^='remove']"

        logger.debug("CartPage initialized")

    # ========================================================================
    # Navigation Actions
    # ========================================================================

    async def proceed_to_checkout(self) -> None:
        """Click the checkout button to proceed to checkout."""
        logger.info("Proceeding to checkout")
        await self.page.locator(self.checkout_button).click()

    async def continue_shopping(self) -> None:
        """Click continue shopping button to return to products page."""
        logger.info("Continuing shopping")
        await self.page.locator(self.continue_shopping_button).click()

    # ========================================================================
    # Cart Item Operations
    # ========================================================================

    async def get_cart_item_names(self) -> list[str]:
        """
        Get names of all items in the cart.

        Returns:
            list[str]: List of item names
        """
        elements = await self.page.locator(self.item_name).all()
        names = [await elem.text_content() for elem in elements]
        cleaned_names = [name.strip() for name in names if name]
        logger.debug(f"Found {len(cleaned_names)} items in cart")
        return cleaned_names

    async def get_cart_item_count(self) -> int:
        """
        Get the number of items in the cart.

        Returns:
            int: Number of items in cart
        """
        count = await self.page.locator(self.cart_items).count()
        logger.debug(f"Cart item count: {count}")
        return count

    async def is_cart_empty(self) -> bool:
        """
        Check if the cart is empty.

        Returns:
            bool: True if cart has no items
        """
        count = await self.get_cart_item_count()
        return count == 0

    async def get_item_details(self, item_name: str) -> dict[str, str]:
        """
        Get details of a specific cart item.

        Args:
            item_name: Name of the item

        Returns:
            dict[str, str]: Item details (name, description, price, quantity)
        """
        cart_item = self.page.locator(self.cart_items).filter(has_text=item_name).first

        name = await cart_item.locator(self.item_name).text_content()
        description = await cart_item.locator(self.item_description).text_content()
        price = await cart_item.locator(self.item_price).text_content()
        quantity = await cart_item.locator(self.item_quantity).text_content()

        return {
            "name": name.strip() if name else "",
            "description": description.strip() if description else "",
            "price": price.strip() if price else "",
            "quantity": quantity.strip() if quantity else "",
        }

    async def remove_item(self, item_name: str) -> None:
        """
        Remove a specific item from the cart.

        Args:
            item_name: Name of the item to remove
        """
        logger.info(f"Removing item from cart: {item_name}")
        cart_item = self.page.locator(self.cart_items).filter(has_text=item_name).first
        remove_btn = cart_item.locator(self.remove_button)
        await remove_btn.click()

    async def remove_all_items(self) -> None:
        """Remove all items from the cart."""
        logger.info("Removing all items from cart")
        item_names = await self.get_cart_item_names()
        for item_name in item_names:
            await self.remove_item(item_name)

    async def get_cart_item_prices(self) -> list[float]:
        """
        Get prices of all items in the cart.

        Returns:
            list[float]: List of item prices
        """
        elements = await self.page.locator(self.item_price).all()
        price_texts = [await elem.text_content() for elem in elements]

        prices = []
        for price_text in price_texts:
            if price_text:
                clean_price = price_text.strip().replace("$", "")
                prices.append(float(clean_price))

        return prices

    async def calculate_items_total(self) -> float:
        """
        Calculate the total price of all items in cart.

        Returns:
            float: Total price of all items
        """
        prices = await self.get_cart_item_prices()
        total = sum(prices)
        logger.debug(f"Cart items total: ${total:.2f}")
        return total

    # ========================================================================
    # Verification Methods
    # ========================================================================

    async def is_page_loaded(self) -> bool:
        """
        Verify that the cart page is fully loaded.

        Returns:
            bool: True if page is loaded
        """
        try:
            await self.page.locator(self.page_title).wait_for(state="visible", timeout=5000)
            await self.page.locator(self.checkout_button).wait_for(state="visible", timeout=5000)
            logger.debug("Cart page fully loaded")
            return True
        except Exception as e:
            logger.error(f"Cart page not fully loaded: {e}")
            return False

    async def is_item_in_cart(self, item_name: str) -> bool:
        """
        Check if a specific item is in the cart.

        Args:
            item_name: Name of the item

        Returns:
            bool: True if item is in cart
        """
        items = await self.get_cart_item_names()
        return item_name in items

    # ========================================================================
    # Assertions
    # ========================================================================

    async def assert_cart_page_displayed(self) -> None:
        """
        Assert that the cart page is displayed correctly.

        Raises:
            AssertionError: If cart page is not displayed
        """
        await self.assert_element_visible(self.page_title)
        await self.assert_text_content(self.page_title, "Your Cart")
        logger.debug("Cart page is displayed correctly")

    async def assert_item_count(self, expected_count: int) -> None:
        """
        Assert that the cart contains the expected number of items.

        Args:
            expected_count: Expected number of items

        Raises:
            AssertionError: If count doesn't match
        """
        actual_count = await self.get_cart_item_count()
        assert actual_count == expected_count, (
            f"Expected {expected_count} items in cart, "
            f"but found {actual_count}"
        )
        logger.debug(f"Cart item count is correct: {expected_count}")

    async def assert_item_in_cart(self, item_name: str) -> None:
        """
        Assert that a specific item is in the cart.

        Args:
            item_name: Name of the item

        Raises:
            AssertionError: If item is not in cart
        """
        assert await self.is_item_in_cart(item_name), (
            f"Item '{item_name}' should be in cart"
        )
        logger.debug(f"Item '{item_name}' is in cart")
