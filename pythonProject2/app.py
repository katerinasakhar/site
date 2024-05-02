from flask import Flask, render_template, url_for, request,redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date
from dateutil.relativedelta import relativedelta


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)



class User(db.Model):
    __tablename__='users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    login=db.Column(db.String(50),nullable=False)
    products=db.relationship('Products')
    def __repr__(self):
        return '<User %r>' % self.id

class Products(db.Model):
    __tablename__ = 'products'
    id=db.Column(db.Integer,primary_key=True)
    user_id=db.Column(db.Integer, db.ForeignKey('users.id'))
    name=db.Column(db.String(100),nullable=False)
    date=db.Column(db.DateTime,nullable=False)
    death_date=db.Column(db.DateTime,nullable=False)
    def __repr__(self):
        return '<Products %r>' % self.id



@app.route('/')
def index():
    return render_template("index.html")


@app.route('/<user_id>/about')
def about():
    return render_template("about.html")


@app.route('/<int:user_id>/products')
def products(user_id):
    products=Products.query.filter_by(user_id=user_id).all()
    return render_template("products.html",products=products,id=user_id)


@app.route('/<int:user_id>/products/<int:id>/del')
def product_delete(user_id,id):
    product=Products.query.get_or_404(id)
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
        product=Products(name=name,date=production_date,death_date=death_date,user_id=user_id)
        try:
            db.session.add(product)
            db.session.commit()
            return redirect('/{}/products'.format(user_id))
        except:
            return "При добавлении продукта произошла ошибка"

    else:
        return render_template("add_product.html")

@app.route ('/sign-in',methods=['POST','GET'])
def sign_in():
    if request.method=="POST":
        l=request.form["login"]
        logins = User.query.with_entities(User.login).all()
        login_values = [login[0] for login in logins]
        if l in login_values:
            id=User.query.filter_by(login=l).first().id
            return redirect('/{}'.format(id))
        else:
            return render_template("sign-in_error.html",login=l)
    return render_template("sign-in.html")

@app.route('/registration',methods=['POST', 'GET'])
def registration():
    if request.method=="POST":
        logins = User.query.with_entities(User.login).all()
        login_values = [login[0] for login in logins]
        name = request.form["user_name"]
        login = request.form["login"]
        if login in login_values:
            print("yes")
            return render_template("registration_exist_login_error.html",name=name,login=login)

        user=User(name=name,login=login)
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
    return render_template("main.html",id=id)



if __name__ == "__main__":
    app.run(debug=True)
