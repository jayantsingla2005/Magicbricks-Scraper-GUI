from scraper.individual_property_scraper import IndividualPropertyScraper

class Dummy:
    pass

def test_restart_driver_calls_callback(monkeypatch):
    called = {'val': False}
    def cb():
        called['val'] = True
    # Construct with minimal deps
    scraper = IndividualPropertyScraper(
        driver=Dummy(),
        property_extractor=Dummy(),
        bot_handler=Dummy(),
        individual_tracker=None,
        logger=None,
        restart_callback=cb
    )
    scraper._restart_driver()
    assert called['val'] is True

