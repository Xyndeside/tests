import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions


def _chrome_options() -> ChromeOptions:
    opts = ChromeOptions()
    opts.add_argument("--headless=new")
    opts.add_argument("--lang=ru-RU")
    opts.add_argument("--force-device-scale-factor=1")
    opts.add_argument("--hide-scrollbars")
    opts.add_argument("--disable-gpu")
    opts.add_experimental_option(
        "prefs",
        {"intl.accept_languages": "ru-RU,ru"},
    )
    return opts


@pytest.fixture
def browser():
    driver = webdriver.Chrome(options=_chrome_options())
    driver.set_window_size(1920, 1080)
    yield driver
    driver.quit()
