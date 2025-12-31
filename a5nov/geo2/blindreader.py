# Author : isaac
# Email  : mkalafsaz@gmail.com
# Time   : Wed 26 Nov 2025 | 23:32:09

import os
from unidecode import unidecode

with open('geoip.dat', 'rb') as f:
    data = f.read()
    asdata = unidecode(data).to_ascii()
    print(asdata)
