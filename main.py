import os
import sys
import time

import requests
import argparse
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
from urllib.parse import urljoin, urlparse


def check_for_redirect(response):
    if response.history:
        raise requests.TooManyRedirects


def download_txt(url, url_params, filename, folder='books/'):
    os.makedirs(folder, exist_ok=True)
    book_url = requests.get(url, params=url_params)
    book_url.raise_for_status()
    check_for_redirect(book_url)
    with open(f"{folder}{sanitize_filename(filename)}.txt", "w") as my_file:
        my_file.write(book_url.text)
    return f"{folder}{sanitize_filename(filename)}.txt"


def download_image(url, folder='images/'):
    os.makedirs(folder, exist_ok=True)
    parsed_url = urlparse(url)
    picture_name = parsed_url.path.split('/')[-1]
    picture = requests.get(url)
    picture.raise_for_status()
    check_for_redirect(picture)
    with open(f"{folder}{picture_name}", "wb") as my_file:
        my_file.write(picture.content)
    return f"{folder}{picture_name}"


def parse_book_page(content, url):
    soup = BeautifulSoup(content.text, 'lxml')
    title_tag = soup.find('h1').text.split('::')
    picture_tag = soup.find('div', class_='bookimage').find('img')['src']
    title = title_tag[0].strip()
    author = title_tag[1].strip()
    picture_url = urljoin(url, picture_tag)
    comments = soup.find_all('div', class_="texts")
    comments_text = [comment.text.split(')')[-1] for comment in comments]
    genres = soup.find('span', class_='d_book').find_all('a')
    book_genres = [genre.text for genre in genres]
    book_attributes = {
        'title': title,
        'author': author,
        'cover': picture_url,
        'comments': comments_text,
        'genre': book_genres
    }
    return book_attributes


if __name__ == '__main__':
    command_arguments = argparse.ArgumentParser(description='скачивание книг с сайта https://tululu.org/ Необходимо '
                                                            'ввести обязательный аргументы - id с какого по какой '
                                                            'загружать')
    command_arguments.add_argument('start_id', help='с какого id начать загрузку', type=int)
    command_arguments.add_argument('end_id', help='на каком id закончить загрузку', type=int)
    args = command_arguments.parse_args()
    for book_id in range(args.start_id, args.end_id + 1):
        book_url = f'https://tululu.org/b{book_id}/'
        download_params = {'id': book_id}
        book_txt_url = 'https://tululu.org/txt.php'
        book_page_response = requests.get(book_url)
        book_page_response.raise_for_status()
        try:
            check_for_redirect(book_page_response)
            book_attributes = parse_book_page(book_page_response, book_url)
            download_image(book_attributes['cover'])
            download_txt(book_txt_url, download_params, f'{book_id}.{book_attributes["title"]}', folder='books/')
        except requests.TooManyRedirects:
            print(f'Книга с id{book_id} не доступна для загрузки')
        except requests.HTTPError as error:
            print(f'возникла ошибка {error}')
        except requests.ConnectionError as error:
            print(f'Ошибка сетевого соединения {error}. Перезапуск парсера через 2 минуты')
            time.sleep(120)

