# Author : isaac
# Email  : mkalafsaz@gmail.com
# Time   : Wed 26 Nov 2025 | 23:32:09

import pygeoip

# For country-level database
gi = pygeoip.GeoIP('geoip.dat')
country = gi.country_code_by_addr('8.8.8.8')
print(f'Country: {country}')

# For city-level database
gi_city = pygeoip.GeoIP('geoip.dat', pygeoip.MEMORY_CACHE)
record = gi_city.record_by_addr('8.8.8.8')
print(record)
