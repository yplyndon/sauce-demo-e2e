import re

import pytest
from playwright.sync_api import expect

from config.settings import settings
from utils.helpers import unique_email

pytestmark = [pytest.mark.regression, pytest.mark.functional]


@pytest.mark.smoke
def test_registration_form_is_displayed(register_page):
    register_page.open()
    for name in ("first_name", "last_name", "email", "password"):
        expect(register_page.field(name)).to_be_visible()
    expect(register_page.submit).to_be_visible()


def _assert_no_account_created(register_page):
    """hCaptcha guards the form, so inline validation text is not guaranteed.
    Contract: the user stays on 'Create Account' and no session exists."""
    expect(register_page.heading).to_be_visible()
    register_page.page.goto("/account")
    expect(register_page.page).to_have_url(re.compile(r"/account/login"))


@pytest.mark.negative
def test_submitting_empty_registration_form_is_rejected(register_page):
    register_page.open()
    register_page.fill_and_submit()
    if register_page.hit_bot_challenge():
        pytest.skip("Shopify showed a bot challenge")
    _assert_no_account_created(register_page)


@pytest.mark.negative
def test_registration_with_invalid_email_is_rejected(register_page):
    register_page.open()
    register_page.fill_and_submit("Test", "User", "not-an-email", "Str0ng-Passw0rd!")
    if register_page.hit_bot_challenge():
        pytest.skip("Shopify showed a bot challenge")
    _assert_no_account_created(register_page)


@pytest.mark.skipif(
    not settings.allow_registration,
    reason="Creates a real customer on the demo store. Set ALLOW_REGISTRATION=true to enable.",
)
def test_new_customer_can_register(register_page):
    register_page.open()
    register_page.fill_and_submit("QA", "Automation", unique_email(), "Str0ng-Passw0rd!")
    if register_page.hit_bot_challenge():
        pytest.skip("Shopify showed a bot challenge")
    expect(register_page.page).to_have_url(re.compile(r"/account$"))
