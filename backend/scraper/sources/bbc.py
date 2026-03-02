from scraper.rss import RSSScraper


class BBCScraper(RSSScraper):
    source_id = "bbc"
    display_name = "BBC News"
    home_url = "https://www.bbc.com/news"
    feed_urls = [
        "https://feeds.bbci.co.uk/news/rss.xml",
        "https://feeds.bbci.co.uk/news/world/rss.xml",
    ]
