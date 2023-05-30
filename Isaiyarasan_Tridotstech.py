from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///inventory.db'
db = SQLAlchemy(app)

# Database Models
class Product(db.Model):
    product_id = db.Column(db.String(50), primary_key=True)

class Location(db.Model):
    location_id = db.Column(db.String(50), primary_key=True)

class ProductMovement(db.Model):
    movement_id = db.Column(db.String(50), primary_key=True)
    timestamp = db.Column(db.DateTime)
    from_location = db.Column(db.String(50), db.ForeignKey('location.location_id'))
    to_location = db.Column(db.String(50), db.ForeignKey('location.location_id'))
    product_id = db.Column(db.String(50), db.ForeignKey('product.product_id'))
    qty = db.Column(db.Integer)

# Routes
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/products', methods=['GET', 'POST'])
def products():
    if request.method == 'POST':
        product_id = request.form['product_id']
        product = Product(product_id=product_id)
        db.session.add(product)
        db.session.commit()
        return redirect(url_for('products'))
    else:
        products = Product.query.all()
        return render_template('products.html', products=products)

@app.route('/locations', methods=['GET', 'POST'])
def locations():
    if request.method == 'POST':
        location_id = request.form['location_id']
        location = Location(location_id=location_id)
        db.session.add(location)
        db.session.commit()
        return redirect(url_for('locations'))
    else:
        locations = Location.query.all()
        return render_template('locations.html', locations=locations)

@app.route('/movements', methods=['GET', 'POST'])
def movements():
    if request.method == 'POST':
        movement_id = request.form['movement_id']
        timestamp = request.form['timestamp']
        from_location = request.form['from_location']
        to_location = request.form['to_location']
        product_id = request.form['product_id']
        qty = int(request.form['qty'])
        movement = ProductMovement(movement_id=movement_id, timestamp=timestamp,
                                   from_location=from_location, to_location=to_location,
                                   product_id=product_id, qty=qty)
        db.session.add(movement)
        db.session.commit()
        return redirect(url_for('movements'))
    else:
        movements = ProductMovement.query.all()
        return render_template('movements.html', movements=movements)

@app.route('/report')
def report():
    locations = Location.query.all()
    report_data = []
    for location in locations:
        product_movements = ProductMovement.query.filter(
            (ProductMovement.from_location == location.location_id) |
            (ProductMovement.to_location == location.location_id)
        ).all()
        product_qty = {}
        for movement in product_movements:
            product_id = movement.product_id
            qty = movement.qty
            if product_id in product_qty:
                product_qty[product_id] += qty
            else:
                product_qty[product_id] = qty
        for product_id, qty in product_qty.items():
            report_data.append({
                'product': product_id,
                'warehouse': location.location_id,
                'qty': qty
            })
    return render_template('report.html', report_data=report_data)

if __name__ == '__main__':
    app.run(debug=True)
