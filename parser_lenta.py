# -*- coding: utf-8 -*-
import undetected_chromedriver
from undetected_chromedriver.webelement import By
import time
import json
from bs4 import BeautifulSoup
import pprint
import requests


def get_data():
    all_viski_lenta = []
    for i in [1, 2]:

        try:
            op = undetected_chromedriver.ChromeOptions()
            op.add_argument("--headless")  # Настройка для работы браузера в фоновом режиме
            driver = undetected_chromedriver.Chrome(options=op)
            # driver.get("https://intoli.com/blog/not-possible-to-block-chrome-headless/chrome-headless-test.html")
            driver.get(
                f"https://lenta.com/catalog/alkogolnye-napitki/krepkijj-alkogol/viski/?sorting=ByPriority&page={i}")
            time.sleep(1)
            button = driver.find_element(By.XPATH,
                                         "/html/body/div[1]/div[2]/div/div/div/div/div[3]/button[1]").click()
            time.sleep(1)
            with open(f"lenta_viski_page{i}.html", "w", encoding="utf-8") as file:
                file.write(driver.page_source)
            print(f"Страница{i} создана")

        except Exception as ex:
            print(ex)
        finally:
            driver.close()
            driver.quit()

        with open(f"lenta_viski_page{i}.html", encoding='utf-8') as file:
            src = file.read()

        # Парсинг
        soup = BeautifulSoup(src, 'lxml')
        all_viski = soup.find_all(class_="sku-card-small-container")
        all_viski_list = []
        for viski in all_viski:
            try:
                discount = viski.find(
                    class_="discount-label-small discount-label-small--sku-card sku-card-small__discount-label").text.strip()
            except AttributeError:
                discount = None
            title = viski.find(class_="sku-card-small-header__title").text.strip()
            price_sale = viski.find(
                class_="price-label sku-card-small-prices__price price-label--small price-label--primary").find(
                class_="price-label__integer").text.strip().replace('\xa0', '')
            price_full = viski.find(
                class_="price-label sku-card-small-prices__price price-label--small price-label--regular").find(
                class_="price-label__integer").text.strip().replace('\xa0', '')
            href = "https://lenta.com/" + viski.find(class_="sku-card-small sku-card-small--ecom").get("href")
            picture = viski.find(class_="square__inner").find("source").get("srcset")
            picture = str(picture.split("?")[0])
            all_viski_list.append({'title': title, 'href': href, 'picture': picture, 'discount': discount,
                                   'price_sale': price_sale, 'price_full': price_full})
        all_viski_lenta.extend(all_viski_list)
        print(f"Парсер страницы {i} готов")

        # Запись всех данных в json
        with open(f"json_discont_viski_page{i}.json", "w") as file:
            json.dump(all_viski_list, file, indent=4, ensure_ascii=False)
        print(f"Запись json страницы {i} готов")

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.136 YaBrowser/20.2.3.213 Yowser/2.5 Safari/537.36',
    }
    # Сохранение картинок
    for i, viski in enumerate(all_viski_lenta):
        viski['count_picture'] = i  # Добавления номера картинки виски в словарь
        url = viski['picture']
        img = requests.get(url, headers=headers)
        with open(f'D:\Parsing_lenta\img\img_{i}.png', 'wb') as file:
            file.write(img.content)
    print("Сохранение картинок завершено")

    return all_viski_lenta


if __name__ == "__main__":
    get_data()
