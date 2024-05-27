from flask_sqlalchemy import SQLAlchemy
from app import app

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    login = db.Column(db.String(50), nullable=False)
    products = db.relationship('Products')

    def __repr__(self):
        return '<User %r>' % self.id


class Products(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    name = db.Column(db.String(100), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    death_date = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        return '<Products %r>' % self.id

class UserChat(db.Model):
    __tablename__ = 'user_chats'
    id = db.Column(db.Integer, primary_key=True)
    chat_id = db.Column(db.String(50), nullable=False)
    login = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return '<UserChat %r>' % self.id