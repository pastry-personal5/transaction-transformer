import time
import yaml

from loguru import logger

import requests
import selenium
from selenium import common as SC
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from simple_portfolio import SimplePortfolio


class WebClientContext:
    driver = None  # It's a Selenium driver.

    def __init__(self):
        self.driver = None

    def cleanup(self):
        if self.driver:
            self.driver.quit()


class YahooFinanceWebExporter:

    def __init__(self):
        self.web_client_context = None
        self.user_id = None
        self.user_password = None

    def prepare_export(self):
        driver = webdriver.Chrome()
        const_amount_time_to_wait_in_sec = 0.5
        driver.implicitly_wait(const_amount_time_to_wait_in_sec)
        self.web_client_context = WebClientContext()
        self.web_client_context.driver = driver
        user_id = self.user_id
        user_password = self.user_password
        self.visit_login_page(user_id, user_password)

    def read_config(self, config_filepath):
        try:
            config_file = open(config_filepath, 'rb')
            config = yaml.safe_load(config_file)
            self.user_id = config['yahoo_account']['id']
            self.user_password = config['yahoo_account']['password']
            return True
        except IOError as e:
            logger.error('IOError.', e)
            logger.error('Configuration filepath was: %s' % config_filepath)
            return False

    def verify_config(self):
        if not self.user_id or len(self.user_id) == 0:
            return False
        if not self.user_password or len(self.user_password) == 0:
            return False
        return True

    def export_simple_portfolio(self, portfolio: SimplePortfolio):
        return True

    def cleanup(self):
        if self.web_client_context:
            self.web_client_context.cleanup()

    def visit_login_page(self, user_id, user_password):
        '''
        Please note that word "id" can be "user name", "username", etc. in Yahoo Web Pages.
        Please note that word "password" can be "passwd", "pw", etc. in Yahoo Web Pages.
        '''
        driver = self.web_client_context.driver

        # It's the yahoo.com main page.
        logger.info('Visiting Yahoo Fiance...')
        driver.get('https://finance.yahoo.com/portfolios/')
        const_time_to_wait = 4
        WebDriverWait(driver, const_time_to_wait).until(
            EC.presence_of_element_located((By.ID, 'login-container'))
        )
        element_for_login_container = driver.find_element(by=By.ID, value='login-container')
        element_for_login_container.click()

        # It's now in a kind of "login-sign-in" page.
        logger.info('Visiting a kind of "login-sign-in" page...')
        WebDriverWait(driver, const_time_to_wait).until(
            EC.presence_of_element_located((By.ID, 'login-username'))
        )

        # Enter user name in an HTML 'form,' then click 'Next' button.
        element_for_login_user_name = driver.find_element(by=By.ID, value='login-username')
        element_for_login_sign_in_button = driver.find_element(by=By.ID, value='login-signin')
        element_for_login_user_name.send_keys(user_id)
        time.sleep(const_time_to_wait)
        element_for_login_sign_in_button.click()

        # It's now in a kind of "enter-your-password" page.
        logger.info('Visiting a kind of "enter-your-password" page...')
        WebDriverWait(driver, const_time_to_wait).until(
            EC.presence_of_element_located((By.ID, 'login-passwd'))
        )

        logger.info('Sending a password text and a mouse click event...')
        element_for_login_password = driver.find_element(by=By.ID, value='login-passwd')
        element_for_login_sign_in_button = driver.find_element(by=By.ID, value='login-signin')
        element_for_login_password.send_keys(user_password)
        time.sleep(const_time_to_wait)
        element_for_login_sign_in_button.click()

        # It's now in a kind of "remember-me" page.
        # by=By.NAME, 'rememberMe'
        # It shows "Stay Verified."
        logger.info('Visiting a kind of "remember-me" page...')

        # Let's try to locate a <div> with an "id."
        try:
            WebDriverWait(driver, const_time_to_wait).until(
                EC.presence_of_element_located((By.ID, 'challenge-header'))
            )
        except selenium.common.exceptions.TimeoutException:
            logger.info('Skipping challenge-header <div> element.')
        element_for_remember_me_button = driver.find_element(by=By.NAME, value='rememberMe')  # <button>
        element_for_remember_me_button.click()

        # It's now a kind of "input two-step-auth verification code" page.
        logger.info('Visiting a kind of "input two-step-auth verification code" page...')
        WebDriverWait(driver, const_time_to_wait).until(
            EC.presence_of_element_located((By.ID, 'verification-code-field'))
        )

        print('Input your two step authentication code using your web browser...')
        print('Then')

        self.wait_for_page_load()

    def wait_for_page_load(self):
        while True:
            print('Input \'c\' to continue: ')
            input_from_user = input()
            if input_from_user == 'c':
                return
