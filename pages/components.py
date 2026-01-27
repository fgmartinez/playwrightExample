"""
Reusable Page Components
========================
Component classes for elements that appear across multiple pages.
These encapsulate the structure and behavior of repeatable UI patterns.

Components are initialized with a root locator and provide methods
to interact with their child elements.

Usage:
    # Get a specific product card
    card = ProductCard(page.locator(".inventory_item").filter(has_text="Backpack").first)
    await card.add_to_cart()
    price = await card.get_price()

    # Iterate over all cards
    for card in await ProductCard.all_on_page(page):
        print(await card.get_name())
"""

from dataclasses import dataclass
from playwright.async_api import Locator, Page

from utils.logger import get_logger

logger = get_logger(__name__)


class ProductCard:
    """
    Component representing a product card on the inventory page.

    Encapsulates the product's name, description, price, image,
    and add/remove cart buttons.
    """

    # Child selectors (relative to card root)
    NAME = ".inventory_item_name"
    DESCRIPTION = ".inventory_item_desc"
    PRICE = ".inventory_item_price"
    IMAGE = ".inventory_item_img"
    ADD_TO_CART = "button[id^='add-to-cart']"
    REMOVE = "button[id^='remove']"

    def __init__(self, root: Locator) -> None:
        """
        Initialize with a locator pointing to the product card container.

        Args:
            root: Locator for .inventory_item element
        """
        self.root = root
        self.name = root.locator(self.NAME)
        self.description = root.locator(self.DESCRIPTION)
        self.price = root.locator(self.PRICE)
        self.image = root.locator(self.IMAGE)
        self.add_to_cart_button = root.locator(self.ADD_TO_CART)
        self.remove_button = root.locator(self.REMOVE)

    @classmethod
    def all_cards(cls, page: Page) -> Locator:
        """Get locator for all product cards on page."""
        return page.locator(".inventory_item")

    @classmethod
    def by_name(cls, page: Page, name: str) -> "ProductCard":
        """Get a specific product card by name."""
        root = cls.all_cards(page).filter(has_text=name).first
        return cls(root)

    async def get_name(self) -> str:
        """Get product name."""
        text = await self.name.text_content()
        return (text or "").strip()

    async def get_description(self) -> str:
        """Get product description."""
        text = await self.description.text_content()
        return (text or "").strip()

    async def get_price(self) -> float:
        """Get product price as float."""
        text = await self.price.text_content()
        if text:
            return float(text.strip().replace("$", ""))
        return 0.0

    async def get_details(self) -> dict[str, str]:
        """Get all product details as dict."""
        return {
            "name": await self.get_name(),
            "description": await self.get_description(),
            "price": (await self.price.text_content() or "").strip(),
        }

    async def add_to_cart(self) -> None:
        """Click add to cart button."""
        logger.debug(f"Adding to cart: {await self.get_name()}")
        await self.add_to_cart_button.click()

    async def remove_from_cart(self) -> None:
        """Click remove button."""
        logger.debug(f"Removing from cart: {await self.get_name()}")
        await self.remove_button.click()

    async def is_in_cart(self) -> bool:
        """Check if product is in cart (remove button visible)."""
        return await self.remove_button.is_visible()

    async def click_name(self) -> None:
        """Click product name to view details."""
        await self.name.click()


class CartItem:
    """
    Component representing an item in the shopping cart.

    Similar to ProductCard but includes quantity and is used
    on the cart and checkout pages.
    """

    # Child selectors
    NAME = ".inventory_item_name"
    DESCRIPTION = ".inventory_item_desc"
    PRICE = ".inventory_item_price"
    QUANTITY = ".cart_quantity"
    REMOVE = "button[id^='remove']"

    def __init__(self, root: Locator) -> None:
        """
        Initialize with a locator pointing to the cart item container.

        Args:
            root: Locator for .cart_item element
        """
        self.root = root
        self.name = root.locator(self.NAME)
        self.description = root.locator(self.DESCRIPTION)
        self.price = root.locator(self.PRICE)
        self.quantity = root.locator(self.QUANTITY)
        self.remove_button = root.locator(self.REMOVE)

    @classmethod
    def all_items(cls, page: Page) -> Locator:
        """Get locator for all cart items on page."""
        return page.locator(".cart_item")

    @classmethod
    def by_name(cls, page: Page, name: str) -> "CartItem":
        """Get a specific cart item by name."""
        root = cls.all_items(page).filter(has_text=name).first
        return cls(root)

    async def get_name(self) -> str:
        """Get item name."""
        text = await self.name.text_content()
        return (text or "").strip()

    async def get_price(self) -> float:
        """Get item price as float."""
        text = await self.price.text_content()
        if text:
            return float(text.strip().replace("$", ""))
        return 0.0

    async def get_quantity(self) -> int:
        """Get item quantity."""
        text = await self.quantity.text_content()
        return int(text.strip()) if text else 0

    async def get_details(self) -> dict[str, str]:
        """Get all item details as dict."""
        return {
            "name": await self.get_name(),
            "description": (await self.description.text_content() or "").strip(),
            "price": (await self.price.text_content() or "").strip(),
            "quantity": (await self.quantity.text_content() or "").strip(),
        }

    async def remove(self) -> None:
        """Remove item from cart."""
        logger.debug(f"Removing from cart: {await self.get_name()}")
        await self.remove_button.click()


@dataclass
class PriceSummary:
    """Data class for checkout price summary."""
    subtotal: float
    tax: float
    total: float

    def verify_calculation(self) -> bool:
        """Verify total equals subtotal + tax."""
        expected = round(self.subtotal + self.tax, 2)
        actual = round(self.total, 2)
        return expected == actual
