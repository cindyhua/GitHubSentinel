import requests
from bs4 import BeautifulSoup
from datetime import datetime
import os
import json
from dateutil.parser import parse
from dateutil.relativedelta import relativedelta

class HackerNewsClient:
    def __init__(self):
        self.base_url = "https://news.ycombinator.com/"
        self.all_news_items = []

    def parse_relative_time(self, time_str):
        now = datetime.now()
        try:
            # 解析相对时间字符串
            delta = parse(time_str, fuzzy=True)
            if 'day' in time_str or 'hour' in time_str or 'minute' in time_str:
                # 如果是天、小时或分钟，使用relativedelta
                time_delta = relativedelta(days=delta.day-1, hours=delta.hour, minutes=delta.minute)
                return (now - time_delta).strftime("%Y-%m-%d %H:%M:%S")
            else:
                # 对于其他情况（如"5 months ago"），直接使用解析结果
                return (now - delta).strftime("%Y-%m-%d %H:%M:%S")
        except ValueError:
            # 如果解析失败，返回原始字符串
            return time_str

    def fetch_news(self, page=1):
        url = f"{self.base_url}news?p={page}"
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        news_items = []
        for item in soup.find_all('tr', class_='athing'):
            try:
                rank = item.find('span', class_='rank').text.strip('.')
                
                # 修改这里：使用更灵活的选择器来找到标题链接
                title_link = item.select_one('.titleline a')
                if title_link is None:
                    print(f"Warning: Could not find title link in item {item}")
                    continue
                
                title = title_link.text
                url = title_link['href']
                
                # Get the source (domain) from the URL
                source = url.split('/')[2] if url.startswith('http') else 'news.ycombinator.com'
                
                subtext = item.find_next_sibling('tr').find('td', class_='subtext')
                score = subtext.find('span', class_='score').text if subtext.find('span', class_='score') else 'N/A'
                author = subtext.find('a', class_='hnuser').text if subtext.find('a', class_='hnuser') else 'N/A'
                time_ago = subtext.find('span', class_='age').text if subtext.find('span', class_='age') else 'N/A'
                
                # 转换相对时间为具体时间点
                specific_time = self.parse_relative_time(time_ago)
                
                news_items.append({
                    'rank': int(rank),
                    'title': title,
                    'url': url,
                    'source': source,
                    'score': score,
                    'author': author,
                    'time': specific_time
                })
            except AttributeError as e:
                print(f"Error parsing item: {e}")
                continue
        
        self.all_news_items.extend(news_items)
        return news_items

    def save_to_file(self):
        # Create the hacknews_progress folder if it doesn't exist
        folder_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'hacknews_progress')
        os.makedirs(folder_path, exist_ok=True)

        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"hacker_news_{timestamp}.json"
        file_path = os.path.join(folder_path, filename)

        # Save all news items to the file
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(self.all_news_items, f, ensure_ascii=False, indent=2)

        print(f"Saved all news items to {file_path}")

    def print_news(self, news_items):
        for item in news_items:
            print(f"Rank: {item['rank']}")
            print(f"Title: {item['title']}")
            print(f"URL: {item['url']}")
            print(f"Score: {item['score']}")
            print(f"Author: {item['author']}")
            print(f"Time: {item['time']}")
            print("---")

    def save_to_markdown(self):
        # Create the hacknews_progress folder if it doesn't exist
        folder_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'hacknews_progress')
        os.makedirs(folder_path, exist_ok=True)

        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"hacker_news_{timestamp}.md"
        file_path = os.path.join(folder_path, filename)

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(f"# Hack News Top List\n")
            f.write(f"生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

            for item in self.all_news_items:
                f.write(f"## {item['title']}\n")
                f.write(f"当前排名：{item['rank']}\n\n")
                f.write(f"来源：{item['url']}\n\n")
                f.write(f"分数：{item['score']}\n\n")
                f.write(f"时间：{item['time']}\n\n")
                f.write("---\n\n")  # 添加分隔线

        print(f"Saved Markdown file to {file_path}")
        return file_path

    def fetch_and_save(self, from_page=1, to_page=2):
        self.all_news_items = []  # 重置新闻列表
        for page in range(from_page, to_page + 1):
            print(f"Fetching page {page}...")
            news = self.fetch_news(page)
            if news:
                self.print_news(news)
                print(f"Fetched news from page {page}")
            else:
                print(f"No news found on page {page}")
        
        if self.all_news_items:
            print(f"Saved news from pages {from_page} to {to_page} to Markdown file.")
            return self.save_to_markdown()
        else:
            print("No news items were fetched.")
            return None

if __name__ == "__main__":
    client = HackerNewsClient()
    client.fetch_and_save(from_page=1, to_page=3)  # 示例：获取第1页到第3页的新闻并保存
