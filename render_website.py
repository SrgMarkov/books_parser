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

    with open("books/books_description.json", "r") as descriptions_file:
        descriptions = descriptions_file.read()

    books_descriptions = json.loads(descriptions)

    books_attributes = []
    for book in books_descriptions:
        cover = book['cover'].split('/')[-1]
        attribute = {
            'title': book['title'],
            'author': book['author'],
            'cover': f'./books/books_covers/{cover}'
        }
        books_attributes.append(attribute)
    chunked_books_attributes = list(chunked(books_attributes, 2))

    rendered_page = template.render(books=chunked_books_attributes)

    with open('index.html', 'w', encoding="utf8") as file:
        file.write(rendered_page)

    print("Site rebuilt")


on_reload()
server = Server()
server.watch('template.html', on_reload)
server.serve(root='.')
