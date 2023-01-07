#!/usr/bin/python3 
from cli import cli

db_name = "localdb2.json"
people = [
    {'name': 'Dakotik','age': 18, 'type': 'Sexy'},
    {'name': 'Masya','age': 3, 'type': 'Cat'},
    {'name': 'Kashak','age': 999, 'type': 'Old Cat'}
]

if __name__ == "__main__":
    cli = cli()
    cli.main(db_name=db_name,init_data=people)