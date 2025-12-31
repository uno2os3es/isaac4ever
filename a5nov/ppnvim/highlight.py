# Author : isaac
# Email  : mkalafsaz@gmail.com
# Time   : Wed 26 Nov 2025 | 23:32:09

import pynvim

# Attach to the running Neovim instance
nvim = pynvim.attach(
    'socket', path='/tmp/nvim.sock'
)  # Adjust the socket path if needed


# Create a command `:HighlightWord` that highlights all occurrences of a word in the buffer
@nvim.command('HighlightWord', sync=True)
def highlight_word(args):
    # Ensure there's an argument (a word to search)
    if len(args) < 1:
        nvim.command('echo "Please provide a word to highlight."')
        return

    word = args[0]

    # Get the current buffer
    buffer = nvim.api.get_current_buf()

    # Search for the word and highlight it
    nvim.command(f'let @/ = "{word}"')  # Set the search register to the word
    nvim.command('normal! n')  # Start searching for the word

    # Highlight all instances of the word in the buffer
    nvim.command('match Search /\%V' + word + '/')

    # Inform the user
    nvim.command(f'echo "Highlighted all occurrences of: {word}"')
