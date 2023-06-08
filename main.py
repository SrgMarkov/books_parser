import os
import requests
import argparse
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
from urllib.parse import urljoin, urlparse


def check_for_redirect(response):
    if response.history:
        raise requests.HTTPError


def download_txt(url, filename, folder='books/'):
    os.makedirs(folder, exist_ok=True)
    book_url = requests.get(url)
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


def parse_book_page(content):
    soup = BeautifulSoup(content.text, 'lxml')
    title_tag = soup.find('h1').text.split('::')
    picture_tag = soup.find('div', class_='bookimage').find('img')['src']
    title = title_tag[0].strip()
    author = title_tag[1].strip()
    picture_url = urljoin(url, picture_tag)
    comments = soup.find_all('div', class_="texts")
    comments_text = []
    for comment in comments:
        comment_text = comment.text.split(')')[-1]
        comments_text.append(comment_text)
    genres = soup.find('span', class_='d_book').find_all('a')
    book_genres = []
    for genre in genres:
        book_genres.append(genre.text)
    book_info = {
        'Заголовок': title,
        'Автор': author,
        'Обложка': picture_url,
        'Комментарии': comments_text,
        'Жанр': book_genres
    }
    return book_info


if __name__ == '__main__':
    command_arguments = argparse.ArgumentParser(description='скачивание книг с сайта https://tululu.org/ Необходимо '
                                                            'ввести обязательный аргументы - id с какого по какой '
                                                            'загружать')
    command_arguments.add_argument('start_id', help='с какого id начать загрузку', type=int)
    command_arguments.add_argument('end_id', help='на каком id закончить загрузку', type=int)
    args = command_arguments.parse_args()
    for book in range(args.start_id, args.end_id + 1):
        url = f'https://tululu.org/b{book}/'
        download_url = f'https://tululu.org/txt.php?id={book}'
        response = requests.get(url)
        response.raise_for_status()
        try:
            check_for_redirect(response)
            book_info = parse_book_page(response)
            download_image(book_info['Обложка'])
            download_txt(download_url, f'{book}.{book_info["Заголовок"]}', folder='books/')
        except requests.HTTPError:
            pass
