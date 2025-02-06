import traceback
import io
import imagehash
import pickle
import hashlib
import json
import base64
from PIL import Image
from selenium.common.exceptions import StaleElementReferenceException, WebDriverException, NoSuchElementException, TimeoutException
from selenium.webdriver import Chrome, ChromeOptions, Firefox#, PhantomJS
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from Tools.api import Api
import imageio
from Data.ad import AdElement
from Data.rubric import Rubric
from config.config import Config
from config.init import Initializer
from time import sleep
import requests


class WebDriver:
    # region init
    i = 0

    def __init__(self, usr_data=None):
        if Config.instance.drivers.browser == "chrome":
            # self.download_dir = download_dir
            options = ChromeOptions()
            # options.binary_location = 'C:\Applications\config\chromium-win-72.0.3596.0\chromium.exe'
            if Config.instance.drivers.chromedriver.hidden:
                options.add_argument("--headless")
            options.add_argument('--start-maximized')
            options.add_argument('--disable-gpu')
            options.add_argument('--ignore-certificate-errors')
            options.add_argument('--disable-popup-blocking')
            if usr_data is not None:
                options.add_argument('user-data-dir=' + usr_data)
            # options.add_experimental_option('prefs', {'download.default_directory': download_dir})
            # self.driver = Chrome(service=ChromeService(ChromeDriverManager().install()), chrome_options=options)
            self.driver = Chrome(executable_path="config/drivers/chromedriver.exe", chrome_options=options)
            self.num_frames = 16
            self.frame_rate = 5
            try:
                self.loadcookies()
            except:
                pass
        elif Config.instance.drivers.browser == "firefox":
            self.driver = Firefox(executable_path=Config.instance.firefoxdriver.path)
        # else:
        #     self.driver = PhantomJS(executable_path=Config.instance.phantomjs.path)
        self.driver.get("http://google.com")

    # endregion
    # region driver
    def visit(self, url: Rubric):
        self.current = url
        self.driver.get(url.link)

    def quit(self):
        try:
            self.driver.close()
            self.driver.quit()
        except:
            pass
        Initializer.deletetmp()

    # endregion
    # region ads
    def links(self):
        paths = Api.xpath_api(self.driver)
        if paths is None:
            print(self.driver.current_url, 'is not in the api')
            return
        print(self.driver.current_url)
        self.get_ads()
        articles = []
        for articl_path in paths['articl_xpath']:
            try:
                articl = self.driver.find_element(By.XPATH, articl_path)
                a = articl.find_element(By.TAG_NAME, 'a')
                print('article:', a.get_attribute("href"))
                articles.append(a.get_attribute("href"))
            except Exception as e:
                print('articl not found')
        for article in articles:
            try:
                self.driver.get(article)
                sleep(2)
                self.get_ads()
            except:
                pass

        
    def get_ads(self):
        paths = Api.xpath_api(self.driver)
        # ---- Ads to close take the ad and remove the element
        for path in paths["ads_to_close"]:
            print('ad to close')
            try:
                element = self.driver.find_element(By.XPATH, path)
                print('---------------------------------------------------------------')
                print(element.get_attribute('id'))
                iframe = element.find_element(By.TAG_NAME, 'iframe')
                self.content_loader(iframe)
                self.driver.execute_script("""
                            var element = arguments[0];
                            element.parentNode.removeChild(element);
                            """, element)
            except:
                print('--iframe not found')
        elements = self.driver.find_elements(By.TAG_NAME, 'ins')
        for element in reversed(elements):
            try:
                iframe = element.find_element(By.TAG_NAME, 'iframe')
                self.content_loader(iframe)
                self.driver.execute_script("""
                            var element = arguments[0];
                            element.parentNode.removeChild(element);
                            """, element)
            except:
                pass
        # ---- get video url
        video_url = None
        for element in self.driver.find_elements(By.CLASS_NAME, 'teads-player'):
            print('---------------------------------------------------------------')
            print('teads element:', element.get_attribute('class'))
            try:
                iframe = element.find_element(By.TAG_NAME, 'iframe')
                self.driver.switch_to.frame(iframe)
                try:
                    video = self.driver.find_element(By.TAG_NAME, 'video')
                    video_url = video.get_attribute('src')
                    # print('video teads url:', video_url)
                    self.driver.switch_to.default_content()
                    break
                except:
                    pass
                try:
                    iframe2 = self.driver.find_element(By.TAG_NAME, 'iframe')
                    self.driver.switch_to.frame(iframe2)
                    try:
                        print("video !!")
                        video = self.driver.find_element(By.TAG_NAME, 'video')
                        video_url = video.get_attribute('src')
                        # print('video2 url:', video_url)
                        self.driver.switch_to.default_content()
                        break
                    except:
                        pass
                    try:
                        iframe3 = self.driver.find_element(By.TAG_NAME, 'iframe')
                        self.driver.switch_to.frame(iframe3)
                        try:
                            video = self.driver.find_element(By.TAG_NAME, 'video')
                            video_url = video.get_attribute('src')
                            # print('video3 url:', video_url)
                            self.driver.switch_to.default_content()
                            break
                        except:
                            pass
                    except Exception as e:
                        print('iframe3 not found')
                except Exception as e:
                    print('iframe2 not found')
            except Exception as e:
                print('iframe not found')
            finally:
                self.driver.switch_to.default_content()
        if video_url:
            print("**1**")
            self.insert_video(iframe, video_url)
            

        # ---- remove header
        try:
            header = self.driver.find_element(By.TAG_NAME, 'header')
            self.driver.execute_script("""
                                var element = arguments[0];
                                element.parentNode.removeChild(element);
                                """, header)
        except:
            print('header not exist')
        # ---- get ads
        for path in paths["ads_xpath"]:
            try:
                print('---------------------------------------------------------------')
                element = self.driver.find_element(By.XPATH, path)
                self.content_loader(element)
            except:
                print('--element not found')
        # ---- remove popup
        for path in paths['popup_close']:
            try:
                button = self.driver.find_element(By.XPATH, path)
                button.click()
            except:
                print('popup not found')
