import math
import os
import json
from jinja2 import Environment, FileSystemLoader, select_autoescape
from livereload import Server
from more_itertools import chunked
from dotenv import load_dotenv
from urllib.parse import quote


BOOKS_IN_PAGE = 10
BOOKS_COLUMNS = 2


def on_reload():
    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html', 'xml'])
    )
    load_dotenv()
    description_folder = os.getenv('FOLDER', default='data')
    template = env.get_template('template.html')
    os.makedirs('pages', exist_ok=True)

    with open(f'{description_folder}/books_description.json', 'r') as descriptions_file:
        books_descriptions = json.load(descriptions_file)

    pages = list(chunked(books_descriptions, BOOKS_IN_PAGE))
    pages_amount = math.ceil(len(books_descriptions) / len(pages))
    for page, books in enumerate(pages, start=1):
        books_attributes = []
        for book in books:
            cover = book['cover'].split('/')[-1]
            book_file = f'{book["id"]}.txt'
            attribute = {
                'title': book['title'],
                'author': book['author'],
                'cover': quote(f'../media/books_covers/{cover}'),
                'text': quote(f'../media/books_txt/{book_file}'),
                'genre': book['genre']
            }
            books_attributes.append(attribute)
        chunked_books_attributes = list(chunked(books_attributes, BOOKS_COLUMNS))
        rendered_page = template.render(books=chunked_books_attributes, amount=pages_amount, current_page=page)

        with open(f'pages/index_{page}.html', 'w', encoding='utf8') as file:
            file.write(rendered_page)


def main():
    on_reload()
    server = Server()
    server.watch('template.html', on_reload)
    server.serve(root='.')


if __name__ == '__main__':
    main()
