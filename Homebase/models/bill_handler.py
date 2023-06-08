import selenium
import time
import re
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime, date
from dateutil.relativedelta import relativedelta

from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

from models.mongo_handler import MongoHandler


class BillHandler:
    def __init__(self):
        self.basic_fit_handler = BasicFitHandler()
        self.orange_handler = OrangeHandler()
        self.csn_handler = CSNHandler()

    def get_dates(self):
        basic_fit_dates = self.basic_fit_handler.get_dates()
        orange_dates = self.orange_handler.get_dates()
        csn_dates = self.csn_handler.get_dates()

        return basic_fit_dates + orange_dates + csn_dates


class PageHandlerParent:
    def __init__(self):
        self.mongo_handler = MongoHandler()
        self.page = None

    def str_to_date(self, str):
        split_str = str.split("-")
        return date(int(split_str[0]), int(split_str[1]), int(split_str[2]))

    def get_date_from_db(self):
        bills = self.mongo_handler.get_bills()
        return bills.get(self.page)

    def get_dates(self):
        today = datetime.today().date()
        dates = self.get_date_from_db()

        current_month_bills = []

        budget_icons = self.mongo_handler.get_budget_icons()

        for date, amount in dates.items():
            formated_date = self.str_to_date(date)
            if formated_date.month == today.month and formated_date > today:
                current_month_bills.append(
                    {"page": self.page, "date": date,
                     "amount": amount, "icon": budget_icons.get(self.page)})
        return current_month_bills


class BasicFitHandler(PageHandlerParent):
    def __init__(self):
        super().__init__()
        self.email = "elajsen.mattson@gmail.com"
        self.pswrd = "Qtepa112"
        self.amount = 19.99

        self.page = "basic-fit"

    def get_driver(self, headless):
        chrome_options = webdriver.ChromeOptions()

        if headless:
            chrome_options.add_argument("--headless=new")

        chrome_options.add_argument("--icognito")
        chrome_options.add_argument(
            '--disable-blink-features=AutomationControlled')

        driver = webdriver.Chrome(
            ChromeDriverManager().install(), chrome_options=chrome_options)
        return driver

    def get_date(self):
        self.driver.get("https://my.basic-fit.com/payments")

        nota_sig_el = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, "//h3[text()='Nota siguiente']"))
        )

        p_els = WebDriverWait(nota_sig_el, 10).until(
            EC.presence_of_element_located((By.XPATH, "..//p"))
        )
        p_els = nota_sig_el.find_elements(by=By.XPATH, value="..//p")

        for p in p_els:
            html = p.get_attribute("innerHTML")
            res = re.findall("[0-9]{2}-[0-9]{2}-[0-9]{4}", html)
            if len(res) > 0:
                date = res[0]
                break
            else:
                print(f"Couldnt find the date {html}")
        self.driver.quit()

        split_date = date.split("-")
        form_date = split_date[-1] + "-" + \
            split_date[-2] + "-" + split_date[-3]
        return form_date

    def log_in(self, email, pswrd):
        try:
            element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(
                    (By.XPATH, "//button[text()='Allow all cookies']"))
            )
            element.click()
        except:
            print("Couldn't turn on cookies")

        email_input = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, "//input[@name='email']"))
        )
        pswrd_input = self.driver.find_element(
            by=By.XPATH, value="//input[@name='password']")

        email_input.send_keys(email)
        pswrd_input.send_keys(pswrd)

        sub_btn = self.driver.find_element(
            by=By.XPATH, value="//button[@type='submit']")
        self.driver.execute_script(
            "window.scrollTo(0, document.body.scrollHeight);")

        sub_btn.click()
        time.sleep(2)

    def get_basic_fit_date(self):
        self.driver = self.get_driver(True)

        self.driver.get("https://my.basic-fit.com/")

        self.log_in(self.email, self.pswrd)

        date = self.get_date()
        return {date: self.amount}


class OrangeHandler(PageHandlerParent):
    def __init__(self):
        super().__init__()
        self.username = "651015507"
        self.pswrd = "Qtepa112"
        self.amount = 15

        self.page = "orange"

    def get_driver(self, headless):
        chrome_options = webdriver.ChromeOptions()

        if headless:
            chrome_options.add_argument("--headless=new")

        chrome_options.add_argument("--icognito")
        chrome_options.add_argument(
            '--disable-blink-features=AutomationControlled')

        driver = webdriver.Chrome(
            ChromeDriverManager().install(), chrome_options=chrome_options)
        return driver

    def log_in(self, username, pswrd):
        element = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, "//div[@id='consent_prompt_submit']"))
        )
        element.click()
        user_el = self.driver.find_element(
            by=By.XPATH, value="//input[@placeholder='Usuario']")
        pswrd_el = self.driver.find_element(
            by=By.XPATH, value="//input[@placeholder='Contraseña']")

        user_el.send_keys(username)
        pswrd_el.send_keys(pswrd)

        self.driver.find_element(
            by=By.XPATH, value="//button[@type='submit']").click()

    def get_date(self):
        self.driver.get("https://areaprivada.orange.es/soycliente/mi-linea")

        element = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, "//div[@class='tariff-renewal-date']"))
        )
        html = element\
            .find_element(by=By.TAG_NAME, value="p").get_attribute("innerHTML")

        date = re.findall("[0-9]{2}/[0-9]{2}/[0-9]{4}", html)
        split_date = date[0].split("/")
        format_date = split_date[-1] + "-" + \
            split_date[-2] + "-" + split_date[-3]
        self.driver.quit()
        return format_date

    def get_orange_date(self):
        self.driver = self.get_driver(True)
        self.driver.get("https://areaprivada.orange.es")

        self.log_in(self.username, self.pswrd)

        date = self.get_date()
        return {date: self.amount}


class CSNHandler(PageHandlerParent):
    def __init__(self):
        super().__init__()
        self.page = "csn"

    def get_csn_dates(self):
        return {
            "2023-08-31": 3953,
            "2023-11-30": 3953
        }
