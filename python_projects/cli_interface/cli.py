#!/usr/bin/python3
from os import path , get_terminal_size
from tinydb import TinyDB , where
from flask import Flask


app = Flask('cli')
@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

class cli:
    def __init__(self):
        db_name = "api_db.json"
        db_path = f"{path.dirname(path.abspath(__file__))}/{db_name}"
        self.db = TinyDB(db_path)
        self.columns = get_terminal_size()[0]
    

    def main(self,data):
        for item in data:
            if not self.db.search(where('name') == item['name']):
                self.db.insert(item)
        print('#'*self.columns)
        # for item in self.db.all():
            # print(f"\nName: {item['name']}\nAge: {item['age']}\nType: {item['type']}\n")
        print('#'*self.columns)
        # self.db.truncate() # Clean DB