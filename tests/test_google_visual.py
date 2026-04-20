import os

import allure
import imagehash
import pytest
from PIL import Image, ImageChops
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

os.makedirs("baselines", exist_ok=True)
os.makedirs("diffs", exist_ok=True)

GOOGLE_URL = "https://www.google.com/?hl=ru&gl=RU"

_CONSENT_BUTTON_XPATHS = [
    "//button[contains(., 'Принять все')]",
    "//button[contains(., 'Accept all')]",
    "//div[@role='button'][contains(., 'Принять все')]",
    "//div[@role='button'][contains(., 'Accept all')]",
    "//button[contains(., 'Отклонить все')]",
    "//button[contains(., 'Reject all')]",
]


def _click_consent_in_current_context(driver) -> bool:
    for xp in _CONSENT_BUTTON_XPATHS:
        try:
            for el in driver.find_elements(By.XPATH, xp):
                if el.is_displayed():
                    el.click()
                    return True
        except Exception:
            continue
    return False


def _dismiss_google_consent(driver) -> bool:
    driver.switch_to.default_content()
    if _click_consent_in_current_context(driver):
        return True
    frames = driver.find_elements(By.TAG_NAME, "iframe")
    for fr in frames:
        try:
            driver.switch_to.default_content()
            driver.switch_to.frame(fr)
            if _click_consent_in_current_context(driver):
                return True
        except Exception:
            pass
        finally:
            driver.switch_to.default_content()
    return False


def _open_google_ready(driver) -> None:
    driver.get(GOOGLE_URL)
    wait = WebDriverWait(driver, 25)
    last = None
    for _ in range(8):
        _dismiss_google_consent(driver)
        try:
            wait.until(lambda d: d.execute_script("return document.readyState") == "complete")
        except TimeoutException:
            pass
        try:
            WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located(
                    (By.CSS_SELECTOR, "textarea[name='q'], input[name='q']")
                )
            )
            return
        except TimeoutException as e:
            last = e
            continue
    raise TimeoutException(
        "Не появилась строка поиска Google. Закройте окно согласия вручную в сценарии или проверьте сеть."
    ) from last


def _attach_png(path: str, name: str) -> None:
    if os.path.isfile(path):
        allure.attach.file(
            path,
            name=name,
            attachment_type=allure.attachment_type.PNG,
        )


@allure.feature("Визуальное тестирование")
@allure.story("Google: полная страница и элемент интерфейса")
@allure.title("Регрессия UI google.com (perceptual hash)")
def test_google_ui_fullpage(browser):
    base = "baselines/google.png"
    curr = "diffs/google_current.png"
    diff = "diffs/google_diff.png"

    with allure.step("Открыть Google: согласие (cookies), затем главная со строкой поиска"):
        _open_google_ready(browser)

    with allure.step("Сохранить скриншот страницы"):
        browser.get_screenshot_as_file(curr)
        _attach_png(curr, "Текущий скриншот (полная страница)")

    if not os.path.exists(base):
        os.replace(curr, base)
        _attach_png(base, "Эталон создан (baseline)")
        pytest.skip("Эталон готов — повторите запуск для сравнения")

    with allure.step("Сравнить с эталоном (phash)"):
        img_1 = Image.open(base).convert("RGB")
        img_2 = Image.open(curr).convert("RGB")
        hash_1 = imagehash.phash(img_1)
        hash_2 = imagehash.phash(img_2)
        delta = hash_1 - hash_2
        allure.attach(
            str(delta),
            name="Разница хешей (phash)",
            attachment_type=allure.attachment_type.TEXT,
        )

    if delta > 5:
        diff_img = ImageChops.difference(img_1, img_2)
        diff_img.save(diff)
        _attach_png(base, "Эталон")
        _attach_png(curr, "Текущий")
        _attach_png(diff, "Разница (ImageChops.difference)")
        assert False, f"Обнаружено отличие UI (см. {diff})"


@allure.feature("Визуальное тестирование")
@allure.story("Элемент интерфейса: область поиска")
@allure.title("Скриншот элемента — форма поиска Google")
def test_google_search_form_element(browser):
    _open_google_ready(browser)
    wait = WebDriverWait(browser, 15)

    with allure.step("Найти форму поиска и сделать скриншот элемента"):
        el = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "textarea[name='q'], input[name='q']"))
        )

        path = "diffs/google_search_form.png"
        el.screenshot(path)
        _attach_png(path, "Элемент: поле поиска")

    assert os.path.isfile(path), "Не удалось сохранить скриншот элемента"
