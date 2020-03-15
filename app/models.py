from werkzeug.security import generate_password_hash, check_password_hash

from app import db


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(64))
    description = db.Column(db.String(256))
    deadline = db.Column(db.DateTime)
    done = db.Column(db.Boolean)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return f'<Task {self.title}>'

    def to_dict(self) -> dict:
        data = {'id': self.id,
                'title': self.title,
                'description': self.description,
                'deadline': self.deadline.strftime("%Y-%m-%d %H:%M"),
                'done': self.done}
        return data

    def from_dict(self, data: dict):
        for field in ['title', 'description', 'deadline']:
            if field in data:
                setattr(self, field, data[field])


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(64), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    tasks = db.relationship('Task', backref='owner', lazy='dynamic')

    def __repr__(self):
        return '<User {}>'.format(self.login)

    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)
