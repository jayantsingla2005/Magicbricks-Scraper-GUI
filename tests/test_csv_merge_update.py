import os
import csv
import tempfile
from integrated_magicbricks_scraper import IntegratedMagicBricksScraper  # type: ignore


def create_temp_csv(rows):
    fd, path = tempfile.mkstemp(suffix='.csv')
    os.close(fd)
    with open(path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    return path


def test_update_csv_with_individual_data_tolerant_mapping():
    # Minimal scraper instance
    scraper = IntegratedMagicBricksScraper(headless=True)

    # Prepare CSV with property_url
    rows = [
        {
            'title': 'X', 'price': '1.0 Cr', 'area': '1000 sqft',
            'property_url': 'https://www.magicbricks.com/foo-pdpid-123',
            'amenities': '', 'description': '', 'builder_name': '',
            'location_address': '', 'specifications': ''
        }
    ]
    csv_path = create_temp_csv(rows)

    try:
        # detailed_properties missing 'url' key; has 'property_url' instead
        detailed_properties = [{
            'property_url': 'https://www.magicbricks.com/foo-pdpid-123',
            'amenities': ['Lift', 'Parking'],
            'description': 'Nice flat',
            'builder_info': {'name': 'Acme'},
            'location_details': {'address': 'Sector 1'},
            'specifications': {'facing': 'East'}
        }]

        # Should not raise and should update CSV
        scraper._update_csv_with_individual_data(csv_path, detailed_properties)

        # Verify CSV updated
        import pandas as pd
        df = pd.read_csv(csv_path)
        assert df.loc[0, 'amenities'] == 'Lift, Parking'
        assert df.loc[0, 'description'] == 'Nice flat'
        assert df.loc[0, 'builder_name'] == 'Acme'
        assert df.loc[0, 'location_address'] == 'Sector 1'
        assert 'specifications' in df.columns
    finally:
        os.remove(csv_path)

