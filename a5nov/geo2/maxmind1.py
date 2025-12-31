# Author : isaac
# Email  : mkalafsaz@gmail.com
# Time   : Wed 26 Nov 2025 | 23:32:09

import maxminddb

# Open and read the GeoIP database
with maxminddb.open_database('geosite.dat') as reader:
    # Look up an IP address
    response = reader.get('8.8.8.8')
    print(response)

    # Example output structure:
    # {
    #     'city': {'names': {'en': 'Mountain View'}},
    #     'continent': {'code': 'NA', 'names': {'en': 'North America'}},
    #     'country': {'iso_code': 'US', 'names': {'en': 'United States'}},
    #     'location': {'latitude': 37.386, 'longitude': -122.0838},
    #     'postal': {'code': '94035'},
    #     'registered_country': {'iso_code': 'US', 'names': {'en': 'United States'}},
    #     'subdivisions': [{'iso_code': 'CA', 'names': {'en': 'California'}}]
    # }
