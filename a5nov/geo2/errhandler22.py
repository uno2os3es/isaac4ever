# Author : isaac
# Email  : mkalafsaz@gmail.com
# Time   : Wed 26 Nov 2025 | 23:32:09

import geoip2.database
import geoip2.errors
from ipaddress import ip_address, IPv4Address, IPv6Address


def read_geoip_database(file_path, ip_to_lookup):
    try:
        with geoip2.database.Reader(file_path) as reader:
            try:
                # Validate IP address
                ip_addr = ip_address(ip_to_lookup)

                if isinstance(ip_addr, IPv4Address):
                    response = reader.city(ip_to_lookup)
                elif isinstance(ip_addr, IPv6Address):
                    response = reader.city(ip_to_lookup)

                # Return structured data
                geo_data = {
                    'ip': ip_to_lookup,
                    'country': {
                        'name': response.country.name,
                        'code': response.country.iso_code,
                    },
                    'city': response.city.name,
                    'location': {
                        'latitude': response.location.latitude,
                        'longitude': response.location.longitude,
                        'time_zone': response.location.time_zone,
                    },
                    'postal_code': response.postal.code,
                    'subdivision': (
                        response.subdivisions.most_specific.name
                        if response.subdivisions
                        else None
                    ),
                }

                return geo_data

            except ValueError:
                print(f'Invalid IP address: {ip_to_lookup}')
                return None
            except geoip2.errors.AddressNotFoundError:
                print(f'IP address not found in database: {ip_to_lookup}')
                return None

    except FileNotFoundError:
        print(f'GeoIP database file not found: {file_path}')
        return None
    except Exception as e:
        print(f'Error reading database: {e}')
        return None


# Usage
result = read_geoip_database('geoip.dat', '8.8.8.8')
if result:
    print(result)
