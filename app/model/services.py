"""Business logic of the app List of tasks
"""
from datetime import datetime

from sqlalchemy.exc import SQLAlchemyError

from app import db
from app.model.models import Task, User


def check_login(login: str) -> User:
    """Checking login in the database

    :param login: User`s login
    :return: object User or None

    """

    return User.query.filter_by(login=login).first()


def create_user(login: str, password: str) -> (int, str, User):
    """Creates a user in the database

    :param login: User`s login
    :param password: User`s password
    :return: (id, message, user): id - code [0 - OK, 1 - Data error, 2 - Database error];
                                  message - a completion message
                                  user - object User

    """
    user = check_login(login)
    if user is not None:
        return 1, f'this login={login} is busy', user
    user = User(login=login)
    user.set_password(password)
    try:
        db.session.add(user)
        db.session.commit()
    except SQLAlchemyError as error:
        db.session.rollback()
        return 2, f'failed to add a user with login={login}!', user
    return 0, f'user with login={login} created', user


def create_task(data: dict, user: User) -> (int, str, Task):
    """Creates a task in the database

    :param data: json object with the fields: title, description, and deadline
    :param user: object User
    :return: (id, message, task): id - code [0 - OK, 1 - Data error, 2 - Database error];
                                  message - a completion message
                                  task - object Task

    """

    task = Task(user_id=user.id, done=False)
    try:
        data['deadline'] = datetime.strptime(data['deadline'], "%Y-%m-%d %H:%M")  # Из str в форматированный DateTime
    except ValueError:
        return 1, 'wrong format deadline (yyyy-mm-dd hh:mm)', task
    task.from_dict(data)
    try:
        db.session.add(task)
        db.session.commit()
    except SQLAlchemyError as error:
        db.session.rollback()
        return 2, f'failed to create an task {task.title}!', task
    return 0, f'task {task.title} created', task


def get_tasks(user: User) -> list:
    """Gets all the user's tasks

    :param user: object User
    :return: list objects Task

    """

    return user.tasks.all()


def get_task(user: User, task_id: int) -> Task:
    """Get a user's task by id

    :param user: object User
    :param task_id: id a task
    :return: object Task

    """

    return user.tasks.filter_by(id=task_id).first()


def done_task(user: User, task_id: int) -> (int, str, Task):
    """Marks the task as completed
    :param user: object User
    :param task_id:  id a task
    :return: (id, message, task): id - code [0 - OK, 1 - Data error, 2 - Database error];
                                  message - a completion message
                                  task - object Task

    """

    task = user.tasks.filter_by(id=task_id).first()
    if task is None:
        return 1, f'the task with id={task_id} doesn`t exist', task
    task.done = True
    try:
        db.session.commit()
    except SQLAlchemyError as error:
        db.session.rollback()
        return 2, f'failed to mark the task with id={task_id} as completed!', task
    return 0, f'the task with id={task_id} is marked as completed', task


def delete_user(login: str)-> (int, str):
    """Deletes a user

    :param login:  user login
    :return: (id, message): id - code [0 - OK, 1 - Data error, 2 - Database error];
                            message - a completion message

    """
    user = check_login(login)
    if user is None:
        return 1, f'user {login} was not found'
    tasks_user = Task.query.filter_by(user_id=user.id).all()
    try:
        for task in tasks_user:
            db.session.delete(task)
        db.session.delete(user)
        db.session.commit()
    except SQLAlchemyError as error:
        db.session.rollback()
        return 2, 'failed to delete the user!'
    return 0, f'user {login} was deleted'


def delete_task(task_id: int) -> (int, str):
    """Deletes an task

    :param task_id:  id a task
    :return: (id, message): id - code [0 - OK, 1 - Data error, 2 - Database error];
                            message - a completion message

    """

    task = Task.query.get(task_id)
    if task is None:
        return 1, f'task {task_id} was not found'
    try:
        db.session.delete(task)
        db.session.commit()
    except SQLAlchemyError as error:
        db.session.rollback()
        return 2, 'failed to delete the task!'
    return 0, f'task {task_id} was deleted'
