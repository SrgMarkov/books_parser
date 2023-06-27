from urllib.parse import urljoin
import requests

from bs4 import BeautifulSoup
from main import parse_book_page, download_image, download_txt, save_book_description


def get_book_by_category_urls(site_url):
    books_pages = []
    for page in range(1, 2):
        category = f'/l55/{page}'
        books_category_url = urljoin(site_url, category)
        books_category_response = requests.get(books_category_url)
        books_category_response.raise_for_status()
        soup = BeautifulSoup(books_category_response.text, 'lxml')
        books_in_category = soup.find_all('table', class_='d_book')
        books_pages = [book.find('a')['href'].strip('/') for book in books_in_category]
    return books_pages


site_url = 'https://tululu.org'
book_txt_url = 'https://tululu.org/txt.php'

for book_id in get_book_by_category_urls(site_url):
    download_params = {'id': book_id.replace('b', '')}
    book_page_response = requests.get(urljoin(site_url, book_id))
    book_page_response.raise_for_status()
    try:
        book_attributes = parse_book_page(book_page_response, urljoin(site_url, book_id))
        download_image(book_attributes['cover'], book_attributes['title'])
        book_id = book_id.replace("b", "")
        download_txt(book_txt_url, download_params, f'{book_id}.{book_attributes["title"]}',
                     folder='books/')
        save_book_description(book_id, book_attributes)
    except requests.TooManyRedirects:
        print(f'Книга с id{book_id} не доступна для загрузки')

