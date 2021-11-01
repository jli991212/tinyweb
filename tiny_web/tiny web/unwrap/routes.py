import os
#import secrets
from flask import render_template, url_for, flash, redirect, request
from unwrap import app, db, bcrypt
from unwrap.forms import RegistrationForm, LoginForm, UpdateAccountForm,addproductsForm,updateproductForm
from unwrap.models import User, Products, Cart
from flask_login import login_user, current_user, logout_user, login_required
from sqlalchemy import func, update
from werkzeug.utils import secure_filename
from flask_paginate import Pagination
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
def getLoginDetails():
    if current_user.is_authenticated:
        noOfItems = Cart.query.filter_by(buyer=current_user).count()
    else:
        noOfItems = 0
    return noOfItems


@app.route("/")
@app.route("/home")
def home():
    noOfItems = getLoginDetails()
    return render_template('home.html', noOfItems=noOfItems)

@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(lastname=form.lastname.data,firstname=form.firstname.data,email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():

    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()

        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get("next")
            return redirect(next_page) if next_page else redirect(url_for('select_products'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', title='Login', form=form)



@app.route("/root_login", methods=['GET', 'POST'])
def root_login():
    admin_email= 'root123@gmail.com'
   # admin_password = 'root123456789'
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        root = User.query.filter_by(email=admin_email).first()
        if root and bcrypt.check_password_hash(root.password, form.password.data):
            login_user(root, remember=form.remember.data)
            next_page = request.args.get("next")
            return redirect(next_page) if next_page else redirect(url_for('admin_page'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', title='Login', form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():

    form = UpdateAccountForm()
    if form.validate_on_submit():
        current_user.lastname = form.lastname.data
        current_user.firstname = form.firstname.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.lastname.data = current_user.lastname
        form.firstname.data = current_user.firstname
        form.email.data = current_user.email
    return render_template('account.html', title='Account',
                           form=form)

@app.route("/about")
def about():
    noOfItems = getLoginDetails()
    return render_template("about.html", noOfItems=noOfItems)
@app.route("/contact")
def contact():
    noOfItems = getLoginDetails()
    return render_template("contact.html", noOfItems=noOfItems)

@app.route("/admin_page")
@login_required
def admin_page():
    noOfItems = getLoginDetails()
    if current_user.email == 'root123@gmail.com':
        return render_template("admin_page.html", noOfItems=noOfItems)
    else:
        return render_template("home.html", noOfItems=noOfItems)


@app.route("/admin_products", methods=['GET', 'POST'])
@login_required
def admin_products():

    #limit = 6
    noOfItems = getLoginDetails()
    if current_user.email != 'root123@gmail.com':
        return render_template("home.html", noOfItems=noOfItems)
    page = request.args.get('page', 1, type=int)
    products = Products.query.filter(Products.deleted==False).paginate(page,4)
    return render_template('admin_products.html', products=products, noOfItems=noOfItems)

@app.route("/select_products", methods=['GET', 'POST'])
def select_products():
    noOfItems = getLoginDetails()
    page = request.args.get('page', 1, type=int)
    products = Products.query.filter(Products.deleted==False).paginate(page,4)
    return render_template('select_products.html', products=products, noOfItems=noOfItems)
@app.route("/search_view", methods=['POST','GET'])
def search_view():
    noOfItems = getLoginDetails()
    page = request.args.get('page', 1, type=int)
    products = Products.query.filter(Products.deleted==False).paginate(page,4)
    if request.method == 'POST':
        tag = request.form['tag']
        #search = "%()%".format(tag)
        products = Products.query.filter(Products.name.contains(tag),Products.deleted==False).paginate(page,4)
        #item = products.items
        return render_template('serach_view.html', products=products, noOfItems=noOfItems)
    else:
        return render_template('serach_view.html', products=products, noOfItems=noOfItems)
@app.route("/catalyst")
def catalyst():
    noOfItems = getLoginDetails()
    page = request.args.get('page', 1, type=int)
    products = Products.query.filter(Products.category=='2',Products.deleted==False).paginate(page,4)
    return render_template('select_products.html', products=products, noOfItems=noOfItems)
@app.route("/materiel")
def materiel():
    noOfItems = getLoginDetails()
    page = request.args.get('page', 1, type=int)
    products = Products.query.filter(Products.category=='1',Products.deleted==False).paginate(page,4)
    return render_template('select_products.html', products=products, noOfItems=noOfItems)


@app.route('/add_products', methods=['GET', 'POST'])
@login_required
def add_products():
    noOfItems = getLoginDetails()
    if current_user.email != 'root123@gmail.com':
        return render_template("home.html", noOfItems=noOfItems)
    form = addproductsForm(request.form, csrf_enabled=False)
    if form.validate_on_submit():
        name = form.name.data
        price = form.price.data
        description = form.description.data
        number = form.number.data
        category= form.category.data
        #category = Category.query.get_or_404(form.category.data)
        image = request.files['image']
        filename = ''
        if image and allowed_file(image.filename):
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        product = Products(name, price, description=description, number=number,category=category, image=filename, deleted=False)
        db.session.add(product)
        db.session.commit()
        flash('The product %s has been created' % name, 'success')
        return redirect(url_for('admin_products'))

    if form.errors:
        flash(form.errors, 'danger')
    return render_template('add_products.html', form = form)
@app.route('/edit_products/<int:product_id>', methods=['GET', 'POST'])
@login_required
def edit_products(product_id):
    noOfItems = getLoginDetails()
    if current_user.email != 'root123@gmail.com':
        return render_template("home.html", noOfItems=noOfItems)
    form = updateproductForm(request.form, csrf_enabled=False)
    update = Products.query.get_or_404(product_id)
    if form.validate_on_submit():
        update.name = form.name.data
        update.price = form.price.data
        update.description= form.description.data
        update.number = form.number.data
        update.category= form.category.data
        #category = Category.query.get_or_404(form.category.data)
        image = request.files['image']
        filename = ''
        if image and allowed_file(image.filename):
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        update.image=filename
        db.session.commit()

        return redirect(url_for('admin_products'))

    if form.errors:
        flash(form.errors, 'danger')
    return render_template('edit_products.html', form = form, update=update)
@app.route("/detail/<int:id>", methods=['GET', 'POST'])
def detail(id):
    noOfItems = getLoginDetails()
    products = Products.query.filter(Products.id==id)
    return render_template('detail.html', products=products, noOfItems=noOfItems)
@app.route("/admin_detail/<int:id>", methods=['GET', 'POST'])
def admin_detail(id):
    noOfItems = getLoginDetails()
    products = Products.query.filter(Products.id==id)
    return render_template('admin_detail.html', products=products, noOfItems=noOfItems)




@app.route('/delete_products/<int:product_id>')
@login_required
def delete_products(product_id):
    noOfItems = getLoginDetails()
    if current_user.email != 'root123@gmail.com':
        return render_template("home.html", noOfItems=noOfItems)
    delete = Products.query.get_or_404(product_id)
    try:
        #db.session.delete(delete)
        delete.deleted=True
        db.session.commit()
        flash('Products  soft delete successfully!')
        return redirect(url_for('admin_products'))
    except:
        flash('there some problem happened try again!')
        return redirect(url_for('admin_products'))
@app.route('/delete_database_products/<int:product_id>')
@login_required
def delete_database_products(product_id):
    noOfItems = getLoginDetails()
    if current_user.email != 'root123@gmail.com':
        return render_template("home.html", noOfItems=noOfItems)
    delete = Products.query.get_or_404(product_id)
    try:
        db.session.delete(delete)
        delete.deleted=True
        db.session.commit()
        flash('Products  delete from the database successfully!')
        return redirect(url_for('admin_products'))
    except:
        flash('there some problem happened try again!')
        return redirect(url_for('admin_products'))

@app.route("/addToCart/<int:pid>")
@login_required
def addToCart(pid):
    # check if product is already in cart
    row = Cart.query.filter_by(product_id=pid, buyer=current_user).first()
    product = Products.query.get_or_404(pid)
    if row:
        # if in cart update quantity : +1
        row.quantity += 1
        product.number -= 1
        db.session.commit()
        flash('This item is already in your cart, 1 quantity added!', 'success')
    else:
        user = User.query.get(current_user.id)
        user.add_to_cart(pid)
        product.number -= 1
        db.session.commit()
    return redirect(url_for('select_products'))
@app.route("/cart", methods=["GET", "POST"])
@login_required
def cart():
    noOfItems = getLoginDetails()
    # display items in cart
    cart = Products.query.join(Cart).add_columns(Cart.quantity, Products.price, Products.name, Products.id,Products.image,
                                                 Products.number, Products.deleted).filter_by(buyer=current_user).all()
    subtotal = 0

    for item in cart:
        subtotal+=float(item.price)*int(item.quantity)

    if request.method == "POST":
        qty = request.form.get("qty")
        idpd = request.form.get("idpd")
        cartitem = Cart.query.filter_by(product_id=idpd).first()
        product=Products.query.get_or_404(idpd)
        cartitem.quantity = qty
        if int(product.number) > int(cartitem.quantity):
            product.number -= int(cartitem.quantity)
            product.deleted = False
            db.session.commit()
            cart = Products.query.join(Cart).add_columns(Cart.quantity, Products.price, Products.name, Products.id,Products.image,
                                                         Products.number,Products.deleted).filter_by(buyer=current_user).all()
            subtotal = 0
            for item in cart:
                subtotal+=float(item.price)*int(item.quantity)
        if int(product.number) == int(cartitem.quantity):
            product.number -= int(cartitem.quantity)
            flash('No more item can be added')
            product.deleted = True
            db.session.commit()
        if int(product.number) < int(cartitem.quantity):
            cartitem.quantity = product.number
            db.session.commit()
    return render_template('cart.html', cart=cart, noOfItems=noOfItems, subtotal=subtotal)

@app.route("/removeFromCart/<int:product_id>")
@login_required
def removeFromCart(product_id):
    item_to_remove = Cart.query.filter_by(product_id=product_id, buyer=current_user).first()
    product = Products.query.get_or_404(product_id)
    product.number+=item_to_remove.quantity
    db.session.delete(item_to_remove)
    db.session.commit()
    flash('Your item has been removed from your cart!', 'success')
    return redirect(url_for('cart'))
@app.route("/checkout")
@login_required
def checkout():

    item = Cart.query.filter_by(buyer=current_user).all()
    for i in item:
        db.session.delete(i)
        db.session.commit()
    flash('you have checkout !', 'success')
    return redirect(url_for('cart'))


