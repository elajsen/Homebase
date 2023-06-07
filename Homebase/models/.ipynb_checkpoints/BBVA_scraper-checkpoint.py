import selenium
import time
import re
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime, date
from dateutil.relativedelta import relativedelta


class BBVAScraper:
    def __init__(self, headless=False):
        self.headless = headless
        self.username = "Y6819278E"
        self.pswrd = "Qtepa1"

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

    def switch_to_iframe(self):
        iframe = self.driver.find_elements_by_tag_name("iframe")
        self.driver.switch_to.frame(iframe[0])

    def switch_to_default(self):
        self.driver.switch_to.default_content()

    def close_modal(self):
        self.driver.find_element_by_xpath(
            xpath=f"//span[@id='entendido']").click()

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
        self.driver.find_elements_by_xpath(
            xpath="//span[text()[contains(., 'Ver detalle por categor')]]")[0].click()
        time.sleep(3)

        self.driver.find_elements_by_xpath(
            xpath="//h3[text()[contains(., 'Mi día a ')]]")[0].click()
        time.sleep(2)

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
            amount_divs = self.driver.find_elements_by_xpath(
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
        category_cards = self.driver.find_elements_by_xpath(
            xpath="//div[@data-cy-id='card-icon']")
        for card in category_cards:
            category = card.find_element_by_tag_name(
                "h3").get_attribute("innerHTML")
            amt_card = card.find_element_by_xpath(
                xpath=".//span[@data-cy-id='data-amount']")
            amount = amt_card.find_element_by_xpath(
                xpath=".//span[@class='sr-only']").get_attribute("innerHTML")
            res[category] = string_to_float(amount)
        res["other income"] = get_income() - res.get("Nómina", 0)
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
