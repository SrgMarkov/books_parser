from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup
from main import parse_book_page, download_image, download_txt, save_book_description

SITE_URL = 'https://tululu.org'
BOOK_TEXT_URL = 'https://tululu.org/txt.php'


def get_book_by_category_urls(url):
    books_pages = []
    for page in range(1, 2):
        category = f'/l55/{page}'
        books_category_url = urljoin(url, category)
        books_category_response = requests.get(books_category_url)
        books_category_response.raise_for_status()
        soup = BeautifulSoup(books_category_response.text, 'lxml')
        books_in_category = soup.select("table.d_book")
        books_pages = [book.select_one("a")['href'].strip('/') for book in books_in_category]
    return books_pages


for book_id in get_book_by_category_urls(SITE_URL):
    download_params = {'id': book_id.replace('b', '')}
    book_page_response = requests.get(urljoin(SITE_URL, book_id))
    book_page_response.raise_for_status()
    try:
        book_attributes = parse_book_page(book_page_response, urljoin(SITE_URL, book_id))
        download_image(book_attributes['cover'], book_attributes['title'])
        book_id = book_id.replace("b", "")
        download_txt(BOOK_TEXT_URL, download_params, f'{book_id} - {book_attributes["title"]}',
                     folder='books/')
        save_book_description(book_id, book_attributes)
    except requests.TooManyRedirects:
        print(f'Книга с id{book_id} не доступна для загрузки')

