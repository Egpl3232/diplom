from . import db
from flask_login import UserMixin
from datetime import datetime as dt


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(30), nullable= False)
    password = db.Column(db.String(500), nullable = False)


class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    basket_ref = db.relationship('Basket', backref='customer')

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)
    subcategorys = db.relationship('SubCategory', backref='subcats') 

class SubCategory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)
    product_ref = db.relationship('Product', backref='subcat')
    category_ref = db.Column(db.Integer, db.ForeignKey(Category.id))


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable = False)
    price = db.Column(db.Integer, nullable = False)
    description = db.Column(db.String(100), nullable = False)
    primary_img = db.Column(db.String(100), nullable = False)
    secondary_img = db.Column(db.String(100), nullable = False)

    subcategory = db.Column(db.Integer, db.ForeignKey(SubCategory.id))
    sales = db.Column(db.Integer, default=0)
    date = db.Column(db.DateTime, default=dt.utcnow)
    sizes = db.relationship('Product_size', backref='product_size')

class Product_size(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    size = db.Column(db.String(7), nullable = False)
    ost = db.Column(db.Integer)
    product = db.Column(db.Integer, db.ForeignKey(Product.id))
    basket_ref = db.relationship('Basket', backref='product')

class Basket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Integer, default=1)

    cust_id = db.Column(db.Integer, db.ForeignKey(Customer.id))
    item_size = db.Column(db.Integer, db.ForeignKey(Product_size.id))


class Promocode(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(20))
    discount = db.Column(db.Integer)
    count = db.Column(db.Integer)


class Order(db.Model):
    id = db.Column(db.Integer, primary_key = True)

    cust_id = db.Column(db.Integer, db.ForeignKey(Customer.id))
    items = db.Column(db.String(400))
    delivery = db.Column(db.String(1000))
    pay_type = db.Column(db.String(20))
    promocode = db.Column(db.Integer, db.ForeignKey(Promocode.id))
    total = db.Column(db.Integer)
