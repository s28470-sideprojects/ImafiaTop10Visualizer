# All comments/messages in code are in English only.
import bs4
import re
import csv
from bs4.element import Tag
import requests
import os
from pathlib import Path
import re


def to_snake_case(name: str) -> str:
    """Convert a string to snake_case: lowercase, spaces and non-alphanum -> underscores"""
    name = name.lower()
    name = re.sub(r'[^a-z0-9]+', '_', name)   # replace non-alphanum with _
    name = re.sub(r'_+', '_', name)           # collapse multiple _
    return name.strip('_')


def parse_tournament(url: str, out_basename: str | Path | None = None):
    """Download tournament page, parse games and save to CSV"""
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

    # if no out_basename provided -> build from og:title
    if out_basename is None:
        title_meta = soup.find("meta", property="og:title")
        if title_meta and "content" in title_meta.attrs:
            out_basename = "data/" + to_snake_case(title_meta["content"])
        else:
            out_basename = "data/tournament_results"

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
    out_path = Path(out_basename).with_suffix(".csv")
    with open(out_path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["tour", "nickname", "points"])
        writer.writeheader()
        writer.writerows(all_rows)

    return all_rows, out_path


if __name__ == '__main__':
    # URL of the tournament
    url = 'https://imafia.org/tournament/387#tournament-results'

    # Example usage
    data, path = parse_tournament(url)
    print(f"Saved {len(data)} rows to {path}")
