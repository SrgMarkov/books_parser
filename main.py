import os
import requests
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


for book in range(1, 11):
    url = f'https://tululu.org/b{book}/'
    download_url = f'https://tululu.org/txt.php?id={book}'
    response = requests.get(url)
    response.raise_for_status()
    try:
        check_for_redirect(response)
        soup = BeautifulSoup(response.text, 'lxml')
        title_tag = soup.find('h1').text.split('::')
        picture_tag = soup.find('div', class_='bookimage').find('img')['src']
        title = title_tag[0].strip()
        author = title_tag[1].strip()
        picture_url = urljoin(url, picture_tag)
        comments = soup.find_all('div', class_="texts")
        print(f'Заголовок: {title}')
        # for comment in comments:
        #     comment_text = comment.text.split(')')[-1]
        #     print(comment_text)
        genres = soup.find('span', class_='d_book').find_all('a',)
        for genre in genres:
            print(genre.text)
        print()
        # download_image(picture_url)
        # download_txt(download_url, f'{book}. {title}', folder='books/')
    except requests.HTTPError:
        pass
