from scraper.rss import RSSScraper


class ReutersScraper(RSSScraper):
    source_id = "reuters"
    display_name = "Reuters"
    home_url = "https://www.reuters.com"
    feed_urls = [
        "https://feeds.reuters.com/reuters/topNews",
        "https://feeds.reuters.com/Reuters/worldNews",
    ]
