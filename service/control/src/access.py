from enum import Flag, auto
from hashlib import md5
import json


class Permissions(Flag):
    NONE = auto()
    READ = auto()
    WRITE = auto()


class UserDoesntExist(Exception):
    pass


class WrongPassword(Exception):
    pass


class User:
    def __init__(self, connector, email='', username='', password='', admin=False):
        self._connector = connector
        self.email = email
        self.username = username
        self.password = password
        self._hashed = ''
        self.admin = admin
        self.permissions = connector.get_permissions_template()

    def import_from_db(self, username='', password='', user_id=None):
        if user_id != None:
            user_id = int(user_id)
            user = self._connector.db.get_user_by_uid(user_id)
        else:
            user = self._connector.db.get_user(username)
        if user == False:
            raise UserDoesntExist
        self.email = user['email']
        self.username = user['username']
        self._hashed = user['password']
        self.password = ''
        self.admin = user['admin']
        self.id = user['uid']
        if password:
            password = self._connector.db.hash_password(password)
            if password != self._hashed:
                raise WrongPassword
        permissions = self._connector.db.get_permissions(self.username)
        if permissions:
            self.permissions = self.__import_permissions(permissions)

    def save_to_db(self, rewrite_access=False):
        user = self._connector.db.get_user(self.username)
        permissions = self._connector.db.get_permissions(self.username)
        if not permissions:
            permissions = self.__export_permissions(self._connector.get_permissions_template())
        if user != False:
            if not rewrite_access:
                return False
            if self.password == '' or self._hashed == '':
                self._hashed = self._connector.db.hash_password(self.password)
            data1 = ':'.join([self.email, self.username, self._hashed, json.dumps(self.__export_permissions(self.permissions))])
            data2 = ':'.join([user['email'], user['username'], user['password'], json.dumps(permissions)])
            hash1 = md5()
            hash1.update(data1.encode())
            h1 = hash1.hexdigest()
            hash2 = md5()
            hash2.update(data2.encode())
            h2 = hash2.hexdigest()
            if h1 == h2:
                return False
            self._connector.db.delete_user(self.username)
            self._connector.db.delete_permissions(self.username)
        id_ = self._connector.db.new_user(self.username, self.email, self.password, self.admin)
        id_ = self._connector.db.set_permissions(self.username, self.__export_permissions(self.permissions))
        return True

    def is_admin(self):
        return self.admin

    def check_permissions(self, element_path, method):
        if self.admin:
            return True
        el = self.get_permission(element_path)
        element_path = element_path.split('.')
        item_permissions = self._connector.get_abi()[self._connector.get_abi_element_original_name(element_path[-1])][method]
        if type(el) == Permissions and el != Permissions.NONE and (el & item_permissions) == item_permissions:
            return True
        return False

    def _public_attrs(self):
        return [attr for attr in self.__dict__ if not attr.startswith('_')]

    def get_permission(self, element_path):
        element_path = element_path.split('.')
        el = self.permissions
        for p in element_path:
            el = el[p]
        if type(el) == dict:
            return el['self']
        return el

    def __nested_set(self, dic, keys, value):
        for key in keys[:-1]:
            dic = dic.setdefault(key, {})
        dic[keys[-1]] = value

    def set_permission(self, element_path, permission):
        element_path = element_path.split('.')
        self.__nested_set(self.permissions, element_path, permission)

    def __export_permissions(self, permissions):
        if type(permissions) == Permissions:
            return permissions.value
        tmp = {}
        for p in permissions:
            tmp[p] = self.__export_permissions(permissions[p])
        return tmp

    def __import_permissions(self, permissions):
        if type(permissions) == int:
            return Permissions(permissions)
        tmp = {}
        for p in permissions:
            tmp[p] = self.__import_permissions(permissions[p])
        return tmp

    def __iter__(self):
        for attr in self._public_attrs():
            if attr == 'permissions':
                attribute = self.__getattribute__(attr)
                d = self.__export_permissions(attribute)
                yield attr, d
                continue
            yield attr, self.__getattribute__(attr)
        return
        yield

    def import_(self, data):
        for attr, value in data.items():
            if attr == 'permissions':
                permissions = self.__import_permissions(value)
                self.permissions |= permissions
                continue
            self.__setattr__(attr, value)

    def export_(self):
        return dict(self)
