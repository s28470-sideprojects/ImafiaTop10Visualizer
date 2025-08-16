# All comments/messages in code are in English only.
import bs4
import re
import csv
from bs4.element import Tag
import requests
import os


def parse_tournament(url: str):
    """Download tournament page, parse games and save to data/tournament_results.csv"""
    headers = {
        'User-Agent': (
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) '
            'Gecko/20100101 Firefox/128.0'
        )
    }

    response = requests.get(url, headers=headers)
    response.raise_for_status()
    html = response.text

    soup = bs4.BeautifulSoup(html, 'html.parser')
    games_items = soup.find('div', class_='games_items')

    games_item_titles = games_items.find_all('div', class_='games_item_title')
    games_item_contents = games_items.find_all(
        'div', class_='games_item_content')

    def extract_game_data(title: Tag, content: Tag):
        game_name: Tag = title.find('div', class_='games_item_name')
        name = game_name.get_text(strip=True)
        tour = re.search(r"#(\d+)", name)
        tour_number = int(tour.group(1)) if tour else None
        game_data = []
        for row in content.find_all('div', class_='games_item_tr'):
            row_table_data = row.find_all('div', class_='games_item_td')
            points = row_table_data[2].get_text(strip=True)
            nickname = row_table_data[3].get_text(strip=True)
            points = re.sub(r"\(.*?\)", '', points)
            points_sum = sum(float(point) for point in points.split('/'))
            points_sum = round(points_sum, 1)
            game_data.append({
                'tour': tour_number,
                'nickname': nickname,
                'points': points_sum
            })
        return game_data

    # collect all rows flat
    all_rows = []
    for title, content in zip(games_item_titles, games_item_contents):
        all_rows.extend(extract_game_data(title, content))

    # ensure data directory exists
    os.makedirs("data", exist_ok=True)

    # save to CSV
    csv_file = os.path.join("data", "tournament_results.csv")
    with open(csv_file, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["tour", "nickname", "points"])
        writer.writeheader()
        writer.writerows(all_rows)

    return all_rows


# URL турнира
url = 'https://imafia.org/tournament/387#tournament-results'

# Example usage
data = parse_tournament(url)
print(f"Saved {len(data)} rows to data/tournament_results.csv")
