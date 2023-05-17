import requests
from bs4 import BeautifulSoup
import os


RESULT_FOLDER = 'data'
RESULT_FILE_NAME = 'links.csv'
PATH_TO_RESULT = os.path.join(os.getcwd(), RESULT_FOLDER)
HTML_PAGES_FOLDER = 'source'
HTML_PAGES_PATH = os.path.join(os.getcwd(), HTML_PAGES_FOLDER)

EXCEPT_CATEGORIES = [
    'Бронированные автомобили',
    'ГАИ, ГИБДД',
    'Гаражные кооперативы',
    'МРЭО',
    'Штрафстоянки',
]


def get_data(url: str):
    headers = {
        'accept': '*/*',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'ru,en;q=0.9,de;q=0.8',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 YaBrowser/23.3.4.603 Yowser/2.5 Safari/537.36'
    }

    req = requests.get(url, headers=headers)

    with open(f'{HTML_PAGES_PATH}/main.html', 'w', encoding='utf-8') as file:
        file.write(req.text)

    with open(f'{HTML_PAGES_PATH}/main.html', 'r', encoding='utf-8') as html_file:
        html_code = html_file.read()

    bs = BeautifulSoup(html_code, 'lxml')
    category_links = bs.find(class_='single').find_all('a')

    category_page_links = []

    for category in category_links:
        if category.text not in EXCEPT_CATEGORIES:
            link = 'https://souo-mos.ru' + category['href']
            category_page_links.append(link)

    print(category_page_links)


def main():
    if not os.path.exists(PATH_TO_RESULT):
        os.mkdir(PATH_TO_RESULT)

    if not os.path.exists(HTML_PAGES_PATH):
        os.mkdir(HTML_PAGES_PATH)

    get_data('https://souo-mos.ru/spravochnyk/avto/')


if __name__ == '__main__':
    main()
