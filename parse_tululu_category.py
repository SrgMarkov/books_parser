import argparse
import json
import os
import time
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup
from main import parse_book_page, download_image, download_txt


def get_books_id_by_category(url, start_page, end_page):
    books_numbers = []
    for page in range(start_page, end_page):
        connection_lost = False
        while True:
            try:
                category_page_url = urljoin(url, f'{page}')
                books_in_category = get_category_page_soup(category_page_url).select("table.d_book")
                books_numbers.extend([book.select_one("a")['href'].strip('/').replace('b', '')
                                      for book in books_in_category])
                break
            except requests.HTTPError as error:
                print(f'возникла ошибка {error}')
                break
            except requests.ConnectionError as error:
                if not connection_lost:
                    print(f'Ошибка сетевого соединения {error}. Перезапуск парсера')
                    time.sleep(10)
                    connection_lost = True
                else:
                    print(f'Ошибка сетевого соединения {error}. Перезапуск парсера через 5 минут')
                    time.sleep(300)
    return books_numbers


def get_category_page_soup(url):
    books_category_response = requests.get(url)
    books_category_response.raise_for_status()
    return BeautifulSoup(books_category_response.text, 'lxml')


if __name__ == '__main__':
    site_url = 'https://tululu.org/'
    books_category_number = 'l55/'
    book_text_url = 'https://tululu.org/txt.php'
    books_category_url = urljoin(site_url, books_category_number)
    last_page_in_category = get_category_page_soup(books_category_url).select("p.center a")[-1].get_text()
    command_arguments = argparse.ArgumentParser(description='скачивание книг категории "Научная фантастика "с сайта '
                                                            'https://tululu.org/ Для уточнения аргументов введите -h')
    command_arguments.add_argument('--start_page', help='с какой страницы начать загрузку', type=int, default=1)
    command_arguments.add_argument('--end_page', help='на какой странице закончить загрузку', type=int,
                                   default=int(last_page_in_category) + 1)
    command_arguments.add_argument('--dest_folder', help='указать папку для загрузки', default='books')
    command_arguments.add_argument('--skip_imgs', help='не скачивать обложки книг',
                                   default=False, action='store_true')
    command_arguments.add_argument('--skip_txt', help='не скачивать текст книг',
                                   default=False, action='store_true')
    args = command_arguments.parse_args()
    os.makedirs(args.dest_folder, exist_ok=True)
    books_attributes = []
    for book_id in get_books_id_by_category(books_category_url, args.start_page, args.end_page):
        download_params = {'id': book_id}
        connection_failure = False
        while True:
            try:
                book_page_response = requests.get(urljoin(site_url, f'b{book_id}'))
                book_page_response.raise_for_status()
                book_attributes = parse_book_page(book_page_response, urljoin(site_url, f'b{book_id}'))
                if not args.skip_imgs:
                    download_image(book_attributes['cover'], book_attributes['title'], args.dest_folder)
                if not args.skip_txt:
                    download_txt(book_text_url, download_params, f'{book_id} - {book_attributes["title"]}',
                                 args.dest_folder)
                books_attributes.append(book_attributes)
                break
            except requests.TooManyRedirects:
                print(f'Книга с id{book_id} не доступна для загрузки')
                break
            except requests.HTTPError as error:
                print(f'возникла ошибка {error}')
                break
            except requests.ConnectionError as error:
                if not connection_failure:
                    print(f'Ошибка сетевого соединения {error}. Перезапуск парсера')
                    time.sleep(10)
                    connection_failure = True
                else:
                    print(f'Ошибка сетевого соединения {error}. Перезапуск парсера через 5 минут')
                    time.sleep(300)
    with open(f"{args.dest_folder}/books_description.json", "a", newline='\r\n',
              encoding='utf8') as json_file:
        json.dump(books_attributes, json_file, ensure_ascii=False, indent=4)
