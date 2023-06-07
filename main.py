import os
import requests


def check_for_redirect(response):
    if response.history:
        raise requests.HTTPError


url = 'https://tululu.org/txt.php?'
os.makedirs('books', exist_ok=True)
for book in range(1, 11):
    book_id = {'id': f'{book}'}
    book_url = requests.get(url, params=book_id)
    book_url.raise_for_status()
    try:
        check_for_redirect(book_url)
        with open(f"books/id{book_id['id']}.txt", "w") as my_file:
            my_file.write(book_url.text)
    except requests.HTTPError:
        print(f"book id{book_id['id']} is not available")



