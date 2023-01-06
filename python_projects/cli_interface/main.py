#!/usr/bin/python3 
from cli import cli

if __name__ == "__main__":
    pople = [
        {'name': 'Dakotik','age': 18, 'type': 'Sexy'},
        {'name': 'Masya','age': 3, 'type': 'Cat'},
        {'name': 'Kashak','age': 999, 'type': 'Old Cat'}
    ]
    cli = cli()
    cli.main(pople)