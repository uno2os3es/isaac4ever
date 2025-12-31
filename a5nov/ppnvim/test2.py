# Author : isaac
# Email  : mkalafsaz@gmail.com
# Time   : Wed 26 Nov 2025 | 23:32:09

import pynvim

# Connect to Neovim
nvim = pynvim.attach('socket', path='/sdcard/tmp/nvim.sock')


# Define a custom command
@nvim.command('SayHello')
def say_hello(args):
    nvim.command('echo "Hello from Python!"')
