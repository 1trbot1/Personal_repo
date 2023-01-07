#!/usr/bin/python3 
from os import path
from tinydb import TinyDB , where

class localdb:
    def init(db_name='localdb.json',init_data=None):
        db_path = f"{path.dirname(path.abspath(__file__))}/{db_name}"
        db = TinyDB(db_path)
        for data in init_data:
            if not db.search(where('name') == data['name']):
                db.insert(data)
        return db