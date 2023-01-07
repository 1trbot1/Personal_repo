#!/usr/bin/python3
from os import get_terminal_size
from progress_bar import progressbar
from localdb import localdb
class cli:
    def __init__(self):
        self.columns = get_terminal_size()[0]
    
    def main(self,db_name='localdb.json',init_data=None):
        db = localdb.init(db_name=db_name,init_data=init_data)
        print('#'*self.columns)
        for item in db.all():
            print(f"\nName: {item['name']}\nAge: {item['age']}\nType: {item['type']}\n")
        print('#'*self.columns)
        db.truncate() # Clean DB
        print(db.all())