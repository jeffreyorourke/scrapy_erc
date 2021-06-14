# -*- coding: utf-8 -*-

primaryspidername = 'erc'

import os
POSTGRES_USER = os.getenv('POSTGRES_USER')
POSTGRES_PASS = os.getenv('POSTGRES_PASS')
PORT = 5432
DB = "scrapy_cancan"
dbschema = 'erc'  #refer also to dbschema variable assignment in models.py

POSTGRES_HOST = os.getenv('LENOVO_CHARCOAL_HOST')
# POSTGRES_HOST = os.getenv('LENOVO_GREY_HOST')
# POSTGRES_HOST = os.getenv('VAIO_HOST')

CONNECTION_STRING = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASS}@{POSTGRES_HOST}:{PORT}/{DB}"
# scrapy-min Conda environment uses 1.3.6 to accomodate scrapyd validation rule on 'postgres'
# conda env config vars list
# conda env config vars set POSTGRES_HOST="localhost"
# conda env config vars set LENOVO_GREY_HOST="localhost" # or ip address of cloud hosted server
# conda env config vars set LENOVO_CHARCOAL_HOST="localhost" # or ip address of cloud hosted server
# conda env config vars set VAIO_HOST="localhost" # or ip address of cloud hosted server

# https://docs.scrapy.org/en/latest/topics/logging.html
# logging.CRITICAL - for critical errors (highest severity)
# logging.ERROR - for regular errors
# logging.WARNING - for warning messages
# logging.INFO - for informational messages
# logging.DEBUG - for debugging messages (lowest severity)
LOG_LEVEL = "INFO"

FEED_EXPORT_ENCODING = "utf-8"
BOT_NAME = 'scrapy_erc'
SPIDER_MODULES = ['scrapy_erc.spiders']
NEWSPIDER_MODULE = 'scrapy_erc.spiders'

# from shutil import which
# SELENIUM_DRIVER_NAME = 'firefox'
# SELENIUM_DRIVER_EXECUTABLE_PATH = which('geckodriver')
# SELENIUM_DRIVER_ARGUMENTS=['-headless']  # '--headless' if using chrome instead of firefox

# Settings for ScrapySplash:
# SPLASH_URL = "http://localhost:8050"
# HTTPCACHE_STORAGE = 'scrapy_splash.SplashAwareFSCacheStorage'
# SPLASH_COOKIES_DEBUG = True

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
    # 'scrapy_erc.middlewares.CaptchaMiddleware': 400,
    # 'scrapy_erc.middlewares.Connectivity': 200,
    'scrapy_erc.middlewares.ScrapyErcDownloaderMiddleware': 543,
    # 'scrapy_selenium.SeleniumMiddleware': 800
    # 'scrapy_splash.SplashCookiesMiddleware': 723,
    # 'scrapy_splash.SplashMiddleware': 725,
    # 'scrapy.downloadermiddlewares.httpcompression.HttpCompressionMiddleware': 810,
}

SPIDER_MIDDLEWARES = {
    # 'scrapy_splash.SplashDeduplicateArgsMiddleware': 100,
    'scrapy.spidermiddlewares.httperror.HttpErrorMiddleware': 200,
    # 'scrapy_erc.middlewares.ScrapyErcSpiderMiddleware': 543,
}

# Retry Middleware - https://www.programmersought.com/article/9263941817/
# RETRY_HTTP_CODES = [500, 502, 503, 504, 522, 524, 408]

# DUPEFILTER_CLASS = 'scrapy_splash.SplashAwareDupeFilter'
# DUPEFILTER_CLASS = 'scrapy.dupefilters.BaseDupeFilter'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'scrapy_dbd (+http://www.yourdomain.com)'
USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36'

# https://deviceatlas.com/blog/list-of-user-agent-strings#desktop
# user-agents=['Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246',
#             'Mozilla/5.0 (X11; CrOS x86_64 8172.45.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.64 Safari/537.36',
#             'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/601.3.9 (KHTML, like Gecko) Version/9.0.2 Safari/601.3.9',
#             'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.111 Safari/537.36',
#             'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:15.0) Gecko/20100101 Firefox/15.0.1',
#             ]
# USER_AGENT=random.choice(user_agents)

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
#CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# See https://docs.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
#DOWNLOAD_DELAY = 3
# The download delay setting will honor only one of:
#CONCURRENT_REQUESTS_PER_DOMAIN = 16
#CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
#COOKIES_ENABLED = False
COOKIES_ENABLED = True
COOKIES_DEBUG = False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# https://github.com/scrapy-plugins/scrapy-splash/issues/67
# Override the default request headers:
DEFAULT_REQUEST_HEADERS = {
  'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
  'Accept-Language': 'th',
  'Referer': 'http://app04.erc.or.th/ELicense/Licenser/05_Reporting/504_ListLicensing_Columns_New.aspx?',
  'Origin': 'http://www.erc.or.th/ERCWeb2/EN/Default.aspx'
}

# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
#}

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
    'scrapy_erc.pipelines.ScrapyErcPipeline': 300,
}

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
#AUTOTHROTTLE_ENABLED = True
# The initial download delay
#AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
#AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED = True
#HTTPCACHE_EXPIRATION_SECS = 0
#HTTPCACHE_DIR = 'httpcache'
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'
