from flask_login import UserMixin
from app import firebase

class User(UserMixin):
    def __init__(self, path):
        data = firebase.get(path, None)
        if data:
            self.id = data['username']
            self.username = data['username']
            self.first_name = data['first_name']
            self.last_name = data['last_name']
            self.cellular = data['cellular']
            self.link = data['link']
            self.password = data['password']
        else:
            self.password = "$2b$12$Z/rUoVk5Ge5AlMTxztxxpeN0ITgcHwCgAjnGG1YjVtR2."

    def __repr__(self):
        print(self.username, self.cellular, self.link)
        return f"User('{self.username}', '{self.cellular}', '{self.link}')"