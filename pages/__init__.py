from pages.base_page import HEADER_LINKS, MENU_LINKS, BasePage
from pages.cart_page import CartPage
from pages.catalog_page import CatalogPage
from pages.content_pages import AboutPage, BlogPage
from pages.home_page import HomePage
from pages.login_page import LoginPage
from pages.product_page import ProductPage
from pages.register_page import RegisterPage
from pages.search_page import SearchPage

__all__ = [
    "HEADER_LINKS", "MENU_LINKS", "BasePage", "HomePage", "CatalogPage", "ProductPage",
    "CartPage", "SearchPage", "LoginPage", "RegisterPage", "AboutPage", "BlogPage",
]
