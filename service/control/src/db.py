import pymongo
import bcrypt
import time
import json
import base64
import os


class DB:
    def __init__(self, connection_string):
        self.c_string = connection_string
        self.__connect()
        self.salt = b'$2b$12$THzbTRP4fVwlM1SitlNKSu'
        if self.users.count_documents({}) != self.permissions.count_documents({}):
            self.client.drop_database('xss')
            self.__connect()

    def __connect(self):
        self.client = pymongo.MongoClient(self.c_string)
        self.db = self.client['xss']
        self.users = self.db['users']
        self.permissions = self.db['permissions']
        self.backups = self.db['backups']

    def __check_connection(self):
        try:
            self.users.find({})
        except Exception:
            self.__connect()

    def new_user(self, username, email, password, is_admin):
        self.__check_connection()
        hashed = self.hash_password(password)
        try:
            next_uid = self.users.find_one(sort=[('uid', pymongo.DESCENDING)])['uid'] + 1
        except Exception as e:
            next_uid = 1
        self.users.insert_one({"username": username, "email": email, "password": hashed, "admin": is_admin, "uid": next_uid})
        return True

    def set_admin(self, username, is_admin):
        self.__check_connection()
        r = self.users.update_one({"username": username}, {"$set": {"admin": is_admin}})
        if r.modified_count == 0:
            return False
        return True

    def hash_password(self, password):
        return bcrypt.hashpw(password.encode(), self.salt).decode()

    def check_user(self, username, password):
        self.__check_connection()
        hashed = self.hash_password(password)
        try:
            u = self.users.find({"username": username, "password": hashed})[0]
            return u['uid']
        except IndexError:
            return False

    def change_password(self, uid: int, password: str):
        self.__check_connection()
        hashed = self.hash_password(password)
        r = self.users.update_one({"$where": f"this.uid == '{uid}'"}, {"$set": {"password": hashed}})
        if r.modified_count == 0:
            return False
        return True

    def get_user_id(self, username):
        self.__check_connection()
        try:
            u = self.users.find({"username": username})[0]
            return u['uid']
        except IndexError:
            return False

    def get_user_by_uid(self, uid: int):
        self.__check_connection()
        try:
            u = self.users.find({"$where": f"this.uid == '{uid}'"}, {"_id": 0})[0]
            return u
        except IndexError:
            return False

    def get_user(self, username: str):
        self.__check_connection()
        try:
            u = self.users.find({"username": username})[0]
            return u
        except IndexError:
            return False

    def get_users(self):
        self.__check_connection()
        users = self.users.find({}, {"_id": 0})
        return list(users)

    def set_permissions(self, username, permissions):
        self.__check_connection()
        user = self.get_user(username)
        self.permissions.insert_one({"username": username, "permissions": permissions, "uid": user["uid"]})
        return user['uid']

    def get_permissions(self, username: str):
        self.__check_connection()
        try:
            p = self.permissions.find({"username": username})[0]['permissions']
            return p
        except IndexError:
            return False

    def get_permissions_by_uid(self, uid: int):
        self.__check_connection()
        user = self.get_user_by_uid(uid)
        try:
            p = self.permissions.find({"uid": user['uid']})[0]['permissions']
            return p
        except IndexError:
            return False

    def delete_user(self, username):
        self.__check_connection()
        self.users.delete_one({"username": username})

    def delete_permissions(self, username):
        self.__check_connection()
        self.permissions.delete_one({"username": username})

    def create_backup(self, backup):
        self.__check_connection()
        backup = base64.b64encode(json.dumps(backup).encode()).decode()
        try:
            next_bid = self.backups.find_one(sort=[('bid', pymongo.DESCENDING)])['bid'] + 1
        except:
            next_bid = 1
        self.backups.insert_one({'backup': backup, 'timestamp': int(time.time()), 'bid': next_bid})
        return next_bid

    def get_backup(self, bid):
        self.__check_connection()
        backup = self.backups.find({"bid": bid}, {'bid': 0, '_id': 0})
        return backup[0]
