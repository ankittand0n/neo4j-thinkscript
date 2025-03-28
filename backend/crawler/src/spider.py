import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from urllib.parse import urljoin
import json
from datetime import datetime
from pathlib import Path
import os

class ThinkScriptSpider(CrawlSpider):
    name = 'thinkscript'
    allowed_domains = ['thinkscript.com']
    start_urls = [
        'https://thinkscript.com/docs/',
        'https://thinkscript.com/docs/thinkScript/',
        'https://thinkscript.com/docs/thinkScript/statements/',
        'https://thinkscript.com/docs/thinkScript/operators/',
        'https://thinkscript.com/docs/thinkScript/functions/'
    ]
    
    def __init__(self, *args, **kwargs):
        super(ThinkScriptSpider, self).__init__(*args, **kwargs)
        self.timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        # Get the project root directory (3 levels up from spider.py)
        self.project_root = Path(__file__).parent.parent.parent.parent
        self.data_dir = self.project_root / 'data' / 'crawls'
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.output_file = self.data_dir / f'thinkscript_data_{self.timestamp}.json'
        self.items = []
    
    # Rules for following links
    rules = (
        # Follow links within the same domain
        Rule(
            LinkExtractor(
                allow=('thinkscript.com/docs/',),
                deny=('wp-admin', 'wp-login', 'feed', 'comment', 'tag', 'category', 'search', 'login', 'register')
            ),
            callback='parse_page',
            follow=True
        ),
    )

    def parse_page(self, response):
        """Parse each page and extract relevant information."""
        # Extract title
        title = response.css('h1::text').get()
        
        # Extract content
        content = ' '.join(response.css('article p::text').getall())
        
        # Extract code examples
        code_blocks = response.css('pre code::text').getall()
        
        # Extract links to other pages
        links = response.css('a::attr(href)').getall()
        links = [urljoin(response.url, link) for link in links]
        
        # Create a unique identifier for this page
        page_id = f"{self.timestamp}_{hash(response.url)}"
        
        # Create metadata
        metadata = {
            'id': page_id,
            'url': response.url,
            'title': title,
            'content': content,
            'code_blocks': code_blocks,
            'links': links,
            'timestamp': self.timestamp,
            'crawl_date': datetime.now().isoformat()
        }
        
        self.items.append(metadata)
        yield metadata

    def closed(self, reason):
        """Called when spider is closed."""
        # Save all items to a JSON file
        with open(self.output_file, 'w') as f:
            json.dump(self.items, f, indent=2)
        
        print(f"\nCrawled data saved to: {self.output_file}")
        self.logger.info('Spider closed: %s', reason) 