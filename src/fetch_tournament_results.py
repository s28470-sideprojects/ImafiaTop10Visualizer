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

class_with_game_result = 'games_item'
class_game_row = 'games_item_tr'
class_tour_name = 'games_item_title'


def parse_tour_name(div):
    tour_div = div.find('div', class_=class_tour_name)
    if tour_div:
        match = re.search(r'Гра\s*#(\d+)', tour_div.get_text())
        return int(match.group(1)) if match else None
    return None


def parse_player_row(row):
    cols = row.find_all(class_='games_item_td')
    if len(cols) < 4:
        return None

    score_text = cols[2].get_text(strip=True)  # "1/0.4"
    try:
        before, after = score_text.split('/')
        score_sum = float(before) + float(after)
    except ValueError:
        score_sum = None

    a_tag = cols[3].find('a')
    if a_tag:
        name = a_tag.get_text(strip=True)
        href = a_tag.get('href', '')
        player_id = href.split('/u/')[-1] if '/u/' in href else None
    else:
        name, player_id = '', None

    return {
        'name': name,
        'player_id': player_id,
        'score_sum': score_sum
    }


divs = soup.find_all('div', class_=class_with_game_result)

results = []

for div in divs:
    tour_name = parse_tour_name(div)
    rows = div.find_all('div', class_=class_game_row)
    for row in rows:
        player_data = parse_player_row(row)
        if player_data:
            player_data['tour'] = tour_name
            results.append(player_data)

with open('data/tournament_results.csv', 'w', newline='', encoding='utf-8') as csvfile:
    fieldnames = ['tour', 'name', 'player_id', 'score_sum']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(results)

print("Сохранено в data/tournament_results.csv (перезаписано)")
