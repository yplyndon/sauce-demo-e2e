import re

import pytest
from playwright.sync_api import expect

pytestmark = [pytest.mark.regression, pytest.mark.functional]


def test_about_page_content(about_page):
    response = about_page.open()
    assert response is not None and response.ok
    expect(about_page.page.get_by_text(re.compile("demo site created for", re.I)).first).to_be_visible()


def test_blog_page_loads(blog_page):
    response = blog_page.open()
    assert response is not None and response.ok
    expect(blog_page.logo).to_be_visible()


def test_footer_about_blurb_and_copyright(home_page):
    home_page.open()
    expect(home_page.footer_about_text).to_be_visible()
    expect(home_page.copyright_notice).to_be_visible()


def test_footer_shows_accepted_payment_methods(home_page):
    home_page.open()
    expect(home_page.payment_icons).to_have_count(3)
    for brand in ("Amex", "Visa", "Mastercard"):
        expect(home_page.page.get_by_role("img", name=f"We accept {brand}")).to_be_visible()


@pytest.mark.parametrize("domain", ["facebook.com", "twitter.com", "instagram.com", "pinterest.com"])
def test_social_links_are_present(home_page, domain):
    home_page.open()
    assert home_page.page.locator(f"a[href*='{domain}']").count() >= 1


def test_blog_rss_feed_link_is_present(home_page):
    home_page.open()
    assert home_page.page.locator("a[href$='/blogs/news.atom']").count() >= 1
