from flask import render_template, jsonify, make_response, request

from app import app, auth
from app.controller.errors import unauthorized, server_error, not_found, bad_request
import app.model.services as service


@auth.verify_password
def verify_password(login, password):
    user = service.check_login(login)
    if user:
        if user.check_password(password):
            return True
        else:
            unauthorized('wrong password')
    unauthorized('unauthorized access')


# Route block

# Web-инструкция к API List of Tasks
@app.route('/')
def index():
    return render_template("index.html")


# Получить список всех задач
@app.route('/tasks', methods=['GET'])
@auth.login_required
def get_tasks():
    user = service.check_login(auth.username())  # Если существует возвращает объект User
    if user is None:
        return server_error('user`s none')
    tasks = service.get_tasks(user)
    return make_response(jsonify({'tasks': [task.to_dict() for task in tasks]}), 200)


# Получить задачу по id
@app.route('/tasks/<int:task_id>', methods=['GET'])
@auth.login_required
def get_task(task_id: int):
    user = service.check_login(auth.username())  # Если существует возвращает объект User
    if user is None:
        return server_error('user`s none')
    task = service.get_task(user, task_id)
    if task is None:
        return not_found(f'task {task_id} was not found')
    return make_response(jsonify(task.to_dict()), 200)


# Отметить задачу как выполненную
@app.route('/done/<int:task_id>', methods=['PUT'])
@auth.login_required
def done_task(task_id: int) -> object:
    user = service.check_login(auth.username())  # Если существует возвращает объект User
    task = service.done_task(user, task_id)
    if task[0] == 1:
        return not_found(task[1])
    elif task[0] == 2:
        return server_error(task[1])
    response = {'status': 200, 'message': task[1], 'task': task[2].to_dict()}
    return make_response(jsonify(response), 200)


# Создать задачу
@app.route('/create_task', methods=['POST'])
@auth.login_required
def create_task() -> object:
    user = service.check_login(auth.username())  # Если существует возвращает объект User
    data = request.get_json() or {}
    if not data:
        return bad_request('missing json request')
    elif 'title' not in data:
        return bad_request('the title field is missing')
    elif 'description' not in data:
        return bad_request('the description field is missing')
    elif 'deadline' not in data:
        return bad_request('the deadline field is missing')
    task = service.create_task(data, user)
    if task[0] == 1:
        return bad_request(task[1])
    elif task[0] == 2:
        return server_error(task[1])
    response = {'status': 201, 'task': task[2].to_dict()}
    return make_response(jsonify(response), 201)


# Создать пользователя
@app.route('/create_user', methods=['POST'])
def create_user() -> object:
    data = request.get_json() or {}
    if not data:
        return bad_request('missing json request')
    elif 'login' not in data:
        return bad_request('the login field is missing')
    elif 'password' not in data:
        return bad_request('the password field is missing')
    user = service.create_user(data['login'], data['password'])
    if user[0] == 1:
        return bad_request(user[1])
    elif user[0] == 2:
        return server_error(user[1])
    response = {'status': 201, 'message': user[1]}
    return make_response(jsonify(response), 201)


# Удалить задачу
@app.route('/delete_task/<int:task_id>', methods=['DELETE'])
@auth.login_required
def delete_task(task_id: int) -> object:
    task = service.delete_task(task_id)
    if task[0] == 1:
        return not_found(task[1])
    elif task[0] == 2:
        return server_error(task[1])
    response = {'status': 200, 'message': task[1]}
    return make_response(jsonify(response))


# Удалить пользователя
@app.route('/delete_user', methods=['DELETE'])
@auth.login_required
def delete_user() -> object:
    result = service.delete_user(auth.username())
    if result[0] == 1:
        return not_found(result[1])
    elif result[0] == 2:
        return server_error(result[1])
    response = {'status': 200, 'message': result[1]}
    return make_response(jsonify(response))
