import os
from lib.utils import permissions_template


def type_permissions(permissions):
    if type(permissions) == int:
        return int
    tmp = {}
    for p in permissions:
        tmp[p] = type_permissions(permissions[p])
    return tmp


Permissions = type_permissions(permissions_template)

endpoints = {}
endpoints['/'] = {'methods': {'GET': {}}}
endpoints['/register'] = {'methods': {'GET': {}, 'POST': {'email': str, 'username': str, 'password1': str, 'password2': str}}}
endpoints['/login'] = {'methods': {'GET': {}, 'POST': {'username': str, 'password': str}}}
endpoints['/get_users'] = {'methods': {'GET': {}}}
endpoints['/get_permissions'] = {'methods': {'GET': {'user_id': int}}}
endpoints['/set_permissions'] = {'methods': {'GET': {}, 'POST': {'user_id': int, 'permissions': type_permissions}}}
endpoints['/change_password'] = {'methods': {'GET': {}, 'POST': {'user_id': int, 'password': str}}, 'form': True}
endpoints['/get_state'] = {'methods': {'GET': {}}}
endpoints['/elements'] = {'methods': {'GET': {}}}
endpoints['/elements/'] = {'methods': {'GET': {}, 'POST': {'method': str, 'args': [int]}}}
endpoints['/ping'] = {'methods': {'GET': {}}}
endpoints['/home'] = {'methods': {'GET': {}}}
endpoints['/get_my_permissions'] = {'methods': {'GET': {}}}
endpoints['/admin/home'] = {'methods': {'GET': {}}}
endpoints['/admin/users'] = {'methods': {'GET': {}}}
endpoints['/admin/user/'] = {'methods': {'GET': {"user_id": int}}}
endpoints['/get_user_info'] = {'methods': {'GET': {}}}
endpoints['/get_user'] = {'methods': {'GET': {'user_id': int}}}
endpoints['/reset_state'] = {'methods': {'POST': {}}}
endpoints['/get_backup'] = {'methods': {'GET': {'backup_id': int}, 'POST': {'backup_id': int}}}
endpoints['/admin'] = {'methods': {'GET': {}}}
endpoints['/admin/'] = {'methods': {'GET': {}}}
