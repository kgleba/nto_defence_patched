#!/usr/bin/env python3
from flask import Flask, make_response, request, redirect, jsonify, session, render_template
from flask_session import Session
from flask_http_middleware import MiddlewareManager
from middlewares import AccessMiddleware, Access
from db import DB
from connector import Connector, BadConnection
from access import Permissions, User, UserDoesntExist, WrongPassword
import os

app = Flask(__name__, static_url_path='/static', static_folder='static', template_folder='templates')

CONTROL_PORT = int(os.getenv('CONTROL_PORT', 8080))
DB_USER = os.getenv('DB_USER', 'user')
DB_PASS = os.getenv('DB_PASS', '3rJLGeVZoGtB4b1H')

PROVIDER_HOST = os.getenv('PROVIDER_HOST', 'control')
PROVIDER_PORT = int(os.getenv('PROVIDER_PORT', 8888))

# DO NOT CHANGE IT! Or the checker will not be able to check your functionality
INIT_ADMIN_USERNAME = os.getenv('INIT_ADMIN_USERNAME', 'admin')
INIT_ADMIN_PASSWORD = os.getenv('INIT_ADMIN_PASSWORD', 'TwfPsNu8BFhElIztxBio')

database = DB(f'mongodb://{DB_USER}:{DB_PASS}@mongo:27017/?authMechanism=DEFAULT')
connector = Connector(PROVIDER_HOST, PROVIDER_PORT, database, '/abi.json')
access = Access(connector)
admin_user = User(connector, username=INIT_ADMIN_USERNAME, password=INIT_ADMIN_PASSWORD, email='admin@mail.com', admin=True)
admin_user.save_to_db(rewrite_access=True)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

app.wsgi_app = MiddlewareManager(app)
app.wsgi_app.add_middleware(AccessMiddleware, db=connector.db)


@app.route('/', methods=['GET'])
@app.route('/home', methods=['GET'])
def home():
    return render_template("home.html")


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template("register.html")
    email = request.json.get('email')
    username = request.json.get('username')
    password = request.json.get('password1')
    password_ = request.json.get('password2')
    if password != password_:
        return make_response({"error": "Passwords do not match"}, 400)
    if not password or not password_:
        return make_response({"error": "Empty password is not allowed"}, 403)
    user = User(connector, email=email, username=username, password=password)
    if user.save_to_db():
        return make_response({"status": "ok"}, 200)
    else:
        return make_response({"error": "User exists!"}, 403)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template("login.html")
    username = request.json.get('username')
    password = request.json.get('password')
    if not password:
        return make_response({"error": "Empty password is not allowed"}, 403)
    try:
        user = User(connector)
        user.import_from_db(username=username, password=password)
        session["user"] = username
        return make_response({"status": "ok", "user_id": user.id}, 200)
    except (UserDoesntExist, WrongPassword):
        return make_response({"error": "Invalid username or password"}, 403)


@app.route('/get_users', methods=['GET'])
@access.is_admin
def get_users():
    users = connector.db.get_users()
    return make_response({"users": users}, 200)


@app.route('/get_my_permissions', methods=['GET'])
def get_my_permissions():
    user = User(connector)
    user.import_from_db(session['user'])
    permissions = connector.db.get_permissions_by_uid(user.id)
    return make_response({'permissions': permissions}, 200)


@app.route('/admin/home', methods=['GET'])
@access.is_admin
def admin_home():
    return render_template('admin_home.html')


@app.route('/admin', methods=['GET'])
@app.route('/admin/', methods=['GET'])
@app.route('/admin/users', methods=['GET'])
@access.is_admin
def admin_users():
    return render_template('admin_users.html')


@app.route('/admin/user/<user_id>', methods=['GET'])
@access.is_admin
def admin_user(user_id):
    user = connector.db.get_user_by_uid(user_id)
    return render_template('admin_user.html')


@app.route('/get_permissions', methods=['GET'])
@access.is_admin
def get_permissions():
    user_id = request.args.get('user_id')
    permissions = connector.db.get_permissions_by_uid(user_id)
    return make_response({"permissions": permissions}, 200)


@app.route('/set_permissions', methods=['POST'])
@access.is_admin
def set_permissions():
    user_id = request.json['user_id']
    permissions = request.json['permissions']
    user = User(connector)
    user.import_from_db(user_id=user_id)
    user.import_({"permissions": permissions})
    user.save_to_db(rewrite_access=True)
    return make_response({"status": "ok"}, 200)


@app.route('/change_password', methods=['POST', 'GET'])
def change_password():
    user = connector.db.get_user(session["user"])
    if int(user["uid"]) != int(request.form.get('user_id')) and not user["admin"]:
        return make_response({"error": "Access denied"}, 403)
    user_id = request.form.get('user_id')
    password = request.form.get('password')
    if connector.db.change_password(user_id, password):
        return make_response({"status": "ok"}, 200)
    else:
        return make_response({"error": "Same password"}, 400)


@app.route('/get_user_info', methods=['GET'])
def get_user_info():
    user = connector.db.get_user(session["user"])
    email = user.get('email')
    username = user.get('username')
    return make_response({'email': email, 'username': username}, 200)


@app.route('/get_user', methods=['GET'])
@access.is_admin
def get_user():
    user_id = request.args.get('user_id')
    user = connector.db.get_user_by_uid(user_id)
    return make_response({'user': user}, 200)


@app.route('/get_state', methods=['GET'])
@access.is_admin
def get_state():
    return make_response({"init_state": connector.get_state()}, 200)


@app.route('/reset_state', methods=['POST'])
@access.is_admin
def reset_state():
    try:
        connector.reset_state()
        return make_response({'status': 'ok'}, 200)
    except BadConnection:
        return make_response({'error': 'Something went wrong'}, 500)


@app.route('/elements', methods=['GET'])
def elements():
    return make_response(connector.get_methods(), 200)


@app.route('/elements/<element_path>', methods=['GET', 'POST'])
def element(element_path):
    if request.method == 'GET':
        element_methods = connector.get_element_methods(element_path)
        return make_response(element_methods, 200)
    method = request.json.get('method')
    args = request.json.get('args')
    user = User(connector)
    user.import_from_db(session['user'])
    if not user.check_permissions(element_path, method):
        return make_response({'error': 'Access denied'}, 403)
    try:
        result = connector.execute(element_path, method, args)
    except BadConnection:
        return make_response({'error': 'Something went wrong'}, 500)
    return make_response({'status': 'ok', 'result': result}, 200)


# anyone should be able to put backups here
@app.route('/put_backup_here', methods=['POST'])
def new_backup():
    backup = request.get_json()
    bid = connector.db.create_backup(backup)
    return make_response({"status": "ok", "backup_id": bid}, 200)


@app.route('/get_backup', methods=['GET'])
@access.is_admin
def get_backup():
    bid = request.json['backup_id']
    backup = connector.db.get_backup(bid)
    return make_response({"backup": backup}, 200)


@app.route('/ping', methods=['GET'])
def ping():
    return 'pong'


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=CONTROL_PORT)
