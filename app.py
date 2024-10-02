from flask import Flask, render_template, redirect, flash, url_for , session,request
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from flask_migrate import Migrate
from wtforms import StringField, TextAreaField, SubmitField  , FloatField
from flask_wtf.file import FileField , FileRequired , FileAllowed , MultipleFileField 
from wtforms.validators import DataRequired, Email, Length
import os
from werkzeug.utils import secure_filename


app = Flask(__name__)
app.secret_key = "any-string-you-want-just-keep-it-secret"
UPLOAD_FOLDER='static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///e-commerce.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)  # Ensure name is unique
    price = db.Column(db.Float, nullable=False)
    gender = db.Column(db.String(10), nullable=True)
    image_filename = db.Column(db.String(250),nullable=True)

    def __repr__(self):
        return f'<Product {self.name}>'
    
class ProductForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    price = FloatField('Price', validators=[DataRequired()])  
    images = MultipleFileField('Product Images', validators=[FileAllowed(['jpg', 'png', 'jpeg'], 'Images only!')])
    gender = StringField('Gender', validators=[DataRequired()])
    submit = SubmitField('Submit')


class ContactForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Phone Number', validators=[DataRequired(), Length(max=15)])  
    comment = TextAreaField('Comment', validators=[DataRequired(), Length(max=500)])
    submit = SubmitField('Submit')
    
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/add_product', methods=['POST', 'GET'])
def add_product():
    form = ProductForm()
    if form.validate_on_submit():
        existing_product = Product.query.filter_by(name=form.name.data).first()
        if existing_product:
            flash("A product with this name already exists. Please choose a different name.")
            return redirect(url_for('add_product'))

      
        files = request.files.getlist('images')  
        image_filenames = []

        for file in files:
            if file and file.filename:  
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                image_filenames.append(filename)

        if image_filenames:
            image_filenames_str = ','.join(image_filenames)

            new_product = Product(
                name=form.name.data,
                price=form.price.data,
                image_filename=image_filenames_str,
                gender=form.gender.data
                
            )
            db.session.add(new_product)
            db.session.commit()
            flash("New product added to the database.")
            return redirect(url_for('home'))

    return render_template('add_product.html', form=form)



@app.route('/add_to_cart/<int:product_id>',methods =['POST'])
def add_to_cart(product_id):
    product = Product.query.get(product_id)
    if product :
        if 'cart' not in session:
            session['cart'] = {}
        if str(product.id) in session['cart']:
            session['cart'][str(product.id)]['quantity'] += 1
        else:
            session['cart'][str(product.id)] = {
                'name': product.name,
                'price' : product.price,
                'quantity' : 1,
                'product_id': product.id,
                'image_filename' : product.image_filename
            }
        session.modified = True
        flash(f'{product.name} added to cart!')
        return redirect(url_for('view_cart'))
    else:
        flash('product not found')
    return redirect(url_for('home'))

@app.route('/cart')
def view_cart():
    cart =session.get('cart' ,{})
    total = sum(item['price'] * item['quantity'] for item in cart.values())
    return render_template('cart.html' , cart=cart ,total =total)

@app.route('/remove_from_cart/<int:product_id>' ,methods =['POST'])
def remove_from_cart(product_id):
    if 'cart' in session and str(product_id) in session['cart']:
        del session['cart'][str(product_id)]
        session.modified =True
        flash('product remove from cart')
    else:
        flash('product not found in cart')
    return redirect(url_for('view_cart'))

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    cart = session.get('cart', {})
    total = sum(item['price'] * item['quantity'] for item in cart.values())
    if request.method == 'POST':
        
        
        session.pop('cart', None)
        return redirect(url_for('home')) 

    return render_template('checkout.html', cart=cart , total=total)


            
@app.route('/')
def home():
    products = Product.query.all()
    
    return render_template('home.html', products=products)

@app.route('/men')
def men_perfumes():
    products = Product.query.filter_by(gender='men').all()
    return render_template('men.html' , products = products)


@app.route('/women')
def women_perfumes():
    products = Product.query.filter_by(gender='women').all()
    return render_template('women.html' ,products = products )

@app.route('/view_all' , methods = ['GET'])
def view_all():
    products = Product.query.all()
   
    return render_template('view_all.html', products=products)

@app.route('/contact', methods=['GET'])
def contact():
    form = ContactForm()
    if form.validate_on_submit():
        flash('Your message has been sent!', 'success')
        return redirect(url_for('contact'))
    return render_template('contact.html', form=form)

@app.route('/update_cart/<int:product_id>' , methods = ['POST'])
def update_cart(product_id):
    action = request.form.get('action')
    if 'cart' in session and str(product_id) in session ['cart']:
        item = session['cart'][str(product_id)]
        if action == 'increase':
            item['quantity'] +=1
        elif action == 'decrease':
            if  item['quantity'] >1:
                item['quantity'] -=1
            else:
                flash('Quantity cannot be less than 1.')
    session.modified =True
    return redirect(url_for('view_cart'))
            

@app.route('/delete/<int:product_id>', methods=['POST'])
def delete(product_id):
    product= Product.query.get(product_id)
    if product:
        db.session.delete(product)
        db.session.commit()
        flash('product deleted successfully')
    else:
        flash('product not found')
    return redirect(url_for('home'))


@app.route('/testers')
def testers():
    return render_template('tester.html')

if __name__ == '__main__':
    app.run(debug=True)
