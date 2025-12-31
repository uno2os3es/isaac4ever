# Author : isaac
# Email  : mkalafsaz@gmail.com
# Time   : Wed 26 Nov 2025 | 23:32:09

from pypdf import PdfReader, PdfWriter

reader = PdfReader('py.pdf', strict=False)
writer = PdfWriter()

for page in reader.pages:
    writer.add_page(page)

with open('fixed.pdf', 'wb') as f:
    writer.write(f)
