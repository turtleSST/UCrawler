from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, TimeoutException, ElementNotInteractableException, ElementClickInterceptedException
import time, os, pathlib, requests, json

def open_chrome(user_port):
    find_port = os.popen('netstat -ano|findstr {}'.format(user_port)).read()
    while str(user_port) in find_port:
        print('Port' + str(user_port) + 'is using')
        user_port += 1
        find_port = os.popen('netstat -ano|findstr {}'.format(user_port)).read()
    os.system('start chrome.exe --remote-debugging-port={} --user-data-dir="D:\\Things\\spider\\UCrawler\\tbSpider\\chrome"'.format(user_port))
    print('Using port ', user_port)

class ItemClass:
    def __init__(self, dataDir, url_keyword, user_port, web):
        self.url_keyword = url_keyword
        self.dataDir = dataDir
        self.user_port = user_port
        self.web = web
        self.failure = []
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:{}".format(self.user_port))
        chrome_driver = "D:\\Things\\spider\\UCrawler\\tbSpider\\chromedriver.exe"
        try:
            self.Chrome = webdriver.Chrome(chrome_driver, options=chrome_options)
        except Exception as e:
            print('Error occurred while starting chrome:\n', e)
        self.Chrome.maximize_window()
        self.Chrome.implicitly_wait(10)
        self.Chrome.set_page_load_timeout(10)
        self.Chrome.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {"source": """
                      Object.defineProperty(navigator, 'webdriver', {
                      get: () => undefined
                      })
                      """})

    def searchwords(self):
        self.Chrome.get('https://taobao.com')
        self.Chrome.find_element_by_xpath('//*[@id="q"]').send_keys('{}'.format(self.url_keyword['searchName']))
        time.sleep(0.3)
        self.Chrome.find_element_by_xpath('//button[@class="btn-search tb-bg"]').click()

    def intercept(self):
        if '验证码拦截' in self.Chrome.title:
            time.sleep(5)
            # slider = self.Chrome.find_element_by_xpath("//span[contains(@class, 'btn_slide')]")
            # try:
            #     if slider.is_displayed():
            #         ActionChains(self.Chrome).click_and_hold(on_element=slider).perform()
            #         ActionChains(self.Chrome).move_by_offset(xoffset=258, yoffset=0).perform()
            #         ActionChains(self.Chrome).pause(0.5).release().perform()
            # except Exception as err:
            #     print(err)
            # time.sleep(1)
    
    def download_video(self, folder, row, col):
        self.Chrome.execute_script("var q=document.documentElement.scrollTop=0")
        tb_booth = self.Chrome.find_element_by_xpath('//*[@id="J_DetailMeta"]/div[1]/div[2]/div[1]')
        flag = False
        try:
            tb_booth.find_element_by_xpath('.//div[@class="tm-video-box"]')
            flag = True
        except NoSuchElementException as e:
            print("Video not started, trying to find")
            pass
        if flag == False:
            try:
                tb_booth.find_element_by_xpath('.//i[@class="tm-video-play J_playVideo"]').click()
                time.sleep(3)
            except NoSuchElementException as e:
                print("No video found")
                return
        try:
            src = tb_booth.find_element_by_xpath('.//video/source').get_attribute('src')
        except NoSuchElementException as e:
            print(e)
            self.failure.append((row, col))
            return
        print("Downloading video from " + src)
        header = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36"}
        response = requests.get(src, headers=header, stream=True)
        with open(folder + '\\video.mp4', 'wb') as f:
            f.write(response.content)

    def scrolldown(self, times):
        y_plus = 550
        y = 0
        for i in range(times):
            y += y_plus
            self.Chrome.execute_script("window.scroll(0,{})".format(y))
            time.sleep(0.2)

    def click_next(self):
        self.Chrome.find_element_by_xpath('//a[@title="下一页"]').click()
        time.sleep(1)

    def get_goods(self, web):
        time.sleep(0.5)
        for item in self.Chrome.find_elements_by_xpath('.//*[@class="item J_MouserOnverReq  "]'):
            shop = item.find_element_by_xpath('.//div[@class="shop"]/a')
            if shop.text != self.url_keyword['shopName']:
                continue
            shop.click()
            break
        time.sleep(0.5)
        self.Chrome.switch_to.window(self.Chrome.window_handles[-1])
        hd = self.Chrome.find_element_by_xpath('//div[@id="hd"]')
        if web == 1:
            banner_box = hd.find_element_by_xpath('.//div[@class="banner-box"]/div')
            target = banner_box.find_element_by_xpath('.//map[@name="fkmap1576167562"]/area[2]').get_attribute('href')
            print(target)
            self.Chrome.get(target)
        if web == 2:
            hd.find_element_by_xpath('.//div[@class="banner-box"]/div/div/div/div/div/a[2]').click()
        if web == 3:
            target = hd.find_element_by_xpath('.//div[@class="banner-box"]/map/area[3]').get_attribute('href')
            print(target)
            self.Chrome.get(target)
        if web == 4:
            hd.find_element_by_xpath('.//ul[@class="menu-list"]/li[3]/a').click()
        time.sleep(3)
        self.Chrome.switch_to.window(self.Chrome.window_handles[-1])

    def getDetailPrice(self):
        self.scrolldown(1)
        m = {}
        tb_sku = self.Chrome.find_element_by_xpath('//*[@id="J_DetailMeta"]/div[1]/div[1]/div/div[4]/div/div')
        props = tb_sku.find_elements_by_xpath('.//dl[contains(@class, "tb-prop tm-sale-prop")]')
        propNum = len(props)
        if propNum == 0:
            title = self.Chrome.find_element_by_xpath('//div[@class="tb-detail-hd"]/h1').text
            price = self.Chrome.find_element_by_xpath('//dl[contains(@class, "tm-price-panel")]/dd/span').text
            m[title] = price
            return m
        if propNum == 1:
            c = props[0].find_element_by_xpath('.//ul[contains(@class, "tm-clear J_TSaleProp")]')
            choices = c.find_elements_by_xpath('.//li')
            for choice in choices:
                title = choice.get_attribute('title')
                try:
                    choice.find_element_by_xpath('.//a').click()
                except ElementNotInteractableException as e:
                    print(e)
                    continue
                price = self.Chrome.find_element_by_xpath('//dl[contains(@class, "tm-price-panel")]/dd/span').text
                m[title] = price
            return m
        else:
            c1 = props[0].find_element_by_xpath('.//ul[contains(@class, "tm-clear J_TSaleProp")]')
            c2 = props[1].find_element_by_xpath('.//ul[contains(@class, "tm-clear J_TSaleProp")]')
            choices1 = c1.find_elements_by_xpath('.//li')
            choices2 = c2.find_elements_by_xpath('.//li')
            for choice1 in choices1:
                time.sleep(0.5)
                title = choice1.get_attribute('title')
                try:
                    choice1.find_element_by_xpath('.//a').click()
                except ElementNotInteractableException as e:
                    print(e)
                    continue
                for choice2 in choices2:
                    time.sleep(0.5)
                    if choice2.get_attribute('class') != "tb-out-of-stock":
                        size = choice2.find_element_by_xpath('.//a/span').text
                        try:
                            choice2.find_element_by_xpath('.//a').click()
                        except ElementNotInteractableException as e:
                            print(e)
                            continue
                        except ElementClickInterceptedException as e:
                            print(e)
                            continue
                        price = self.Chrome.find_element_by_xpath('//dl[contains(@class, "tm-price-panel")]/dd/span').text
                        m[title + '_' + size] = price
                        choice2.find_element_by_xpath('.//a').click()
                choice1.find_element_by_xpath('.//a').click()
            return m

    def browse(self):
        time.sleep(0.5)
        print("Browsing " + self.url_keyword['folderName'] + "'s shop")
        self.scrolldown(2)
        if web == 1 or web == 2:
            targetElem = self.Chrome.find_elements_by_xpath('//div[@class="item5line1"]')[:9]
        if web == 3:
            targetElem = self.Chrome.find_elements_by_xpath('//div[@class="item4line1"]')[:4]
        if web == 4:
            targetElem = self.Chrome.find_element_by_xpath('.//div[@class="item3line1"]')
        self.scrolldown(5)
        row = 1
        col = 1
        for i in targetElem:
            col = 1
            for j in i.find_elements_by_xpath('.//dl[contains(@class,"item")]'):
                j.find_element_by_xpath('.//dd[@class="detail"]/a').click()
                time.sleep(3)
                self.Chrome.switch_to.window(self.Chrome.window_handles[-1])
                try:
                    title = self.Chrome.find_element_by_xpath('//div[@class="tb-detail-hd"]/h1').text
                except TimeoutException as e:
                    print(e)
                    self.Chrome.execute_script('window.stop ? window.stop() : document.execCommand("Stop");')
                    title = self.Chrome.find_element_by_xpath('//div[@class="tb-detail-hd"]/h1').text
                    pass
                d = (self.dataDir + title).replace('/', '_')
                pathlib.Path(d).mkdir(exist_ok = True)
                if web < 4:
                    self.download_video(d, row, col)
                price = self.getDetailPrice()
                print("Title: " + title)
                print("Price: " + str(price))
                msg = []
                msg.append(price)
                self.scrolldown(9)
                time.sleep(3)
                body = self.Chrome.find_element_by_xpath('//div[@id="mainwrap" and @class="main-wrap"]')
                try:
                    name = body.find_element_by_xpath('.//div[@class="name"]/b').text
                    print("品牌名称: " + name)
                    attrs = body.find_element_by_id('J_AttrUL')
                    for attr in attrs.find_elements_by_xpath('.//li'):
                        msg.append(attr.text)
                except NoSuchElementException as e:
                    print(e)
                    pass
                print(msg)
                with open(d + '\\msg.json', 'w', encoding='utf-8') as f:
                    json.dump(msg, f, ensure_ascii = False)
                boxes = body.find_element_by_xpath('.//div[@id="description"]/div')
                descriptions = boxes.find_elements_by_xpath('.//p')
                for description in descriptions:
                    try:
                        imgs = description.find_elements_by_xpath('.//img')
                    except NoSuchElementException as e:
                        print(e)
                        continue
                    except StaleElementReferenceException as e:
                        print(e)
                        continue
                    cache = []
                    seq = 1
                    for img in imgs:
                        img_src = img.get_attribute('src')
                        img_name = img_src.split('/')[-1].split('!!')[0][:-1]
                        if img_name not in cache:
                            cache.append(img_name)
                            file_name = d + '\\' + str(seq) + '.' + img_src.split('.')[-1]
                            seq += 1
                            header = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36"}
                            print("Downloading " + img_src)
                            img_data = requests.get(url = img_src, headers=header, timeout=10)
                            file_size = int(img_data.headers['Content-Length']) / 1024
                            if file_size > 1:
                                with open(file_name, 'wb') as f:
                                    f.write(img_data.content)
                if self.web == 2:
                    time.sleep(4)
                self.Chrome.close()
                self.Chrome.switch_to.window(self.Chrome.window_handles[-1])
                col += 1
            self.scrolldown(1)
            row += 1
        print("Row = " + str(row) + ", Col = " + str(col))
        print("Video download failure " + str(len(self.failure)))
        print(self.failure)
    

    def start(self):
        self.searchwords()
        time.sleep(1)
        self.intercept()
        self.get_goods(self.web)
        self.browse()
        self.Chrome.quit()

if __name__ == '__main__':
    user_port = 9555
    open_chrome(user_port)
    web = 4
    config = [{'searchName': 'tom尤克里里', 'shopName': 'tom乐器旗舰店', 'folderName': 'TOM'}, {'searchName': 'enya尤克里里', 'shopName': 'enya乐器旗舰店', 'folderName': 'enya'}, {'searchName': '彩虹人尤克里里', 'shopName': '彩虹人旗舰店', 'folderName': 'aNueNue'}, {'searchName': '星光流行音乐教室', 'shopName': 'liuzli', 'folderName': 'xingGuang'}]
    dataDir = '.\\data\\' + config[web - 1]['folderName'] + '\\'
    pathlib.Path(dataDir).mkdir(exist_ok = True)
    browser = ItemClass(dataDir, config[web - 1], user_port, web)
    browser.start()
