import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# 添加 src 目录到 Python 路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from hackernews_client import HackerNewsClient

class TestHackerNewsClient(unittest.TestCase):

    def setUp(self):
        self.client = HackerNewsClient()

    @patch('src.hackernews_client.requests.get')
    def test_fetch_news(self, mock_get):
        # 模拟 requests.get 的返回值
        mock_response = MagicMock()
        mock_response.text = '''
        <html>
            <tr class="athing">
                <td class="title">
                    <span class="rank">1.</span>
                    <a class="titlelink" href="https://example.com">Test Title</a>
                </td>
            </tr>
            <tr>
                <td class="subtext">
                    <span class="score">100 points</span>
                    <a class="hnuser">testuser</a>
                    <span class="age">1 hour ago</span>
                </td>
            </tr>
        </html>
        '''
        mock_get.return_value = mock_response

        news = self.client.fetch_news()

        self.assertEqual(len(news), 1)
        self.assertEqual(news[0]['rank'], '1')
        self.assertEqual(news[0]['title'], 'Test Title')
        self.assertEqual(news[0]['url'], 'https://example.com')
        self.assertEqual(news[0]['score'], '100 points')
        self.assertEqual(news[0]['author'], 'testuser')
        self.assertEqual(news[0]['time'], '1 hour ago')

    @patch('src.hackernews_client.requests.get')
    def test_fetch_news_with_page(self, mock_get):
        mock_response = MagicMock()
        mock_response.text = '<html></html>'  # 简化的响应
        mock_get.return_value = mock_response

        self.client.fetch_news(page=2)

        mock_get.assert_called_once_with('https://news.ycombinator.com/news?p=2')

    def test_print_news(self):
        news_items = [{
            'rank': '1',
            'title': 'Test Title',
            'url': 'https://example.com',
            'score': '100 points',
            'author': 'testuser',
            'time': '1 hour ago'
        }]

        with patch('builtins.print') as mock_print:
            self.client.print_news(news_items)
            mock_print.assert_called()

if __name__ == '__main__':
    unittest.main()
