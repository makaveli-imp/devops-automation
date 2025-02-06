import threading
import traceback
import random

import time
from selenium.common.exceptions import TimeoutException, WebDriverException

from Data.rubric import Rubric, Visit
from Tools.driver import WebDriver
from config.config import Config


class Tracker(threading.Thread):
    sites = []
    pause = False

    def __init__(self, i: int):
        super().__init__()
        self.i = i

    def run(self):
        webdriver = WebDriver(usr_data=r'C:\Profiles\P' + str(self.i) + r'\User Data')
        while True:
            try:
                lock = threading.Lock()
                lock.acquire()
                if len(Tracker.sites) == 0:
                    Tracker.sites = Rubric.getrebrics()
                url = Tracker.sites[random.randint(0, (len(Tracker.sites) - 1))]
                Tracker.sites.remove(url)
                lock.release()
                # if 'hespress' not in url.link:
                #     continue
                Visit.generatevisite(url)
                webdriver.visit(url)
                time.sleep(3)
                print("visit id :", url.visit.id)
                webdriver.links()
            except (WebDriverException, TimeoutException, ConnectionRefusedError):
                webdriver.quit()
                webdriver = WebDriver(usr_data=r'C:\Profiles\P' + str(self.i) + r'\User Data')
            except:
                traceback.print_exc()
                continue

        webdriver.quit()
