import requests, time, pathlib
from bs4 import BeautifulSoup
imgdir = './images/'
url = 'http://www.tomukulele.com/'
headers = {'Host':'www.tomukulele.com', 'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36 Edg/92.0.902.67', 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9', 'Accept-Encoding':'gzip, deflate','Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6'}
cookies = {'ASPSESSIONIDCCBQRQRR':'BDAIOHMBHPJLNKPHDPAELFBD'}

def get_contents(door, url, headers, cookies):
    target = url + door
    html = requests.get(target, headers=headers, cookies=cookies).text
    soup = BeautifulSoup(html, 'lxml')
    print("Get " + target)
    return soup

def next_page(soup, url, headers, cookies):
    if soup == None:
        return soup
    page = soup.find('div', class_ = 'mainproducts')
    p = page.find('div', class_='page')
    refs = p('a')
    for r in refs:
        if r.text == '下一页':
            door = r['href']
            print('Next page: ', end = '')
            s = get_contents(door, url, headers, cookies)
            return s
    return None

def downloader(box, material, model, url):
    try:
        src = box.img['src']
        name = imgdir + material + '/' + model + '/' + src.split('/')[-1]
        target = url + src
        header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36 Edg/92.0.902.67'}
        food = requests.get(target, headers=header)
        print('Downloading ' + target)
        with open(name, 'wb') as f:
            print('Saving at ' + name)
            f.write(food.content)
    except TypeError as e:
        pass

def brower(soup, material, url):
    if soup == None:
        return False
    shops = soup.find('div', class_ = 'mainproducts')
    if shops != None:
        pathlib.Path(imgdir + material).mkdir(exist_ok = True)
        lists = shops.ul
        navs = lists('a')
        for nav in navs:
            model = nav.find('div', class_='tit').text
            pathlib.Path(imgdir + material + '/' + model).mkdir(exist_ok = True)
            time.sleep(0.5)
            door = nav['href']
            s = get_contents(door, url, headers, cookies)
            foods = s.find('div', class_ = 'wrap_info')
            imgs = foods.find_all('p')
            for i in imgs:
                downloader(i, material, model, url)
        return True
    return False

def main():
    pathlib.Path(imgdir).mkdir(exist_ok = True)
    html, soup = get_contents('', url, headers, cookies)
    boxes = soup.find('div', class_ = 'nav fl')
    contents = boxes.find('li', id = 'm3', class_ = 'm4')
    xsr = contents.find('div', class_ = 'xiao_six_r')
    refs = xsr.find_all('a')
    for r in refs:
        u = r['href']
        soup = get_contents(u, url, headers, cookies)
        material = r.text
        while brower(soup, material, url) == True:
            soup = next_page(soup, url, headers, cookies)

if __name__ == "__main__":
    main()