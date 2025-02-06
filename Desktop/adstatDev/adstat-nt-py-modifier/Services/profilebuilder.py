import threading
import traceback
import random

import time
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.common.by import By

from Data.engine import SearchEngine
from Data.secteur import Secteur, Query
from Tools.driver import WebDriver


class ProfileBuilder(threading.Thread):
    visited = []
    searsher = ['https://www.bing.com/search?q=', "https://www.google.com/search?q=",
                "https://www.youtube.com/results?search_query="]

    def __init__(self, i: int):
        super().__init__()
        self.i = i

    def run(self):
        webdriver = WebDriver(usr_data=r'C:\Profiles\S' + str(self.i) + r'\User Data')

        while True:
            try:
                webdriver.savecookies()
                if len(Query.queries) == 0:
                    Secteur.getsecteurs()
                q = Query.queries[random.randint(0, (len(Query.queries) - 1))]
                Query.queries.remove(q)
                for se in SearchEngine.getEngines():
                    print("search for : ", q.name)
                    webdriver.driver.get(se.link + q.name)
                    links = [a.get_attribute("href") for a in
                             webdriver.driver.find_elements(By.XPATH, se.xpath)]
                    links = [l for l in links if se.id not in l and l not in self.visited]
                    if len(links) == 0:
                        print('end search for ', q, ' in ', se.id)
                    else:
                        for a in links:
                            print('{:2}/{:3} : {}'.format(links.index(a) + 1, len(links), a))
                            webdriver.driver.get(a)
                            self.visited.append(a)
                            webdriver.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                            webdriver.enitierSS("ss/{:10} {:3} {:3}.jpeg".format(q.name, len(links), links.index(a) + 1))
                            time.sleep(2)
                    time.sleep(2.5)
                webdriver.savecookies()
            except (WebDriverException, TimeoutException,ConnectionRefusedError):
                webdriver.quit()
                webdriver = WebDriver(usr_data=r'C:\Profiles\P' + str(self.i) + r'\User Data')

            except Exception as ex:
                print(ex.__class__)
                traceback.print_exc()
                continue
