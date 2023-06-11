import selenium
import time
import re
import pandas as pd
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from django.conf import settings

from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait


class BBVAScraper:
    def __init__(self, headless=False):
        self.headless = headless
        self.username = settings.CREDENTIALS["bbva"]["username"]
        self.pswrd = settings.CREDENTIALS["bbva"]["password"]

        self.month_translation_dict = {
            "DIC": 12,
            "NOV": 11,
            "OCT": 10,
            "SEP": 9,
            "AGO": 8,
            "JUL": 7,
            "JUN": 6,
            "MAY": 5,
            "ABR": 4,
            "MAR": 3,
            "FEB": 2,
            "ENE": 1
        }

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

    def get_dates(self):
        dates = []

        current = datetime.today().date().replace(day=1)

        dates.append({
            "start": current,
            "end": datetime.today().date()
        })

        for i in range(1, 13):
            dates.append({
                "start": current - relativedelta(months=i),
                "end": current - relativedelta(months=i - 1) - relativedelta(days=1)
            })
        return dates

    def find_element_with_wait(self, by=None, value=None):
        element = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((by, value))
        )
        return element

    def find_elements_with_wait(self, by=None, value=None):
        element = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((by, value))
        )
        elements = self.driver.find_elements(by=by, value=value)
        return elements

    # ------ MISC FUNCTIONS --------
    def convert_date(self, date):
        split_string = str(date).split("-")
        formated_date = split_string[-1] + "/" + \
            split_string[-2] + "/" + split_string[-3]
        return formated_date

    def get_item_by_text(self, text):
        item = self.driver.find_elements_by_xpath(
            xpath=f"//*[contains(text(), '{text}')]")[0]
        return item

    def find_item_by_xpath_custom(self, tag, attribute, text):
        return self.driver.find_element_by_xpath(xpath=f"//{tag}[@{attribute}='{text}']").click()

    # ----- WEBPAGE NAVIGATION -------
    def switch_to_iframe(self):
        iframe = self.driver.find_elements_by_tag_name("iframe")
        self.driver.switch_to.frame(iframe[0])

    def switch_to_default(self):
        self.driver.switch_to.default_content()

    def close_modal(self):
        self.find_element_with_wait(By.XPATH,
                                    "//span[@id='entendido']").click()

    def get_date_from_mov_element(self, mov_element):
        date_el = mov_element.find_element(by=By.XPATH, value=".//div[@class='contieneFechas']")\
            .find_element(by=By.TAG_NAME, value="b")

        span_elements = date_el.find_elements(by=By.TAG_NAME, value="span")
        day = int(span_elements[0].get_attribute("innerHTML")
                  .replace(" ", ""))

        if len(span_elements) > 1:
            year = int(span_elements[1].get_attribute("innerHTML")
                       .replace(" ", ""))
        else:
            year = datetime.today().year

        month_regex = "[A-Z]{3}."
        month = re.findall(month_regex, date_el.get_attribute("innerHTML"))[
            0].replace(".", "")
        month = self.month_translation_dict.get(month)

        return date(year, month, day)

    def get_category_from_mov_element(self, mov_element):
        category = mov_element.find_element(by=By.XPATH, value=".//td[@role='gridcell']")\
            .find_element(by=By.XPATH, value=".//i[@role='img']").get_attribute("aria-label")
        return category

    def get_amount_from_mov_element(self, mov_element):
        amount = mov_element.find_element(by=By.XPATH, value=".//span[@class='mensaje']").get_attribute("innerHTML")\
            .replace(" ", "").replace("€", "")
        return amount

    def get_data_from_mov_element(self, mov_element):
        date = self.get_date_from_mov_element(mov_element)

        category = self.get_category_from_mov_element(mov_element)

        amount = self.get_amount_from_mov_element(mov_element)

        return {
            "date": str(date),
            "category": category,
            "amount": amount
        }

    def log_in(self):
        # Cookies
        self.get_item_by_text("Aceptar").click()

        time.sleep(2)
        # Acceso
        self.get_item_by_text("Acceso").click()

        time.sleep(2)
        self.switch_to_iframe()

        time.sleep(1)
        el = self.driver.find_elements_by_tag_name("input")

        el[0].send_keys(self.username)
        el[1].send_keys(self.pswrd)

        self.get_item_by_text("Entrar").click()

    def go_to_categories(self):
        start = self.driver.current_url.split("#")[0]
        self.driver.get(start + "#dashboard/pfm/gastos")

    def go_to_movements(self):
        start = self.driver.current_url.split("#")[0]
        self.driver.get(start + "#cuentas/1/ficha")

    def get_movements_from_page(self):
        tbody = self.find_element_with_wait(by=By.TAG_NAME, value="tbody")
        movement_elements = tbody.find_elements(
            by=By.XPATH, value=".//tr[@role='row']")
        return movement_elements

    def filter_dates(self, date_from, date_until):
        btn = self.driver.find_elements_by_xpath("//div[@id='dateSimulationContainer']")[0]\
            .find_element_by_tag_name("i")
        time.sleep(1)
        btn.click()

        inputs = self.driver.find_elements_by_xpath(
            "//input[@aria-required='true']")
        desde = inputs[0]
        hasta = inputs[1]

        desde.clear()
        hasta.clear()

        desde.send_keys(date_from)
        hasta.send_keys(date_until)
        time.sleep(2)

        btn = self.driver.find_element_by_xpath(
            "//span[text()[contains(., 'Filtrar por fecha')]]")
        btn.click()
        try:
            btn.click()
        except:
            pass

    def get_category_information(self):
        def string_to_float(string):
            edited_string = string.replace(".", "").replace(",", ".")
            res = re.findall("[\d]{1,10}.[\d]{1,2}", edited_string)
            return float(res[0])

        def get_income():
            amount_divs = self.find_elements_with_wait(By.XPATH,
                                                       "//div[contains(@class, 'tableTotalAmounts')]")
            to_check = 1
            amount_divs[to_check].find_element_by_tag_name(
                "dt").get_attribute("innerHTML")
            amount = amount_divs[to_check].find_element_by_tag_name("dd")\
                .find_element_by_xpath(".//span[@class='sr-only']").get_attribute("innerHTML")
            cleaned_amount = amount.replace(
                ".", "").replace(",", ".").replace("€", "")
            return float(cleaned_amount)

        res = {}
        category_cards = self.find_elements_with_wait(
            by=By.XPATH,
            value="//div[@data-cy-id='card-icon']")

        for card in category_cards:
            category = card.find_element_by_tag_name(
                "h3").get_attribute("innerHTML")
            amt_card = card.find_element_by_xpath(
                xpath=".//span[@data-cy-id='data-amount']")
            amount = amt_card.find_element_by_xpath(
                xpath=".//span[@class='sr-only']").get_attribute("innerHTML")
            res[category] = string_to_float(amount)
        # res["other income"] = get_income() - res.get("Nómina", 0)
        return res

    def get_current_month_categories(self):
        self.driver = self.get_driver(self.headless)
        self.driver.get("https://www.bbva.es/")

        self.log_in()

        tries = 0
        continue_ = True
        while continue_:
            try:
                self.switch_to_default()

                self.close_modal()

                continue_ = False
            except:
                if tries > 4:
                    continue_ = False

                time.sleep(2)
                tries += 1

        self.go_to_categories()

        categories = self.get_category_information()

        self.driver.quit()
        return categories

    def get_backlog_month_categories(self):
        self.driver = self.get_driver(self.headless)
        self.driver.get("https://www.bbva.es/")

        self.log_in()

        tries = 0
        continue_ = True
        while continue_:
            try:
                self.switch_to_default()

                self.close_modal()

                continue_ = False
            except:
                if tries > 4:
                    continue_ = False

                time.sleep(2)
                tries += 1

        self.go_to_categories()

        dates = self.get_dates()

        res_dict = []
        for date in dates:
            start, end = self.convert_date(
                date.get("start")), self.convert_date(date.get("end"))
            self.filter_dates(start, end)
            time.sleep(2)

            temp = self.get_category_information()
            temp["date"] = str(date.get("start"))
            res_dict.append(temp)

        self.driver.quit()

        return res_dict

    def get_most_recent_movements(self):
        self.driver = self.get_driver(self.headless)
        self.driver.get("https://www.bbva.es/")

        self.log_in()

        self.go_to_movements()

        movement_elements = self.get_movements_from_page()

        data = []
        columns = ["date", "category", "amount"]
        for mov in movement_elements:
            mov_data = self.get_data_from_mov_element(mov)

            data.append([mov_data.get("date"), mov_data.get(
                "category"), mov_data.get("amount")])

        return pd.DataFrame(data, columns=columns)
