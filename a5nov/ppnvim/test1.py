# Author : isaac
# Email  : mkalafsaz@gmail.com
# Time   : Wed 26 Nov 2025 | 23:32:09

import pynvim

# Connect to Neovim (assuming Neovim is running in background)
nvim = pynvim.attach('socket', path='/sdcard/tmp/nvim.sock')

# Execute a command
nvim.command('echo "Hello, Neovim!"')

# Get current buffer
buffer = nvim.buffer

# Print current buffer content
print(buffer[:])
