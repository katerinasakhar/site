from flask import Flask, render_template, url_for, request,redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date
from dateutil.relativedelta import relativedelta

app = Flask(__name__)
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///user.db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///products.db'
db = SQLAlchemy(app)



# class User(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(50), nullable=False)
#     surname = db.Column(db.String(50))
#     user_mail = db.Column(db.String, nullable=False)
#     def __repr__(self):
#         return '<User %r>' % self.id

class Products(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(100),nullable=False)
    date=db.Column(db.DateTime,nullable=False)
    death_date=db.Column(db.DateTime,nullable=False)
    def __repr__(self):
        return '<Products %r>' % self.id

@app.route('/')
def index():
    return render_template("index.html")


@app.route('/about')
def about():
    return render_template("about.html")


@app.route('/products')
def products():
    products=Products.query.order_by(Products.date).all()
    return render_template("products.html",products=products)


@app.route('/add-product', methods=['POST', 'GET'])
def add_product():
    if request.method == "POST":
        name = request.form['name_product']
        production_date = date.fromisoformat(request.form['production_date'])
        days=0
        weeks=0
        months=0
        years=0
        if len(request.form['days'])>0:
            days = int(request.form['days'])
        if len(request.form['weeks']) > 0:
            weeks = int(request.form['weeks'])
        if len(request.form['months']) > 0:
            months=int(request.form['months'])
        if len(request.form['years']) > 0:
            years = int(request.form['years'])
        delta=relativedelta(years=years,months=months,days=days,weeks=weeks)
        death_date=production_date+delta
        product=Products(name=name,date=production_date,death_date=death_date)
        try:
            db.session.add(product)
            db.session.commit()
            return redirect('/products')
        except:
            return "При добавлении продукта произошла ошибка"

    else:
        return render_template("add_product.html")


@app.route('/user/<string:name>/<int:id>')
def user(name, id):
    return "User page " + name + " " + str(id)


if __name__ == "__main__":
    app.run(debug=True)
