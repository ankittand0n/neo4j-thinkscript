import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from urllib.parse import urljoin
from datetime import datetime
from ..items import ThinkscriptItem

class ThinkScriptSpider(CrawlSpider):
    name = 'thinkscript'
    allowed_domains = ['toslc.thinkorswim.com']
    start_urls = ['https://toslc.thinkorswim.com/center/reference/thinkScript']
    
    # Rules for following links
    rules = (
        # Follow links within the same domain and specific paths
        Rule(
            LinkExtractor(
                allow=(
                    'toslc.thinkorswim.com/center/reference/thinkScript',
                    'toslc.thinkorswim.com/center/reference/thinkScript/.*',
                    'toslc.thinkorswim.com/center/reference/thinkScript/functions/.*',
                    'toslc.thinkorswim.com/center/reference/thinkScript/constants/.*',
                    'toslc.thinkorswim.com/center/reference/thinkScript/operators/.*',
                    'toslc.thinkorswim.com/center/reference/thinkScript/declarations/.*',
                    'toslc.thinkorswim.com/center/reference/thinkScript/reserved-words/.*'
                ),
                deny=('wp-admin', 'wp-login', 'feed', 'comment', 'tag', 'category', 'author', 'page')
            ),
            callback='parse_page',
            follow=True
        ),
    )

    def parse_page(self, response):
        """Parse each page and extract relevant information."""
        # Debug logging
        self.logger.info(f"Parsing page: {response.url}")
        
        # Skip if not a content page
        if not response.css('main') and not response.css('.content'):
            self.logger.debug(f"Skipping non-content page: {response.url}")
            return

        item = ThinkscriptItem()
        
        # Extract title - try multiple selectors
        title = response.css('h1::text').get()
        if not title:
            title = response.css('.page-title::text').get()
        if not title:
            title = response.css('.content h1::text').get()
        item['title'] = title
        
        # Extract content - try multiple selectors
        content = []
        content.extend(response.css('main p::text').getall())
        content.extend(response.css('.content p::text').getall())
        content.extend(response.css('article p::text').getall())
        item['content'] = ' '.join([c.strip() for c in content if c.strip()])
        
        # Extract code examples - try multiple selectors
        code_blocks = []
        code_blocks.extend(response.css('pre code::text').getall())
        code_blocks.extend(response.css('.content pre code::text').getall())
        code_blocks.extend(response.css('main pre code::text').getall())
        item['code_blocks'] = [code.strip() for code in code_blocks if code.strip()]
        
        # Extract navigation links
        nav_links = response.css('nav a::attr(href)').getall()
        nav_links = [urljoin(response.url, link) for link in nav_links]
        
        # Extract content links
        content_links = response.css('main a::attr(href)').getall()
        content_links = [urljoin(response.url, link) for link in content_links]
        
        # Combine all links
        item['links'] = list(set(nav_links + content_links))  # Remove duplicates
        
        # Add metadata
        item['url'] = response.url
        item['crawled_at'] = datetime.now().isoformat()
        
        # Debug logging
        self.logger.info(f"Found content: Title={bool(title)}, Content length={len(item['content'])}, Code blocks={len(item['code_blocks'])}")
        
        yield item

    def closed(self, reason):
        """Called when spider is closed."""
        self.logger.info('Spider closed: %s', reason) 