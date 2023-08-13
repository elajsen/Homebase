import selenium
import time
import re
import os
import platform
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
    def __init__(self, headless=True):
        self.headless = headless
        self.username = settings.CREDENTIALS["bbva"]["username"]
        self.pswrd = settings.CREDENTIALS["bbva"]["password"]

        self.logged_in = False

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

    def find_chromedriver_path(self):
        # Get the current directory path
        current_directory = os.getcwd()

        # Check if the "chromedriver" executable exists in the current directory
        chromedriver_filename = "chromedriver"
        chromedriver_path = os.path.join(
            current_directory, chromedriver_filename)

        if os.path.exists(chromedriver_path):
            return chromedriver_path
        else:
            return None

    def find_chrome_binary_path(self):
        system = platform.system()

        if system == "Windows":
            # Windows Chrome binary path
            program_files = os.environ.get("PROGRAMFILES", "C:\\Program Files")
            chrome_binary_path = os.path.join(
                program_files, "Google", "Chrome", "Application", "chrome.exe")
        elif system == "Darwin":
            # macOS Chrome binary path
            chrome_binary_path = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
        else:
            # Linux Chrome binary path
            # Or "/usr/bin/google-chrome-stable" for some distributions
            chrome_binary_path = "/usr/bin/google-chrome"

        return chrome_binary_path

    def get_driver(self, headless):
        chrome_options = webdriver.ChromeOptions()

        if headless:
            chrome_options.add_argument("--headless=new")

        chrome_options.add_argument("--icognito")
        chrome_options.add_argument(
            '--disable-blink-features=AutomationControlled')

        """
        driver = webdriver.Chrome(
            ChromeDriverManager().install(), chrome_options=chrome_options)
        """
        driver_route = self.find_chromedriver_path()
        chrome_options.binary_location = self.find_chrome_binary_path()
        # print(f"Driver Route: {driver_route}")
        driver = webdriver.Chrome(
            executable_path=driver_route, chrome_options=chrome_options
        )
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
        self.find_element_with_wait(
            by=By.TAG_NAME,
            value="iframe"
        )
        iframe = self.driver.find_elements_by_tag_name("iframe")
        try:
            assert False
            self.driver.switch_to.frame(iframe[0])
            print("switched to iframe")
        except:
            print("Couldn't switch to iframe")

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
        element_month_text = date_el.get_attribute("innerHTML")
        month = re.findall(month_regex, element_month_text)[
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

    def get_concept_from_mov_element(self, mov_element):
        concept = mov_element\
            .find_element(by=By.CLASS_NAME,
                          value="concepto")\
            .get_attribute("innerHTML")
        return concept.strip()

    def get_description_from_mov_element(self, mov_element):
        description = mov_element\
            .find_element(by=By.XPATH,
                          value="//div[@class='descripcionEspecifica']")\
            .find_element(by=By.TAG_NAME,
                          value="b")\
            .get_attribute("innerHTML")
        return description.strip()

    def get_data_from_mov_element(self, mov_element):

        id = mov_element.get_attribute("data-movement-id")
        date = self.get_date_from_mov_element(mov_element)
        category = self.get_category_from_mov_element(mov_element)
        amount = self.get_amount_from_mov_element(mov_element)
        concept = self.get_concept_from_mov_element(mov_element)
        description = self.get_description_from_mov_element(mov_element)

        return {
            "id": id,
            "date": str(date),
            "description": description,
            "concept": concept,
            "category": category,
            "amount": amount
        }

    def log_in(self):
        # Cookies
        if self.logged_in:
            return
        self.driver = self.get_driver(self.headless)
        self.driver.get("https://www.bbva.es/")
        try:
            self.find_element_with_wait(
                by=By.XPATH,
                value="//*[contains(text(), 'Aceptar')]"
            ).click()
            print("Accepted cookies")
        except:
            print("Couldn't find cookies accept")

        time.sleep(2)
        # Acceso
        # self.get_item_by_text("Acceso").click()
        self.find_element_with_wait(
            by=By.XPATH,
            value="//*[contains(text(), 'Acceso')]"
        ).click()

        time.sleep(2)
        self.switch_to_iframe()

        time.sleep(1)
        el = self.find_elements_with_wait(
            by=By.TAG_NAME,
            value="input")

        el[0].send_keys(self.username)
        el[1].send_keys(self.pswrd)

        btn = self.find_elements_with_wait(
            by=By.XPATH,
            value="//*[@data-lit-component='button']")[0]
        btn.click()

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

        self.logged_in = True

    def go_to_categories(self):
        if "#dashboard/pfm/gastos" in self.driver.current_url:
            return
        start = self.driver.current_url.split("#")[0]
        self.driver.get(start + "#dashboard/pfm/gastos")

    def go_to_movements(self):
        if "#cuentas/1/ficha" in self.driver.current_url:
            return
        start = self.driver.current_url.split("#")[0]
        self.driver.get(start + "#cuentas/1/ficha")

    def get_movements_from_page(self):
        tbody = self.find_element_with_wait(by=By.TAG_NAME, value="tbody")
        movement_elements = tbody.find_elements(
            by=By.XPATH, value=".//tr[@role='row']")
        return movement_elements

    def filter_dates(self, date_from, date_until):
        btn = self.find_element_with_wait(by=By.XPATH, value="//div[@id='dateSimulationContainer']")\
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

        res["other income"] = round(get_income() - res.get("Nómina", 0), 2)

        return res

    def filter_for_current_month(self):
        self.find_element_with_wait(by=By.XPATH,
                                    value="//span[@data-testid='consultas']").click()
        start_date = datetime.today().date().replace(day=1)
        end_date = datetime.today().date()

        if start_date == datetime.today().date():
            return

        formated_start_date = "/".join(str(start_date).split("-")[::-1])
        formated_end_date = "/".join(str(end_date).split("-")[::-1])

        start = self.find_element_with_wait(by=By.XPATH,
                                            value="//input[@name='filtros.fechas.inicio']")
        print(start)
        time.sleep(5)
        start.clear()
        start.send_keys(formated_start_date)

        end = self.find_element_with_wait(by=By.XPATH,
                                          value="//input[@name='filtros.fechas.fin']")
        end.clear()
        end.send_keys(formated_end_date)

        btn_span = self.find_element_with_wait(by=By.XPATH,
                                               value="//span[@data-testid='boton-buscar-movimiento']")
        btn_span.click()

    def scroll_to_show_all_movements(self):

        mostrar_mas = self.find_elements_with_wait(by=By.CLASS_NAME,
                                                   value="botonMostrarMas")

        while True:
            if len(mostrar_mas) > 0:
                self.driver.execute_script(
                    "arguments[0].scrollIntoView();", mostrar_mas[0])

                try:
                    mostrar_mas[0].click()
                except:
                    return

    def get_current_month_categories(self):

        self.log_in()

        self.go_to_categories()

        categories = self.get_category_information()

        self.go_to_movements()

        retentions = self.get_retentions()
        categories["Retentions"] = retentions

        # self.driver.quit()
        return categories

    def get_backlog_month_categories(self):
        self.log_in()

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

    def get_retentions(self):
        retention_element = self.find_element_with_wait(by=By.CLASS_NAME,
                                                        value="c-encabezado-descripcionProducto__retenciones-amount")

        retention = retention_element.get_attribute("innerHTML")\
            .replace("€", "").replace("-", "").replace(",", ".")
        print(f"retention: {float(retention)}")
        return float(retention)

    def get_most_recent_movements(self):
        self.log_in()

        self.go_to_movements()

        print("Filter for movements")
        self.filter_for_current_month()
        time.sleep(1)

        self.scroll_to_show_all_movements()

        print("Get movements from page")
        movement_elements = self.get_movements_from_page()

        data = []
        columns = ["id", "date", "description", "concept",
                   "category", "amount"]
        for index, mov in enumerate(movement_elements):
            print(f"Element: {index}")
            mov_data = self.get_data_from_mov_element(mov)
            print(mov_data)

            data.append([
                mov_data.get("id"),
                mov_data.get("date"),
                mov_data.get("description"),
                mov_data.get("concept"),
                mov_data.get("category"),
                mov_data.get("amount")])

        self.driver.quit()

        df = pd.DataFrame(data, columns=columns)

        df["amount"] = df["amount"].str.replace(".", "")
        df["amount"] = df["amount"].str.replace(",", ".")
        df["amount"] = pd.to_numeric(df["amount"])
        df["date"] = pd.to_datetime(df["date"])

        return df
