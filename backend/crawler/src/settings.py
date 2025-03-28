# Scrapy settings for ThinkScript crawler

BOT_NAME = 'thinkscript_crawler'

SPIDER_MODULES = ['src.crawler.spider']
NEWSPIDER_MODULE = 'src.crawler.spider'

# Crawl responsibly by identifying yourself (and your website) to web servers
USER_AGENT = 'ThinkScript Crawler (+https://github.com/yourusername/neo4j-thinkscript)'

# Obey robots.txt rules
ROBOTSTXT_OBEY = True

# Configure maximum concurrent requests performing at the same time to the same domain
CONCURRENT_REQUESTS_PER_DOMAIN = 1

# Configure a delay for requests for the same website
DOWNLOAD_DELAY = 2

# Enable or disable downloader middlewares
DOWNLOADER_MIDDLEWARES = {
    'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
    'scrapy.downloadermiddlewares.retry.RetryMiddleware': 90,
    'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 110,
}

# Configure item pipelines
ITEM_PIPELINES = {
    'src.crawler.pipelines.ThinkScriptPipeline': 300,
}

# Enable and configure logging
LOG_LEVEL = 'INFO'

# Configure output format
FEED_FORMAT = 'json'
FEED_URI = 'output/thinkscript_data.json'

# Configure maximum depth for crawling
DEPTH_LIMIT = 3

# Configure output encoding
FEED_EXPORT_ENCODING = 'utf-8' 