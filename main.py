import requests
from bs4 import BeautifulSoup
import os
import csv


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


def data_to_csv(data: str):
    PATH_TO_RESULT_FILE = os.path.join(PATH_TO_RESULT, RESULT_FILE_NAME)

    if not os.path.exists(PATH_TO_RESULT_FILE):
        with open(PATH_TO_RESULT_FILE, 'w', encoding='utf-8', newline='') as csv_file:
            csvwriter = csv.writer(csv_file)
            csvwriter.writerow([data])

    else:
        with open(PATH_TO_RESULT_FILE, 'a', encoding='utf-8', newline='') as csv_file:
            csvwriter = csv.writer(csv_file)
            csvwriter.writerow([data])


def get_data(url: str):
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36'
    }

    req = requests.get(url, headers=headers)

    with open(f'{HTML_PAGES_PATH}/main.html', 'w', encoding='utf-8') as file:
        file.write(req.text)

    with open(f'{HTML_PAGES_PATH}/main.html', 'r', encoding='utf-8') as html_file:
        html_code = html_file.read()

    bs = BeautifulSoup(html_code, 'lxml')
    category_links = bs.find(class_='single').find_all('a')

    category_page_links = {}

    for category in category_links:
        if category.text not in EXCEPT_CATEGORIES:
            link = 'https://souo-mos.ru' + category['href']
            category_page_links[category.text] = link

    count = 0

    for category, link in category_page_links.items():
        print(f'\nВыполняется обработка в категории {category}...')
        
        req = requests.get(link, headers=headers)

        with open(f'{HTML_PAGES_PATH}/{category}.html', 'w', encoding='utf-8') as file:
            file.write(req.text)

        with open(f'{HTML_PAGES_PATH}/{category}.html', 'r', encoding='utf-8') as html_file:
            html_code = html_file.read()

        bs = BeautifulSoup(html_code, 'lxml')
        boxes = bs.find(class_='posts').find_all(class_='box')
        
        if not boxes:
            print('Данных в данной категории нет...\n')
            count += 1

            continue

        total_pages = int(bs.find('a', attrs={'class': 'last'})['href'].split('/')[-2])
        
        for page in range(1, total_pages + 1):
            print(f'\nСтраница {page}')

            page_link = link + f'page/{page}/'
            req = requests.get(page_link, headers=headers)
            
            with open(f'{HTML_PAGES_PATH}/{category}_{page}.html', 'w', encoding='utf-8') as file:
                file.write(req.text)

            with open(f'{HTML_PAGES_PATH}/{category}_{page}.html', 'r', encoding='utf-8') as file:
                html = file.read()

            bs = BeautifulSoup(html, 'lxml')

            boxes = bs.find('div', attrs={'id': 'boxes'}).find_all(class_='box')

            for box in boxes:
                if box.find('a').text.lower() != 'тестовая организация':
                    name_firm = box.find('a').text
                    firm_link = box.find('a')['href']

                    req = requests.get(firm_link, headers=headers)
                    bs = BeautifulSoup(req.text, 'lxml')

                    try:
                        site = bs.find(class_='posts').find('article').find('a', attrs={'itemprop': 'url'})['href']

                    except TypeError:
                        print(f'Сайт фирмы {name_firm} не указан')
                        continue

                    data_to_csv(site)

                    print(f'Сайт фирмы {name_firm} записан...')
                        
        count += 1            


def main():
    if not os.path.exists(PATH_TO_RESULT):
        os.mkdir(PATH_TO_RESULT)

    if not os.path.exists(HTML_PAGES_PATH):
        os.mkdir(HTML_PAGES_PATH)

    get_data('https://souo-mos.ru/spravochnyk/avto/')

    print('\nРабота завершена.')


if __name__ == '__main__':
    main()
