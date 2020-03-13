# List-of-tasks
Веб-сервис предоставляющий RESTful API для управления персональным списком задач

Работать с веб-сервисом могут только авторизованные пользователи!

Функции RESTful API:

#### 1. Создать пользователя (url/create_user) [POST запрос]


##### Тело JSON:

	 {
        "login": "user1",
        "password": "pass"
     }
	

##### Ответ сервера:
    
     {
        "status": 201,
        "message": "user user1 created"
     }

#### 2. Удалить пользователя (url/delete_user) [DELETE запрос]
	
##### Ответ сервера:

	 {
        "message": "user user1 was deleted",
        "status": 200
     }

#### 3. Создать задачу (url/create_task) [POST запрос]
	
##### Тело JSON:

	 {
        "title": "Task 1",
        "description": "Description 1",
        "deadline": "2020-03-12 15:00"
     }
     
##### Ответ сервера:

	 {
        "status": 201,
        "task": {
            "deadline": "2020-03-12 15:00",
            "description": "Description 1",
            "done": false,
            "id": 1,
            "title": "Task 1"
        }
     }
    
#### 4. Удалить задачу (url/delete_task/1) [DELETE запрос]
	
##### Ответ сервера:

     {
        "message": "Task 1 was deleted",
        "status": 200
     }

#### 5. Получить список задач (url/tasks) [GET запрос]
	
##### Ответ сервера:
   
   	 {
        "tasks": [
            {
                "deadline": "2020-03-12 15:00",
                "description": "Description 1",
                "done": false,
                "id": 1,
                "title": "Task 1"
            }
	    ]
	 }
	
#### 6. Получить задачу по id (url/tasks/1) [GET запрос]
	
##### Ответ сервера:
    
     {
        "tasks":
            {
                "deadline": "2020-03-12 15:00",
                "description": "Description 1",
                "done": false,
                "id": 1,
                "title": "Task 1"
            }
     }

#### 7. Отметить задачу как выполненную (url/done/1) [PUT запрос]
	
##### Ответ сервера:

	 {
        "message": "Task 1 was completed",
        "status": 200,
        "task": {
            "deadline": "2020-03-12 15:00",
            "description": "Description 1",
            "done": true,
            "id": 1,
            "title": "Task "
        }
     }
