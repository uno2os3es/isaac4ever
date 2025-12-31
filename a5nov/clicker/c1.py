# Author : isaac
# Email  : mkalafsaz@gmail.com
# Time   : Wed 26 Nov 2025 | 23:32:09

import click


# Define a command with arguments
@click.command()
@click.argument('name')  # Argument for the name
@click.option('--greeting', default='Hello', help='Custom greeting message')
def greet(name, greeting):
    """Simple greeting command."""
    click.echo(f'{greeting}, {name}!')


if __name__ == '__main__':
    greet()
