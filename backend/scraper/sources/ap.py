from scraper.rss import RSSScraper


class APScraper(RSSScraper):
    source_id = "ap"
    display_name = "AP News"
    home_url = "https://apnews.com"
    feed_urls = [
        "https://rsshub.app/apnews/topics/apf-topnews",
    ]
