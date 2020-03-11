from flask import Flask

app = Flask(__name__)


@app.route('/tasks', methods=['GET'])
def get_tasks():
    pass


@app.route('/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    pass


@app.route('/done/<int:task_id>', methods=['PUT'])
def done_task(task_id):
    pass


@app.route('/create_tasks', methods=['POST'])
def create_task():
    pass


@app.route('/delete/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    pass


if __name__ == '__main__':
    app.run(debug=True)