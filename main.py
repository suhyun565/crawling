import nest_asyncio
nest_asyncio.apply()
import time
from bs4 import BeautifulSoup
from selenium import webdriver
import json
import asyncio
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import ActionChains
import urllib.request
import requests
import time
from bs4 import BeautifulSoup as bs
from selenium import webdriver
import json

url="https://style.kakao.com/category/10000012"
browser = webdriver.Chrome("C:\./chromedriver")
browser.get(url)


def scroll():
    browser.execute_script("window.scrollTo(0,document.body.scrollHeight);")
    browser.execute_script("window.scrollTo(0,1000);")

for i in range(0,90):
         scroll()
         i+1
links=[]
html = browser.page_source
soup = bs(html, "html.parser")
for link in soup.find_all('a', {'class':"link_prd"}):
    links.append(link.get('href'))

print(len(links))

num_end = len(links)
new_url = link.get('href')


def scraper(new_url):
    options = webdriver.ChromeOptions()
    options.headless = True
    options.add_argument('window-size=1920x1080')
    options.add_argument("disable-gpu")

    driver = webdriver.Chrome("C:\./chromedriver", options=options)
    driver.get(new_url)

    return driver


async def get_product_info(Item_Num, waitTime, link):
    loop = asyncio.get_event_loop()
    url = "https://style.kakao.com" + link

    browser = await loop.run_in_executor(None, scraper, url)
    await  loop.run_in_executor(None, browser.get, url)
    await  loop.run_in_executor(None, browser.maximize_window)

    try:
        html = browser.page_source
        soup = BeautifulSoup(html, 'html.parser')

        title = (soup.find("strong", attrs={"class": "tit_proinfo"})).get_text()
        print(Item_Num, "st_title:", title)
        shop_title = (soup.find("strong", attrs={"class": "tit_shop"})).get_text()
        print(Item_Num, "st_shop_title:", shop_title)
        img_url = soup.find("img", attrs={"class": "img_thumb"}).get("src")
        print("st_img_url:", img_url)

        # 상세보기 클릭하고 url얻어오기
        item_detail = await loop.run_in_executor(None, WebDriverWait(browser, waitTime).until,
                                                 EC.presence_of_element_located(
                                                     (By.XPATH, "//*[@id='main']/main/div[1]/div/div[2]/div")))
        await loop.run_in_executor(None, item_detail.click)

        await loop.run_in_executor(None, browser.switch_to.window, browser.window_handles[-1])
        url = browser.current_url
        print(Item_Num, "url:", url)

        data = []
        kakao = {'category': '스커트', 'title': title, 'shop_title': shop_title, 'url': url, 'img_url': img_url}
        data.append(kakao)
        print(data)
        file.write(json.dumps(data, ensure_ascii=False))

    except:
        print("ERROR: Element search failed.")


async def main(waitTime, start, num_end):
    interval = 5
    tmp_start = start
    while (num_end >= tmp_start):
        tmp_end = tmp_start + interval - 1 if (tmp_start + interval <= num_end) else num_end
        futures = [asyncio.ensure_future(get_product_info(str(i), waitTime, links[i])) for i in
                   range(tmp_start, tmp_end)]
        await asyncio.gather(*futures)
        tmp_start = tmp_end + 1


if __name__ == "__main__":
    file = open("./kakao2.json", "w", encoding='utf-8')

    waitTime = 5

    start = time.time()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(waitTime, 1, num_end))
    file.close()

    num_end = time.time()
    print(f'time taken: {num_end - start}')
