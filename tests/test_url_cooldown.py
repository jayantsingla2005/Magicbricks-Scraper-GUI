import time
from scraper.individual_property_scraper import IndividualPropertyScraper

class Dummy:
    def __init__(self):
        self.called=False
    def __getattr__(self, name):
        # allow any attribute access for simplicity
        return lambda *a, **k: None

def test_url_cooldown_and_skip(monkeypatch):
    s = IndividualPropertyScraper(driver=Dummy(), property_extractor=Dummy(), bot_handler=Dummy(), logger=None)
    url = "https://www.magicbricks.com/x"
    # record failures to trigger cooldown
    s._record_url_failure(url)
    assert url in s.url_cooldowns
    # simulate sequential skip path
    now = time.time()
    assert s.url_cooldowns[url] > now
    # sequential method checks cooldown before scraping; emulate quickly
    assert (url in s.url_cooldowns) and (s.url_cooldowns[url] > time.time())

