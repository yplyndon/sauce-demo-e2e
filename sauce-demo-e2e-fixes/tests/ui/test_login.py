import re

import pytest
from playwright.sync_api import expect

from config.settings import settings
from utils.helpers import unique_email

pytestmark = [pytest.mark.regression, pytest.mark.functional]


@pytest.mark.smoke
def test_login_form_is_displayed(login_page):
    login_page.open()
    expect(login_page.email).to_be_visible()
    expect(login_page.password).to_be_visible()
    expect(login_page.submit).to_be_visible()


def _assert_no_session_created(login_page):
    """The store is protected by hCaptcha, so an inline error message is not guaranteed.
    The reliable contract is: the user stays on the login form and no session exists."""
    expect(login_page.heading).to_be_visible()
    expect(login_page.page).not_to_have_url(re.compile(r"/account$"))
    login_page.page.goto("/account")
    expect(login_page.page).to_have_url(re.compile(r"/account/login"))


@pytest.mark.negative
def test_login_with_unknown_account_is_rejected(login_page):
    login_page.open()
    login_page.login(unique_email("nobody"), "Wrong-Password-123")
    if login_page.hit_bot_challenge():
        pytest.skip("Shopify showed a bot challenge")
    _assert_no_session_created(login_page)


@pytest.mark.negative
def test_login_with_empty_fields_is_rejected(login_page):
    login_page.open()
    login_page.login("", "")
    if login_page.hit_bot_challenge():
        pytest.skip("Shopify showed a bot challenge")
    _assert_no_session_created(login_page)


@pytest.mark.negative
def test_account_page_redirects_guests_to_login(page):
    page.goto("/account")
    expect(page).to_have_url(re.compile(r"/account/login"))


def test_forgot_password_reveals_recovery_form(login_page):
    login_page.open()
    login_page.forgot_password_link.click()
    expect(login_page.recover_email).to_be_visible()


@pytest.mark.skipif(
    not (settings.test_user_email and settings.test_user_password),
    reason="Set TEST_USER_EMAIL / TEST_USER_PASSWORD in .env to run the positive login test",
)
def test_valid_customer_can_log_in(login_page):
    login_page.open()
    login_page.login(settings.test_user_email, settings.test_user_password)
    if login_page.hit_bot_challenge():
        pytest.skip("Shopify showed a bot challenge")
    expect(login_page.page).to_have_url(re.compile(r"/account$"))
