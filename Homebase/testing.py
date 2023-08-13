import django, os, json, time, re
from datetime import datetime, date 
from dateutil.relativedelta import relativedelta
from selenium.webdriver.common.by import By
from django.conf import settings
from selenium.webdriver.support import expected_conditions as EC

import pandas as pd
import numpy as np

os.environ['DJANGO_SETTINGS_MODULE'] = 'Homebase.settings'
django.setup()

from models.BBVA_scraper import BBVAScraper

bbva_scraper = BBVAScraper(headless=False)

bbva_scraper.get_backlog_month_categories()