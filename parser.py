import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import csv

KEYWORDS = ['дизайн', 'фото', 'web', 'python']

def contains_keywords(text, keywords):
    return any(keyword.lower() in text.lower() for keyword in keywords)

def get_articles(base_url, keywords, days=5):
    articles = []
    today = datetime.now()
    start_date = today - timedelta(days=days)

    for page in range(1, 6):
        url = f"{base_url}page{page}/"
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        articles_list = soup.find('div', class_='tm-articles-list')
        if not articles_list:
            continue

        for article in articles_list.find_all('article'):
            time_tag = article.find('time')
            if not time_tag:
                continue
            date_str = time_tag['datetime']
            article_date = datetime.strptime(date_str.split('T')[0], '%Y-%m-%d')

            if article_date < start_date:
                continue

            title_elem = article.find('h2').find('a', class_='tm-title__link')
            if not title_elem:
                continue
            title = title_elem.get_text(strip=True)
            link = f"https://habr.com{title_elem['href']}"

            if contains_keywords(title, keywords):
                articles.append({
                    'date': article_date.strftime('%Y-%m-%d'),
                    'title': title,
                    'link': link
                })
    return articles

def save_to_csv(articles, filename):
    with open(filename, mode='w', encoding='utf-8', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=['date', 'title', 'link'])
        writer.writeheader()
        writer.writerows(articles)

if __name__ == "__main__":
    base_url = "https://habr.com/ru/articles/"
    output_file = "habr_parser2.csv"
    articles = get_articles(base_url, KEYWORDS, days=5)

    if articles:
        print(f"Найдено {len(articles)} статей.")
        save_to_csv(articles, output_file)
        print(f"Данные успешно сохранены в {output_file}")
    else:
        print("Статьи не найдены.")
