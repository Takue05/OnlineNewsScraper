BOT_NAME = 'news_scraper'

SPIDER_MODULES = ['news_scraper.spiders']
NEWSPIDER_MODULE = 'news_scraper.spiders'

# Obey robots.txt rules (be ethical)
ROBOTSTXT_OBEY = True

# Configure item pipelines
ITEM_PIPELINES = {
    'news_scraper.pipelines.DailyCSVPipeline': 300,
}

# Configure maximum concurrent requests
CONCURRENT_REQUESTS = 16

# Add a delay to be respectful
DOWNLOAD_DELAY = 1.5

# Use a reasonable user agent
USER_AGENT = 'NewsResearchProject (+http://takudzwa.nhema@students.uz.ac.zw)'