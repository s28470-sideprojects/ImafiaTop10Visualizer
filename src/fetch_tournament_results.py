import bs4
import re
import csv
import requests

# URL турнира
url = 'https://imafia.org/tournament/387#tournament-results'

# Стандартный Mozilla User-Agent
headers = {
    'User-Agent': (
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) '
        'Gecko/20100101 Firefox/128.0'
    )
}

# Загружаем страницу
response = requests.get(url, headers=headers)
response.raise_for_status()  # если ошибка — сразу упадёт
html = response.text

soup = bs4.BeautifulSoup(html, 'html.parser')