#--
    def content_loader(self, el: WebElement):
        try:
            if 'youtube' in el.get_attribute('src'):
                video_url = el.get_attribute('src')
                video_url = video_url.split('?')[0]
                print("**2**")
                self.insert_video(el, video_url)
                return
            size = el.size
            print(size)
            print('iframe: ', el.get_attribute('id'))
            self.driver.switch_to.frame(el)
            try:
                lima_video = self.driver.find_element(By.TAG_NAME, 'lima-video')
                video_url = lima_video.get_attribute("src")
                print("**3**")
                self.driver.switch_to.default_content()
                self.insert_video(el, video_url)
                return
            except:
                pass
            try:
                img = self.driver.find_element(By.TAG_NAME, 'img')
                print('found image')
                size_img = img.size
                print(size_img)
                if(size_img['height'] >= size['height'] / 2 and  size_img['width'] >= size['width'] / 2):
                    print('++image: ', img.get_attribute('src'))
                    self.download_picture(el = img)
                    self.driver.switch_to.default_content()
                    return
                else:
                    print('+-image small:', img.get_attribute('src'))
            except:
                print('--image not found')
                try:
                    ifram2 = self.driver.find_element(By.TAG_NAME, 'iframe')
                    if 'youtube' in ifram2.get_attribute('src'):
                        video_url = ifram2.get_attribute('src')
                        video_url = video_url.split('?')[0]
                        print("**4**")
                        self.driver.switch_to.default_content()
                        self.insert_video(el, video_url)
                        return
                    print('ifram2: ', ifram2.get_attribute('id'))
                    self.driver.switch_to.frame(ifram2)
                    try:
                        lima_video = self.driver.find_element(By.TAG_NAME, 'lima-video')
                        video_url = lima_video.get_attribute("src")
                        print("**5**")
                        self.driver.switch_to.default_content()
                        self.insert_video(el, video_url)
                        return
                    except:
                        pass
                    try:
                        img2 = self.driver.find_elements(By.TAG_NAME, 'img')
                        if len(img2) > 3:
                            raise Exception
                        size_img2 = img2.size
                        print(size_img2)
                        if(size_img2['height'] > size['height'] / 2 and  size_img2['width'] > size['width'] / 2):
                            print('++image2: ', img2.get_attribute('src'))
                            self.download_picture(el = img2)
                            self.driver.switch_to.default_content()
                            return
                        else:
                            print('+-image2 small:', img2.get_attribute('src'))
                    except:
                        print('--image2 not found')
                    print('cur_url2', self.driver.current_url)
                except:
                    print('--ifram2 not found')
            self.driver.switch_to.default_content()
            if (not el.is_displayed()) or (el.size['height'] < 30 or el.size['width'] < 30):
                return
            print('screenshoot')
            self.take_screenshot(el)
        except:
            print('Not an Iframe')
            try:
                img = el.find_element(By.TAG_NAME, 'img')
                self.download_picture(el = img)
            except:
                try:
                    video = el.find_element(By.TAG_NAME, 'video')
                    video_url = video.get_attribute("src")
                    print("**6**")
                    self.insert_video(el, video_url)
                except:
                    self.take_screenshot(el)
    def download_picture(self, el: WebElement):
        try:
            url = el.get_attribute('src')
            print('++picture', url)
            img_stream = requests.get(url, stream=True, timeout=5)
            img_data = requests.get(url, timeout=5).content
            if hash(img_data) == 0:
                print('broken image')
                return
            hashs = [str(imagehash.average_hash(Image.open(img_stream.raw)))]
            xpath = self.getabsolutexpath(el)
            ad = AdElement(self.current, [""], [""],
                                el.location.get("x"), el.location.get("y"),
                                el.size.get("width"), el.size.get("height"), xpath, hashs)
            try:
                with open(Config.instance.directories.adsdir + ad.getfilename(), 'wb') as f:
                    f.write(img_data)
                ad.insert()
                print('picture inserted')
            except:
                print('couldnt save picture')
        except:
            print('download picture error')
    def insert_video(self, iframe: WebElement, video_url):
        print("found a video")
        try:
            print('++video:', video_url)
            hashs = [hashlib.md5(video_url.encode()).hexdigest()]
            ad = AdElement(self.current, [""], [""],
                iframe.location.get("x"), iframe.location.get("y"),
                iframe.size.get("width"), iframe.size.get("height"), "xpath", hashs, True, video_url)
            ad.insert()
            print('video inserted')
        except Exception as e:
            print(e)
    def take_screenshot(self, el: WebElement):
        try:
            frames = []
            hashs = []
            for p in range(self.num_frames):
                screenshot = el.screenshot_as_base64
                png_recovered = base64.b64decode(screenshot)
                screenshot = Image.open(io.BytesIO(png_recovered))
                frames.append(screenshot)
                extrema = screenshot.convert("L").getextrema()
                if extrema[0] < (extrema[1] - 25):
                    hashs.append(str(imagehash.average_hash(screenshot, 12)))
                sleep(1/self.frame_rate)
            xpath = self.getabsolutexpath(el)
            if len(hashs) == 0:
                print('One color')
                return
            hashs = list(dict.fromkeys(hashs))
            ad = AdElement(self.current, [""], [""],
                                el.location.get("x"), el.location.get("y"),
                                el.size.get("width"), el.size.get("height"), xpath, hashs)
            try:
                imageio.mimsave(Config.instance.directories.adsdir + ad.getfilename(), frames, 'GIF', duration=1/self.frame_rate)
                ad.insert()
                print('screenshot inserted')
            except:
                print('couldnt save sreenshot')
        except Exception as e:
            print('error secreenshot')
   

    def getabsolutexpath(self, element: WebElement):
        script = r'''function getXPath(node) {
                    if (node.id !== '') {
                        return '//' + node.tagName.toLowerCase() + '[@id=""' + node.id + '""]'

                    }
                    if (node === document.body) {
                        return node.tagName.toLowerCase()
                    }
                    var nodeCount = 0;
                    var childNodes = node.parentNode.childNodes;

                    for (var i = 0; i<childNodes.length; i++) {
                        var currentNode = childNodes[i];

                        if (currentNode === node) {
                            return getXPath(node.parentNode) + '/' + node.tagName.toLowerCase()
                    + '[' + (nodeCount + 1) + ']'
                        }

                        if (currentNode.nodeType === 1 &&
                            currentNode.tagName.toLowerCase() === node.tagName.toLowerCase()) {
                            nodeCount++
                        }
                    }
                };
                return getXPath(arguments[0]);'''
        try:
            return self.driver.execute_script(script, element)
        except:

            traceback.print_exc()
            return ""


    # endregion
    # region searcher
    def savecookies(self):
        pickle.dump(self.driver.get_cookies(), open("config/cookies.pkl", "wb"))

    def loadcookies(self):
        cookies = pickle.load(open("config/cookies.pkl", "rb"))
        for cookie in cookies:
            self.driver.add_cookie(cookie)
    # endregion
