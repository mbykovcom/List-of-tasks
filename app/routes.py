from app import app, db, auth
from app.models import Task, User
from flask import render_template, jsonify, make_response, request
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError


# The error handling block
@app.errorhandler(400)
def bad_request(error: str = None) -> object:
    response = {'error': 'bad request',
                'message': ''}
    if error is not None:
        response['message'] = f'{error}'
    return make_response(jsonify(response), 400)


@auth.error_handler
def unauthorized(error: str = 'unauthorized access') -> object:
    response = {'error': 'unauthorized',
                'message': ''}
    if error is not None:
        response['message'] = f'{error}'
    return make_response(jsonify(response), 401)


@app.errorhandler(404)
def not_found(error: str = None) -> object:
    response = {'error': 'not found',
                'message': ''}
    if error is not None:
        response['message'] = f'{error}'
    return make_response(jsonify(response), 404)


@app.errorhandler(405)
def method_not_allowed(error: str = None) -> object:
    response = {'error': 'method not allowed',
                'message': ''}
    if error is not None:
        response['message'] = f'{error}'
    return make_response(jsonify(response), 405)


@app.errorhandler(500)
def server_error(error: str = None) -> object:
    response = {'error': 'internal server error',
                'message': ''}
    if error is not None:
        response['message'] = f'{error}'
    return make_response(jsonify(response), 500)


@auth.verify_password
def verify_password(login, password):
    user = User.check_login(login)
    if user:
        if user.check_password(password):
            return True
        else:
            unauthorized('wrong password')
    unauthorized('unauthorized access')


# Route block

# Web-инструкция к API List of Tasks
@app.route('/')
def index() -> object:
    return render_template('index.html')


# Получить список всех задач
@app.route('/tasks', methods=['GET'])
@auth.login_required
def get_tasks() -> object:
    user = User.check_login(auth.username())    # Если существует возвращает объект User
    tasks = user.tasks.all()
    return make_response(jsonify({'tasks': [task.to_dict() for task in tasks]}), 200)


# Получить задачу по id
@app.route('/tasks/<int:task_id>', methods=['GET'])
@auth.login_required
def get_task(task_id: int) -> object:
    user = User.check_login(auth.username())    # Если существует возвращает объект User
    task = user.tasks.filter_by(id=task_id).first()
    if task is None:
        return not_found(f'task {task_id} was not found')
    return make_response(jsonify(task.to_dict()), 200)


# Отметить задачу как выполненную
@app.route('/done/<int:task_id>', methods=['PUT'])
@auth.login_required
def done_task(task_id: int) -> object:
    user = User.check_login(auth.username())    # Если существует возвращает объект User
    task = user.tasks.filter_by(id=task_id).first()
    if task is None:
        return not_found(f'task {task_id} was not found')
    task.done = True
    try:
        db.session.commit()
    except SQLAlchemyError as error:
        db.session.rollback()
        return server_error('failed to mark the task as completed!')
    response = {'status': 200, 'message': f'task {task_id} was completed', 'task': task.to_dict()}
    return make_response(jsonify(response), 200)


# Создать задачу
@app.route('/create_task', methods=['POST'])
@auth.login_required
def create_task() -> object:
    user = User.check_login(auth.username())    # Если существует возвращает объект User
    data = request.get_json() or {}
    if not data:
        return bad_request('missing json request')
    elif 'title' not in data:
        return bad_request('the title field is missing')
    elif 'description' not in data:
        return bad_request('the description field is missing')
    elif 'deadline' not in data:
        return bad_request('the deadline field is missing')
    task = Task()
    task.user_id = user.id
    try:
        data['deadline'] = datetime.strptime(data['deadline'], "%Y-%m-%d %H:%M")    # Из str в форматированный DateTime
    except ValueError:
        return bad_request('wrong format deadline (yyyy-mm-dd hh:mm)')
    task.from_dict(data)
    task.done = False
    try:
        db.session.add(task)
        db.session.commit()
    except SQLAlchemyError as error:
        db.session.rollback()
        return server_error('failed to create an task!')
    response = {'status': 201, 'task': task.to_dict()}
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

    users = User.query.all()
    list_login = [user.login for user in users]
    if data['login'] in list_login:
        return bad_request('this login is busy')
    user = User()
    user.login = data['login']
    user.set_password(data['password'])
    try:
        db.session.add(user)
        db.session.commit()
    except SQLAlchemyError as error:
        db.session.rollback()
        return server_error('failed to add a user!')
    response = {'status': 201, 'message': f'user {user.login} created'}
    return make_response(jsonify(response), 201)


# Удалить задачу
@app.route('/delete_task/<int:task_id>', methods=['DELETE'])
@auth.login_required
def delete_task(task_id: int) -> object:
    task = Task.query.get(task_id)
    if task is None:
        return not_found(f'task {task_id} was not found')
    try:
        db.session.delete(task)
        db.session.commit()
    except SQLAlchemyError as error:
        db.session.rollback()
        return server_error('failed to delete the task!')
    response = {'status': 200, 'message': f'task {task_id} was deleted'}
    return make_response(jsonify(response))


# Удалить пользователя
@app.route('/delete_user', methods=['DELETE'])
@auth.login_required
def delete_user() -> object:
    user = User.check_login(auth.username())
    if user is None:
        return not_found(f'user {auth.username()} was not found')
    tasks_user = Task.query.filter_by(user_id=user.id).all()
    try:
        for task in tasks_user:
            db.session.delete(task)
        db.session.delete(user)
        db.session.commit()
    except SQLAlchemyError as error:
        db.session.rollback()
        return server_error('failed to delete the user!')
    response = {'status': 200, 'message': f'user {auth.username()} was deleted'}
    return make_response(jsonify(response))