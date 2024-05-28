# -*- coding: utf-8 -*-
from flask import Flask, render_template, url_for, request, redirect
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from database import db, User, Products
from app import app


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/<user_id>/about')
@app.route('/about')
def about(user_id):
    return render_template("about.html")


@app.route('/<int:user_id>/products')
def products(user_id):
    products = Products.query.filter_by(user_id=user_id).all()
    return render_template("products.html", products=products, id=user_id)


@app.route('/<int:user_id>/products/<int:id>/del')
def product_delete(user_id, id):
    product = Products.query.get_or_404(id)
    try:
        db.session.delete(product)
        db.session.commit()
        return redirect('/{}/products'.format(user_id))
    except:
        return "При удалении продукта произошла ошибка"


@app.route('/<int:user_id>/add-product', methods=['POST', 'GET'])
def add_product(user_id):
    if request.method == "POST":
        name = request.form['name_product']
        production_date = date.fromisoformat(request.form['production_date'])
        days = 0
        weeks = 0
        months = 0
        years = 0
        if request.form['days']:
            days = int(request.form['days'])
        if request.form['weeks']:
            weeks = int(request.form['weeks'])
        if request.form['months']:
            months = int(request.form['months'])
        if request.form['years']:
            years = int(request.form['years'])
        delta = relativedelta(years=years, months=months, days=days, weeks=weeks)
        death_date = production_date + delta
        product = Products(name=name, date=production_date, death_date=death_date, user_id=user_id)
        try:
            db.session.add(product)
            db.session.commit()
            return redirect('/{}/products'.format(user_id))
        except:
            return "При добавлении продукта произошла ошибка"

    else:
        return render_template("add_product.html")


@app.route('/sign-in', methods=['POST', 'GET'])
def sign_in():
    if request.method == "POST":
        l = request.form["login"]
        logins = User.query.with_entities(User.login).all()
        login_values = [login[0] for login in logins]
        if l in login_values:
            id = User.query.filter_by(login=l).first().id
            return redirect('/{}'.format(id))
        else:
            return render_template("sign-in_error.html", login=l)
    return render_template("sign-in.html")


@app.route('/registration', methods=['POST', 'GET'])
def registration():
    if request.method == "POST":
        logins = User.query.with_entities(User.login).all()
        login_values = [login[0] for login in logins]
        name = request.form["user_name"]
        login = request.form["login"]
        if login in login_values:
            print("yes")
            return render_template("registration_exist_login_error.html", name=name, login=login)

        user = User(name=name, login=login)
        try:
            db.session.add(user)
            db.session.commit()

            return redirect('/{}'.format(user.id))
        except:
            return "При регистрации произошла ошибка"
    else:
        return render_template("registration.html")


@app.route('/<int:id>')
def user_page(id):
    return render_template("main.html", id=id)
