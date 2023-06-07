import requests

url = 'https://tululu.org/txt.php?id=32168'
book = requests.get(url)
print(book.text)