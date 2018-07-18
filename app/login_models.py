from flask_login import UserMixin
from app import firebase

class User(UserMixin):
    def __init__(self, path):
        data = firebase.get(path, None)
        if data:
            self.id = data['username']
            self.username = data['username']
            self.email = data['email']
            self.link = data['link']
            self.password = data['password']
        else:
            self.password = "$2b$12$Z/rUoVk5Ge5AlMTxztxxpeN0ITgcHwCgAjnGG1YjVtR2."

    def __repr__(self):
        print(self.username, self.email, self.link)
        return f"User('{self.username}', '{self.email}', '{self.link}')"