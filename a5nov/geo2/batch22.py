# Author : isaac
# Email  : mkalafsaz@gmail.com
# Time   : Wed 26 Nov 2025 | 23:32:09

import geoip2.database


def batch_lookup_ips(file_path, ip_list):
    results = {}

    with geoip2.database.Reader(file_path) as reader:
        for ip in ip_list:
            try:
                response = reader.city(ip)
                results[ip] = {
                    'country': response.country.iso_code,
                    'city': response.city.name,
                    'latitude': response.location.latitude,
                    'longitude': response.location.longitude,
                }
            except geoip2.errors.AddressNotFoundError:
                results[ip] = {'error': 'IP not found'}
            except Exception as e:
                results[ip] = {'error': str(e)}

    return results


# Example usage
ips = ['8.8.8.8', '1.1.1.1', '208.67.222.222']
results = batch_lookup_ips('geoip.dat', ips)

for ip, data in results.items():
    print(f'{ip}: {data}')
