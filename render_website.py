import os
import json
from jinja2 import Environment, FileSystemLoader, select_autoescape
from livereload import Server
from more_itertools import chunked


def on_reload():
    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html', 'xml'])
    )

    template = env.get_template('template.html')
    os.makedirs('pages', exist_ok=True)
    with open("books/books_description.json", "r") as descriptions_file:
        descriptions = descriptions_file.read()

    books_descriptions = json.loads(descriptions)

    books_pages = list(chunked(books_descriptions, 10))
    for count, books in enumerate(books_pages):
        books_attributes = []
        for book in books:
            cover = book['cover'].split('/')[-1]
            book_file = f'{cover.split(".")[0]}.txt'
            attribute = {
                'title': book['title'],
                'author': book['author'],
                'cover': f'../books/books_covers/{cover}',
                'text': f'../books/books_txt/{book_file}'
            }
            books_attributes.append(attribute)
        chunked_books_attributes = list(chunked(books_attributes, 2))
        rendered_page = template.render(books=chunked_books_attributes)

        with open(f'pages/index_{count + 1}.html', 'w', encoding="utf8") as file:
            file.write(rendered_page)

    print("Site rebuilt")


on_reload()
server = Server()
server.watch('template.html', on_reload)
server.serve(root='.')
