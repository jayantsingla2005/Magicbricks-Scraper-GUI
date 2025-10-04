from scraper.individual_property_scraper import IndividualPropertyScraper

class Dummy:
    def __getattr__(self, name):
        return lambda *a, **k: None

def test_segment_key_extraction():
    s = IndividualPropertyScraper(driver=Dummy(), property_extractor=Dummy(), bot_handler=Dummy())
    url = "https://www.magicbricks.com/kamala-natraj-santacruz-east-mumbai-pdpid-4d42"
    seg = s._segment_key_from_url(url)
    assert 'santacruz' in seg


def test_record_segment_failure_sets_cooldown():
    s = IndividualPropertyScraper(driver=Dummy(), property_extractor=Dummy(), bot_handler=Dummy())
    url = "https://www.magicbricks.com/aspen-park-goregaon-east-mumbai-pdpid-4d42"
    s._record_segment_failure(url)
    seg = s._segment_key_from_url(url)
    assert seg in s.segment_cooldowns and s.segment_cooldowns[seg] > 0

