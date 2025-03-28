# Scrapy settings for ThinkScript crawler

BOT_NAME = 'thinkscript_crawler'

SPIDER_MODULES = ['thinkscript_crawler.spiders']
NEWSPIDER_MODULE = 'thinkscript_crawler.spiders'

# Crawl responsibly by identifying yourself (and your website) to web servers
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'

# Obey robots.txt rules
ROBOTSTXT_OBEY = True

# Configure maximum concurrent requests performing at the same time to the same domain
CONCURRENT_REQUESTS_PER_DOMAIN = 1

# Configure a delay for requests for the same website
DOWNLOAD_DELAY = 5  # Increased delay to be more respectful

# Enable or disable downloader middlewares
DOWNLOADER_MIDDLEWARES = {
    'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
    'scrapy.downloadermiddlewares.retry.RetryMiddleware': 90,
    'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 110,
}

# Configure item pipelines
ITEM_PIPELINES = {
    'thinkscript_crawler.pipelines.ThinkscriptPipeline': 300,
}

# Enable and configure logging
LOG_LEVEL = 'DEBUG'
LOG_FORMAT = '%(asctime)s [%(name)s] %(levelname)s: %(message)s'

# Configure output format
FEED_FORMAT = 'json'
FEED_URI = 'output/thinkscript_data.json'

# Configure maximum depth for crawling
DEPTH_LIMIT = 3

# Configure output encoding
FEED_EXPORT_ENCODING = 'utf-8'

# Configure retry settings
RETRY_ENABLED = True
RETRY_TIMES = 3
RETRY_HTTP_CODES = [500, 502, 503, 504, 522, 524, 408, 429]

# Configure timeout settings
DOWNLOAD_TIMEOUT = 15

# Configure cookies
COOKIES_ENABLED = True

# Configure maximum response size
DOWNLOAD_MAXSIZE = 1073741824  # 1GB

# Configure response encoding
FEED_EXPORT_INDENT = 2 