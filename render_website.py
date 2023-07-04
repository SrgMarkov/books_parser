import json
from http.server import HTTPServer, SimpleHTTPRequestHandler
from jinja2 import Environment, FileSystemLoader, select_autoescape

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

rendered_page = template.render(books=books_attributes)

with open('index.html', 'w', encoding="utf8") as file:
    file.write(rendered_page)

server = HTTPServer(('0.0.0.0', 8000), SimpleHTTPRequestHandler)
server.serve_forever()
