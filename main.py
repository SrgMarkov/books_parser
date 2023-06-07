import os
import requests

url = 'https://tululu.org/txt.php?'
os.makedirs('books', exist_ok=True)
for book in range(1, 11):
    book_id = {'id': f'{book}'}
    book_url = requests.get(url, params=book_id)
    book_url.raise_for_status()

    with open(f"books/{book_id['id']}.txt", "w") as my_file:
        my_file.write(book_url.text)
