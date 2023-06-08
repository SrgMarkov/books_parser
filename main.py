import os
import requests
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename


def check_for_redirect(response):
    if response.history:
        raise requests.HTTPError


def download_txt(url, filename, folder='books/'):
    os.makedirs(folder, exist_ok=True)
    book_url = requests.get(url)
    book_url.raise_for_status()
    try:
        check_for_redirect(book_url)
        with open(f"{folder}{sanitize_filename(filename)}.txt", "w") as my_file:
            my_file.write(book_url.text)
        return f"{folder}{sanitize_filename(filename)}.txt"
    except requests.HTTPError:
        print(f"book is not available")


for book in range(1, 11):
    url = f'https://tululu.org/b{book}/'
    download_url = f'https://tululu.org/txt.php?id={book}'
    response = requests.get(url)
    response.raise_for_status()
    try:
        check_for_redirect(response)
        soup = BeautifulSoup(response.text, 'lxml')
        title_tag = soup.find('h1').text.split('::')
        title = title_tag[0].strip()
        author = title_tag[1].strip()
        download_txt(download_url, f'{book}. {title}', folder='books/')
    except requests.HTTPError:
        print(f"book is not available")
