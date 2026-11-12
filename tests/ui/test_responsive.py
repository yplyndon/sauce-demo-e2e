import pytest
from playwright.sync_api import expect

from testdata import PRODUCTS

pytestmark = [pytest.mark.regression, pytest.mark.responsive]

VIEWPORTS = {
    "mobile": {"width": 375, "height": 812},
    "tablet": {"width": 768, "height": 1024},
    "desktop": {"width": 1440, "height": 900},
}


@pytest.mark.parametrize("name", VIEWPORTS)
def test_home_page_renders_on_viewport(page, home_page, name):
    page.set_viewport_size(VIEWPORTS[name])
    home_page.open()
    expect(home_page.logo).to_be_visible()
    first = PRODUCTS[0]
    expect(home_page.product_card(first.handle, first.title)).to_be_visible()


@pytest.mark.parametrize("name", VIEWPORTS)
def test_home_page_has_no_horizontal_scroll(page, home_page, name):
    page.set_viewport_size(VIEWPORTS[name])
    home_page.open()
    overflow = page.evaluate("document.documentElement.scrollWidth - window.innerWidth")
    assert overflow <= 1, f"{name}: page overflows horizontally by {overflow}px"


@pytest.mark.parametrize("name", ["mobile", "tablet"])
def test_product_page_add_button_visible_on_small_screens(page, open_product, name):
    page.set_viewport_size(VIEWPORTS[name])
    pdp = open_product(PRODUCTS[0].handle)
    expect(pdp.add_button).to_be_visible()
