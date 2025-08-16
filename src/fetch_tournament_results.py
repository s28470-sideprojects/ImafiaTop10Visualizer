import bs4
import re
import csv
from bs4.element import PageElement, Tag
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

games_items = soup.find('div', class_='games_items')


games_item_titles = games_items.find_all(
    name='div', class_='games_item_title')
games_item_contents = games_items.find_all(
    name='div', class_='games_item_content')


def extract_game_data(title: Tag, content: Tag):
    game_name: Tag = title.find('div', class_='games_item_name')
    name = game_name.get_text(strip=True)
    tour = re.search(r"#(\d+)", name)
    tour_number = tour.group(1) if tour else None
    game_data = []
    for row in content.find_all('div', class_='games_item_tr'):
        row_table_data = row.find_all('div', class_='games_item_td')
        points = row_table_data[2].get_text(strip=True)
        nickname = row_table_data[3].get_text(strip=True)
        points = re.sub(r"\(.*?\)", '', points)
        points_sum = sum(float(point) for point in points.split('/'))
        game_data.append({
            'tour': tour_number,
            'nickname': nickname,
            'points': points_sum
        })
    return game_data


games_with_extracted_data = []
for title, content in zip(games_item_titles, games_item_contents):
    extracted = extract_game_data(title, content)
    games_with_extracted_data.append(extracted)

print(games_with_extracted_data)
