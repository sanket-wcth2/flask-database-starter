"""
Part 6: Homework - Product Inventory App
========================================
See Instruction.md for full requirements and hints.

How to Run:
1. Make sure venv is activated
2. Install: pip install flask flask-sqlalchemy
3. Run: python app.py
4. Open browser: http://localhost:5000
"""

from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = "inventory_secret_key"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///part6-inventory.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


# =============================================================================
# STEP 1: Product Model (Already done for you)
# =============================================================================

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, default=0)
    price = db.Column(db.Float, nullable=False)


# =============================================================================
# STEP 2: Create your routes here
# =============================================================================

# Route 1: Home page - display all products
# Your code here...
@app.route('/')
def index():
    products = Product.query.all()

    total_value = 0
    for product in products:
        total_value += product.quantity * product.price

    return render_template(
        'index.html',
        products=products,
        total_value=total_value
    )



# Route 2: Add product page - form to add new product
# Your code here...
@app.route('/add', methods=['GET', 'POST'])
def add_product():
    if request.method == 'POST':
        name = request.form['name']
        quantity = int(request.form['quantity'])
        price = float(request.form['price'])
        product=Product(name=name, quantity=quantity, price=price)
        db.session.add(product)
        db.session.commit()
        flash(" Product added successfully!", "success")
        return redirect(url_for('index'))
    return render_template('add.html')

#route 3: Edit product page - form to edit existing product

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_product(id):
    product = Product.query.get_or_404(id)

    if request.method == 'POST':
        product.name = request.form['name']
        product.quantity = int(request.form['quantity'])
        product.price = float(request.form['price'])

        db.session.commit()
        flash("Product updated successfully!", "success")
        return redirect(url_for('index'))

    return render_template('edit.html', product=product)


# Route 4: Delete product
# Your code here...
@app.route('/delete/<int:id>')
def delete_product(id):
    product = Product.query.get_or_404(id)
    db.session.delete(product)
    db.session.commit()
    flash("Product deleted successfully!", "success")
    return redirect(url_for('index'))

# =============================================================================
# STEP 3: Initialize database (Already done for you)
# =============================================================================

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
