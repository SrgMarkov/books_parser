import os
import time
import requests
import argparse
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse


def check_for_redirect(response):
    if response.history:
        raise requests.TooManyRedirects


def download_txt(url, url_params, filename, folder):
    os.makedirs(f'{folder}/books_txt', exist_ok=True)
    book_text = requests.get(url, params=url_params)
    book_text.raise_for_status()
    check_for_redirect(book_text)
    with open(f"{folder}/books_txt/{filename}.txt", "w") as book_txt:
        book_txt.write(book_text.text)


def download_image(url, title, folder):
    os.makedirs(f'{folder}/books_covers', exist_ok=True)
    parsed_url = urlparse(url)
    picture_name = parsed_url.path.split('/')[-1]
    readable_picture_name = f'{picture_name.split(".")[0]} - {title}.{picture_name.split(".")[-1]}'
    picture = requests.get(url)
    picture.raise_for_status()
    check_for_redirect(picture)
    with open(f"{folder}/books_covers/{readable_picture_name}", "wb") as book_cover:
        book_cover.write(picture.content)


def parse_book_page(content, url):
    soup = BeautifulSoup(content.text, 'lxml')
    title, author = soup.select('h1')[0].get_text().split(' \xa0 :: \xa0 ')
    picture_url = urljoin(url, soup.select("div.bookimage a img")[0]['src'])
    comments = [comment.get_text() for comment in soup.select("div.texts span")]
    genres = [genre.get_text() for genre in soup.select("span.d_book a")]
    book_attributes = {
        'title': title,
        'author': author,
        'cover': picture_url,
        'comments': comments,
        'genre': genres
    }
    return book_attributes


if __name__ == '__main__':
    command_arguments = argparse.ArgumentParser(description='скачивание книг с сайта https://tululu.org/ Необходимо '
                                                            'ввести обязательный аргументы - id с какого по какой '
                                                            'загружать')
    command_arguments.add_argument('start_id', help='с какого id начать загрузку', type=int)
    command_arguments.add_argument('end_id', help='на каком id закончить загрузку', type=int)
    command_arguments.add_argument('--dest_folder', help='указать папку для загрузки', default='books')
    command_arguments.add_argument('--skip_imgs', help='не скачивать обложки книг',
                                   default=False, action='store_const', const=True)
    command_arguments.add_argument('--skip_txt', help='не скачивать текст книг',
                                   default=False, action='store_const', const=True)
    args = command_arguments.parse_args()
    for book_id in range(args.start_id, args.end_id + 1):
        book_url = f'https://tululu.org/b{book_id}/'
        download_params = {'id': book_id}
        book_txt_url = 'https://tululu.org/txt.php'
        connection_failure = False
        while True:
            try:
                book_page_response = requests.get(book_url)
                book_page_response.raise_for_status()
                check_for_redirect(book_page_response)
                book_attributes = parse_book_page(book_page_response, book_url)
                if not args.skip_imgs:
                    download_image(book_attributes['cover'], book_attributes["title"], args.dest_folder)
                if not args.skip_txt:
                    download_txt(book_txt_url, download_params, f'{book_id} - {book_attributes["title"]}',
                                 args.dest_folder)
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
