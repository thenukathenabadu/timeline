from scraper.rss import RSSScraper


class GuardianScraper(RSSScraper):
    source_id = "guardian"
    display_name = "The Guardian"
    home_url = "https://www.theguardian.com"
    feed_urls = [
        "https://www.theguardian.com/world/rss",
        "https://www.theguardian.com/international/rss",
    ]
