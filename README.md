## Парсинг электронной библиотеки

Данный скрипт позволяет скачивать книги с сервиса [tululu.org](https://tululu.org/) 
 
### Как установить

- должен быть установлен Python3
- Установить зависимости командой
```
pip install -r requirements.txt
```
### Как запустить

#### Парсинг по id книги

Передать в качестве аргумента в командной строке id книги с которой начинать скачивание, а так же id на которой закончить. По умолчанию книги сохраняются в папку `books`, обложки книг (если они есть) в папку `images`. 

Например:

```
python3 main.py 10 20
```
сохранит книги от id10 до id20если такие доступны для скачивания

#### Парсинг по категории

Реализован парсинг по категории *Научная фантастика*, для запуска парсера необходимо ввести:

```
python3 parse_tululu_category.py
```
По данной команде будут скачены все книги данной категории. Можно ограничить скачивание указав аргументом страницу начала `--start_page` и окончания `--end_page` загрузки. Например:

```
python3 parse_tululu_category.py --start_page 10 --end_page 15
```
сохранит все книги, расположенные с 10 по 15 страницы категории

### Дополнительные аргументы

Можно указать необязательные аргументы:

- `--dest_folder ExampeFolder` - папка для загрузки, по умолчанию **books**
- `--skip_imgs True` - не загружать обложки книг
- `--skip_txt True` - не загружать текст книг


### Основные функции

**check_for_redirect** - Проверяет есть ли редирект при обращении к ссылке

**download_txt** - скачивание книги в формате txt, по умолчанию в папку books

**download_image** - скачивание обложки книги, по умолчанию в папку image

**parse_book_page** - создает словарь с информацией о книге в виде словаря (название, автор, ссылка на картинку обложки, комментарии, жанр)

**save_book_description** - скачивает json файл с описанием книги

**get_book_id_by_category** - получает список id книг в необходимой категории

### Просмотр книг

#### Файл с описанием
Необходимо указать путь к файлу с описанием книг. Для этого создайте рядом с `render_website.py` файл `.env` и пропишите путь:
```
DESCRIPTION_FILE=/Users/ExampleUser/Downloads/books_description.json
```
По умолчанию установлен файл `data/books_description.json`

#### Запуск сайта

Для создания страниц с книгами запустите команду
```
python3 render_website.py
```

Для просмотра - откройте в браузере файл `index_1.html` в папке pages или перейдите по [cсылке](http://127.0.0.1:5500/pages/index_1.html) 

Пример рабочего сайта можно посмотреть [по данной ссылке на Github Pages](https://srgmarkov.github.io/books_parser/pages/index_1.html)
