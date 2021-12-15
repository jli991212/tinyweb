from datetime import datetime
from unwrap import db, login_manager
from flask_login import UserMixin
from flask import flash
from sqlalchemy.sql import expression
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(20), unique=False, nullable=False)
    lastname = db.Column(db.String(20), unique=False, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    cart = db.relationship('Cart', backref='buyer', lazy=True)

    def add_to_cart(self, product_id):
        item_to_add = Cart(product_id=product_id, user_id=self.id)
        db.session.add(item_to_add)
        db.session.commit()
        flash('Your item has been added to your cart!', 'success')

    def __repr__(self):
        return f"User('{self.firstname}','{self.lastname}', '{self.email}','{self.id}')"


class Products(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text, nullable=False)
    number = db.Column(db.Integer, nullable=False)
    image = db.Column(db.String(100))
    category = db.Column(db.String(100), nullable=False)
    deleted = db.Column(db.Boolean, server_default=expression.false(), nullable=False)

    def __repr__(self):
        return f"('{self.id}','{self.name}', '{self.price}','{self.description}','{self.number}', '{self.image}','{self.category}', '{self.deleted}')"

    def __init__(self, name, price, category, number, description, image, deleted):
        self.image = image
        self.name = name
        self.price = price
        self.category = category
        self.description = description
        self.number = number
        self.deleted = deleted


class Cart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    number = db.Column(db.Integer, nullable=False, default=0)

    def update_qty(self, qty):
        cartitem = Cart.query.filter_by(product_id=self.id).first()
        cartitem.quantity = qty
        db.session.commit()

    def __repr__(self):
        return f"Cart('Product id:{self.product_id}','id: {self.id}','User id:{self.user_id}'')"

