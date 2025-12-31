# Author : isaac
# Email  : mkalafsaz@gmail.com
# Time   : Wed 26 Nov 2025 | 23:32:09

import geoip2.database

# Read the database
reader = geoip2.database.Reader('geoip.dat')

try:
    # Look up IP address
    response = reader.city('8.8.8.8')

    # Extract specific information
    print(f'Country: {response.country.name}')
    print(f'Country Code: {response.country.iso_code}')
    print(f'City: {response.city.name}')
    print(f'Postal Code: {response.postal.code}')
    print(f'Latitude: {response.location.latitude}')
    print(f'Longitude: {response.location.longitude}')
    print(f'Time Zone: {response.location.time_zone}')

finally:
    reader.close()
