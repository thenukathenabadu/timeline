from scraper.rss import RSSScraper


class AlJazeeraScraper(RSSScraper):
    source_id = "aljazeera"
    display_name = "Al Jazeera"
    home_url = "https://www.aljazeera.com"
    feed_urls = [
        "https://www.aljazeera.com/xml/rss/all.xml",
    ]
