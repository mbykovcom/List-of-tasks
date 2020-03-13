import unittest
from app import app
from json import dumps, loads
from base64 import b64encode


class TestRoutes(unittest.TestCase):
    def setUp(self) -> None:
        self.app = app.test_client()
        self.user = {'login': 'test_user', 'password': 'pass'}
        self.auth = {
            'Authorization': 'Basic ' + b64encode(f"{self.user['login']}:{self.user['password']}".encode()).decode()}
        self.app.post('/create_user', data=dumps(self.user), content_type='application/json')

    def tearDown(self) -> None:
        self.app.delete('/delete_user', headers=self.auth)

    def test_unauthorized_access(self):
        unauthorized_access = self.app.get('/tasks')
        json_answer = loads(unauthorized_access.data)
        self.assertEqual(unauthorized_access.status_code, 401, 'unauthorized_access - wrong status code')
        self.assertEqual(json_answer['message'], 'unauthorized access', 'unauthorized_access - wrong json answer')

    # Проверка отображение веб-инструкция к API List of Tasks
    def test_index(self):
        index_page = self.app.get('/')
        self.assertEqual(index_page.status_code, 200, 'index - wrong status code')
        self.assertIn(f'List of tasks', index_page.data.decode('UTF-8'))


    def test_create_user(self):
        # Если никаких данных переданно не было
        user = {}
        create_user = self.app.post('/create_user', data=dumps(user), content_type='application/json')
        json_answer = loads(create_user.data)
        self.assertEqual(json_answer['message'], 'missing json request', 'create_user - wrong json answer')
        self.assertEqual(create_user.status_code, 400, 'create_user - wrong status code')
        # Передан только login
        user['login'] = 'created_user'
        create_user = self.app.post('/create_user', data=dumps(user), content_type='application/json')
        json_answer = loads(create_user.data)
        self.assertEqual(json_answer['message'], 'the password field is missing', 'create_user - wrong json answer')
        self.assertEqual(create_user.status_code, 400, 'create_user - wrong status code')
        # Переданны login и password
        user['password'] = 'pass'
        create_user = self.app.post('/create_user', data=dumps(user), content_type='application/json')
        json_answer = loads(create_user.data)
        self.assertEqual(create_user.status_code, 201, 'create_user - wrong status code')
        self.assertEqual(json_answer['message'], f'user {user["login"]} created', 'create_user - wrong json answer')
        # Пользователь с таким login существует
        create_user = self.app.post('/create_user', data=dumps(user), content_type='application/json')
        json_answer = loads(create_user.data)
        self.assertEqual(create_user.status_code, 400, 'create_user - wrong status code')
        self.assertEqual(json_answer['message'], 'this login is busy', 'create_user - wrong json answer')
        # Передан только password
        user.pop('login')
        create_user = self.app.post('/create_user', data=dumps(user), content_type='application/json')
        json_answer = loads(create_user.data)
        self.assertEqual(json_answer['message'], 'the login field is missing', 'create_user - wrong json answer')
        self.assertEqual(create_user.status_code, 400, 'create_user - wrong status code')

    def test_delete_user(self):
        # Удалиться может только аторизованный пользователь
        user = {'login': 'created_user', 'password': 'pass'}
        headers = {'Authorization': 'Basic ' + b64encode(f"{user['login']}:{user['password']}".encode()).decode()}
        delete_user = self.app.delete('/delete_user', headers=headers)
        json_answer = loads(delete_user.data)
        self.assertEqual(delete_user.status_code, 200, 'delete_user - wrong status code')
        self.assertEqual(json_answer['message'], f'user {user["login"]} was deleted', 'delete_user - wrong json answer')

    def test_create_task(self):
        # Поля для создания задачи пустые
        task = {}
        create_task = self.app.post('/create_task', headers=self.auth, data=dumps(task),
                                    content_type='application/json')
        json_answer = loads(create_task.data)
        self.assertEqual(json_answer['message'], 'missing json request', 'create_task - wrong json answer [message]')
        self.assertEqual(create_task.status_code, 400, 'create_task - wrong status code')
        # Передан только title задачи
        task['title'] = 'test task'
        create_task = self.app.post('/create_task', headers=self.auth, data=dumps(task),
                                    content_type='application/json')
        json_answer = loads(create_task.data)
        self.assertEqual(json_answer['message'], 'the description field is missing',
                         'create_task - wrong json answer [message]')
        self.assertEqual(create_task.status_code, 400, 'create_task - wrong status code')
        # Переданы title и description
        task['description'] = 'test description'
        create_task = self.app.post('/create_task', headers=self.auth, data=dumps(task),
                                    content_type='application/json')
        json_answer = loads(create_task.data)
        self.assertEqual(json_answer['message'], 'the deadline field is missing',
                         'create_task - wrong json answer [message]')
        self.assertEqual(create_task.status_code, 400, 'create_task - wrong status code')
        # Передан невалидный deadline
        task['deadline'] = '13.03.2020'
        create_task = self.app.post('/create_task', headers=self.auth, data=dumps(task),
                                    content_type='application/json')
        json_answer = loads(create_task.data)
        self.assertIsInstance(json_answer, dict, 'create_task - no json response')
        self.assertEqual(create_task.status_code, 400, 'create_task - wrong status code')
        self.assertEqual(json_answer['message'], 'wrong format deadline (yyyy-mm-dd hh:mm)',
                         'create_task - wrong json answer [message]')
        # Переданы все данные для создания задачи
        task['deadline'] = '2020-03-13 10:00'
        create_task = self.app.post('/create_task', headers=self.auth, data=dumps(task),
                                    content_type='application/json')
        json_answer = loads(create_task.data)
        self.assertIsInstance(json_answer, dict, 'create_task - no json response')
        self.assertEqual(create_task.status_code, 201, 'create_task - wrong status code')
        self.assertEqual(json_answer['task']['title'], task['title'], 'create_task - wrong json answer task[title]')
        self.assertEqual(json_answer['task']['description'], task['description'],
                         'create_task - wrong json answer task[description]')
        self.assertEqual(json_answer['task']['deadline'], task['deadline'],
                         'create_task - wrong json answer task[deadline]')
        self.assertEqual(json_answer['task']['done'], False, 'create_task - wrong json answer task[done]')
        # Переданы description и deadline
        task.pop('title')
        create_task = self.app.post('/create_task', headers=self.auth, data=dumps(task),
                                    content_type='application/json')
        json_answer = loads(create_task.data)
        self.assertEqual(json_answer['message'], 'the title field is missing',
                         'create_task - wrong json answer [message]')
        self.assertEqual(create_task.status_code, 400, 'create_task - wrong status code')

    def test_get_tasks(self):
        # Если список еще пуст
        get_tasks = self.app.get('/tasks', headers=self.auth)
        json_answer = loads(get_tasks.data)
        self.assertEqual(get_tasks.status_code, 200, 'get_tasks - wrong status code')
        self.assertEqual(len(json_answer['tasks']), 0, 'get_tasks - wrong json answer')
        # Добавление в список задачи и отображение полного списка задач
        task = {'title': 'test task', 'description': 'test description', 'deadline': '2020-03-13 10:00'}
        self.app.post('/create_task', headers=self.auth, data=dumps(task), content_type='application/json')
        get_tasks = self.app.get('/tasks', headers=self.auth)
        json_answer = loads(get_tasks.data)
        self.assertEqual(get_tasks.status_code, 200, 'get_tasks - wrong status code')
        self.assertEqual(len(json_answer['tasks']), 1, 'get_tasks - wrong json answer')
        self.assertEqual(list(json_answer['tasks'][0].keys()), ['deadline', 'description', 'done', 'id', 'title'],
                         'get_tasks - wrong json answer')

    def test_get_task(self):
        # Если отсутствует задача с таким id
        get_task = self.app.get('/tasks/10', headers=self.auth)
        json_answer = loads(get_task.data)
        self.assertEqual(get_task.status_code, 404, 'get_task - wrong status code')
        self.assertEqual(json_answer['message'], 'task 10 was not found', 'create_task - wrong json answer [message]')
        # Добавление задачи и просмотр по id
        task = {'title': 'test task', 'description': 'test description', 'deadline': '2020-03-13 10:00'}
        create_task = self.app.post('/create_task', headers=self.auth, data=dumps(task),
                                    content_type='application/json')
        json_answer = loads(create_task.data)
        get_tasks = self.app.get(f'/tasks/{json_answer["task"]["id"]}', headers=self.auth)
        json_answer = loads(get_tasks.data)
        self.assertEqual(get_tasks.status_code, 200, 'get_task - wrong status code')
        self.assertEqual(list(json_answer.keys()), ['deadline', 'description', 'done', 'id', 'title'],
                         'get_tasks - wrong json answer')

    def test_done(self):
        # Выполнить несуществующую задачу
        done_task = self.app.put(f'/done/1', headers=self.auth)
        json_answer = loads(done_task.data)
        self.assertEqual(done_task.status_code, 404, 'done_task - wrong status code')
        self.assertEqual(json_answer['message'], 'task 1 was not found', 'done_task - wrong json answer [message]')
        # Добавление и выполнение задачи по id
        task = {'title': 'test task', 'description': 'test description', 'deadline': '2020-03-13 10:00'}
        create_task = self.app.post('/create_task', headers=self.auth, data=dumps(task),
                                    content_type='application/json')
        json_answer = loads(create_task.data)
        done_task = self.app.put(f'/done/{json_answer["task"]["id"]}', headers=self.auth)
        json_answer = loads(done_task.data)
        self.assertEqual(done_task.status_code, 200, 'done_task - wrong status code')
        self.assertEqual(json_answer['message'], f'task {json_answer["task"]["id"]} was completed',
                         'done_task - wrong json answer [message]')
        self.assertEqual(json_answer['task']['done'], True, 'done_task - wrong json answer [done]')

    def test_delete_task(self):
        # Удалить несуществующую задачу
        delete_task = self.app.delete('/delete_task/10', headers=self.auth)
        json_answer = loads(delete_task.data)
        self.assertEqual(delete_task.status_code, 404, 'delete_task - wrong status code')
        self.assertEqual(json_answer['message'], 'task 10 was not found', 'delete_task - wrong json answer [message]')
        # Добавить и удалить задачу по id
        task = {'title': 'test task', 'description': 'test description', 'deadline': '2020-03-13 10:00'}
        create_task = self.app.post('/create_task', headers=self.auth, data=dumps(task),
                                    content_type='application/json')
        id_task = loads(create_task.data)["task"]["id"]
        delete_task = self.app.delete(f'/delete_task/{id_task}', headers=self.auth)
        json_answer = loads(delete_task.data)
        self.assertEqual(delete_task.status_code, 200, 'delete_task - wrong status code')
        self.assertEqual(json_answer['message'], f'task {id_task} was deleted',
                         'delete_task - wrong json answer [message]')


if __name__ == '__main__':
    unittest.main()
