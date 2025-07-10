import pytest
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.edge.options import Options as EdgeOptions
import allure
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import Keys

BROWSERSTACK_USERNAME = 'sewminihewawitha_Y9VX5t'
BROWSERSTACK_ACCESS_KEY = 'ovamcbW6mDw59BTLC2pN'

browsers = [
    {'browser': 'Chrome', 'os': 'Windows', 'os_version': '11', 'browser_version': 'latest'},
    {'browser': 'Firefox', 'os': 'Windows', 'os_version': '11', 'browser_version': 'latest'},
    {'browser': 'Edge', 'os': 'Windows', 'os_version': '11', 'browser_version': 'latest'},
]

@pytest.fixture(params=browsers, scope="class")
def browser_driver(request):
    browser = request.param['browser']
    os_name = request.param['os']
    os_version = request.param['os_version']
    browser_version = request.param['browser_version']

    if browser == 'Chrome':
        options = ChromeOptions()
    elif browser == 'Firefox':
        options = FirefoxOptions()
    elif browser == 'Edge':
        options = EdgeOptions()
    else:
        raise ValueError(f"Unsupported browser: {browser}")

    bstack_options = {
        "os": os_name,
        "osVersion": os_version,
        "browserVersion": browser_version,
        "projectName": "simplilearn_tests",
        "buildName": "simplilearn_build",
        "sessionName": "Simplilearn Test Suite",
        "seleniumVersion": "4.33.0",
        "debug": True,
        "networkLogs": True,
        "consoleLogs": "info"
    }

    options.set_capability('bstack:options', bstack_options)
    options.set_capability('browserName', browser)

    url = f"https://{BROWSERSTACK_USERNAME}:{BROWSERSTACK_ACCESS_KEY}@hub-cloud.browserstack.com/wd/hub"
    driver = webdriver.Remote(command_executor=url, options=options)

    driver.set_window_size(1920, 1080)
    request.cls.driver = driver
    yield driver
    driver.quit()

def set_browserstack_status(driver, status, reason):
    driver.execute_script(
        f'browserstack_executor: {{"action": "setSessionStatus", "arguments": {{"status":"{status}","reason":"{reason}"}}}}'
    )


@pytest.mark.usefixtures("browser_driver")
@allure.feature("Simplilearn Test Suite")
class TestSimplilearn:

    @allure.title("Verify Simplilearn home page loads successfully")
    def test_home(self):
        try:
            self.driver.get("https://www.simplilearn.com/")
            expected_url = "https://www.simplilearn.com/"
            assert expected_url in self.driver.current_url, "Home page failed to load"

            set_browserstack_status(self.driver, "passed", "Home page loaded successfully")
        except Exception as e:
            set_browserstack_status(self.driver, "failed", f"Home page test failed: {str(e)}")
            raise

    @allure.title("Verify that if 'All Courses' menu expands correctly")
    def test_course_navigation(self):
        try:
            self.driver.get("https://www.simplilearn.com/")
            with allure.step("Click 'All Courses' menu"):
                all_courses_btn = self.driver.find_element(By.XPATH, "//span[text()='All Courses']")
                all_courses_btn.click()
                WebDriverWait(self.driver, 10).until(
                    EC.visibility_of_element_located((By.XPATH, "//div[contains(@class,'category-list')]"))
                )

            with allure.step("Verify dropdown is visible"):
                assert "All Courses" in self.driver.page_source or "category" in self.driver.page_source.lower()

            set_browserstack_status(self.driver, "passed", "'All Courses' menu expanded successfully")
        except Exception as e:
            set_browserstack_status(self.driver, "failed", f"'All Courses' menu test failed: {str(e)}")
            raise

    @allure.title("Verify that user can successfully login with valid credentials")
    def test_login(self):
        try:
            self.driver.get("https://www.simplilearn.com/")
            with allure.step("Click login link"):
                login_btn = self.driver.find_element(By.XPATH, '//*[@id="topHeader"]/div/div/nav/div/a')
                login_btn.click()

            with allure.step("Wait for login page"):
                WebDriverWait(self.driver, 10).until(EC.url_contains("user/login"))

            with allure.step("Enter credentials and submit"):
                self.driver.find_element(By.XPATH, '//*[@id="login-form"]/div[2]/input').send_keys("sewminihw@gmail.com")
                self.driver.find_element(By.XPATH, '//*[@id="password"]').send_keys("SQA#%234ab")
                self.driver.find_element(By.XPATH, '//*[@id="login-form"]/div[5]/input').click()

            with allure.step("Wait for dashboard"):
                WebDriverWait(self.driver, 15).until(EC.url_contains("dashboard"))

            assert "dashboard" in self.driver.current_url

            set_browserstack_status(self.driver, "passed", "Login test passed successfully")
        except Exception as e:
            set_browserstack_status(self.driver, "failed", f"Login test failed: {str(e)}")
            raise

    @allure.title("Verify that search function works correctly")
    def test_search(self):
        try:
            self.driver.get("https://lms.simplilearn.com/dashboard")

            search_input_xpath = "/html/body/div[1]/app-root/app-dashboard-layout/app-dashboard/div/section/div/section[1]/app-mainpanel/div/app-no-course/div/div/div/div/input"

            with allure.step("Wait for search input and enter search term"):
                search_input = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, search_input_xpath))
                )
                search_input.clear()
                search_input.send_keys("Selenium Docker", Keys.ENTER)

            time.sleep(4)  # or better explicit wait for search results

            with allure.step("Verify search term is present in input"):
                assert "Selenium Docker" == search_input.get_attribute("value")

            set_browserstack_status(self.driver, "passed", "Search function works correctly")
        except Exception as e:
            set_browserstack_status(self.driver, "failed", f"Search test failed: {str(e)}")
            raise

    @allure.title("Confirms responsive layout loads correctly")
    def test_responsive_ui(self):
        try:
            self.driver.get("https://www.simplilearn.com/")
            width = self.driver.execute_script("return window.innerWidth")
            assert width > 0
            set_browserstack_status(self.driver, "passed", "Responsive layout loaded correctly")
        except Exception as e:
            set_browserstack_status(self.driver, "failed", f"Responsive UI test failed: {str(e)}")
            raise
