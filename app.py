from flask import Flask, jsonify, request, Blueprint
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from marshmallow import fields, validate
from marshmallow import ValidationError
import mysql.connector
from mysql.connector import Error

# api = Blueprint('api', __name__, url_prefix='api')

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:Darknight1234@localhost/e_commerce_db'
db = SQLAlchemy(app)
ma = Marshmallow(app)

@app.route('/')
def home():
    return "Welcome to the Flask Music Festivallllll"

class CustomerSchema(ma.Schema):
    name = fields.String(required=True) 
    email = fields.String(required=True)
    phone = fields.String(required=True)
    
    class Meta:
        fields = ("name", "email", "phone", "id")

class ProductSchema(ma.Schema):
    name = fields.String(required=True, validate=validate.Length(min=1))
    price = fields.Float(required=True, validate=validate.Range(min=0))
    
    class Meta:
        fields = ("name", "price", "id")
        
class CustomerAccountSchema(ma.Schema):
    username = fields.String(required=True, validate=validate.Length(min=1))
    password = fields.String(required=True)
    customer = fields.Nested(CustomerSchema)
    
    class Meta:
        fields = ("username", "password", "customer")

class OrderSchema(ma.Schema):
    date = fields.Date(required=True)
    customer_id = fields.Integer(required=True)

    class Meta:
        fields = ("date", "customer_id")
        
class OrderDetailsSchema(ma.Schema):
    id = fields.Integer()
    date = fields.Date()
    products = fields.Nested('ProductSchema', many=True)

order_details_schema = OrderDetailsSchema()

order_schema = OrderSchema()

product_schema = ProductSchema()
products_schema = ProductSchema(many=True)
        
customer_schema = CustomerSchema()
customers_schema = CustomerSchema(many=True)

customer_account_schema = CustomerAccountSchema()

# def get_db_connection():
#     db_name = "e_commerce_db"
#     user = "root "
#     password = "Darknight1234"
#     host = "127.0.0.1"

#     try:
#         conn = mysql.connector.connect(
#             database = db_name,
#             user = user,
#             password = password,
#             host = host
#         )
        
#         # if conn.is_connected():
#         print("Connected to mysql Yayyy")
#         return conn
    
#     except Error as e:
#         print(f"Error: {e}")
#         return None
        
class Customer(db.Model):
    __tablename__ = 'Customers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(320))
    phone = db.Column(db.String(15))
    orders = db.relationship('Order', backref= 'customer')
    
class Order(db.Model):
    __tablename__ = 'Orders'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('Customers.id'))
    
#one to one
class CustomerAccount(db.Model):
    __tablename__ = 'Customer_Accounts'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('Customers.id'))
    customer = db.relationship('Customer', backref = 'customer_account', uselist=False)
    
#many to many

order_product = db.Table('Order_Product', 
            db.Column('order_id', db.Integer, db.ForeignKey('Orders.id'), primary_key = True),
            db.Column('product_id', db.Integer, db.ForeignKey('Products.id'), primary_key=True)
)


class Product(db.Model):
    __tablename__ = 'Products'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    price = db.Column(db.Float, nullable=False)
    orders = db.relationship('Order', secondary=order_product, backref=db.backref('products'))


@app.route('/customers', methods=['GET'])
# def get_customers():
#     try:
#         conn = get_db_connection()
#         if conn is None:
#             return jsonify({"error": "Database connection failed"}), 500
#         cursor = conn.cursor(dictionary=True)
        
#         query = "SELECT * FROM Customers"
        
#         cursor.execute(query)
        
#         customers = cursor.fetchall()
        
#         return customers_schema.jsonify(customers)
#     except Error as e:
#         print(f"Error: {e}")
#         return jsonify({"error": "Interval Server Error"}), 500
    
#     finally:
#         if conn and conn.is_connected():
#             cursor.close()
#             conn.close()
def get_customers():
    customers = Customer.query.all()
    return customers_schema.jsonify(customers)

@app.route('/customers', methods=['POST'])
def add_customer():
    try:
        customer_data = customer_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    new_customer = Customer(name=customer_data['name'], email=customer_data['email'], phone=customer_data['phone'])
    db.session.add(new_customer)
    db.session.commit()
    return jsonify({"message": "New customer added successfully"}), 201

@app.route('/customers/<int:id>', methods=['PUT']) 
def update_customer(id):
    customer = Customer.query.get_or_404(id)
    try:
        customer_data = customer_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    customer.name = customer_data['name']
    customer.email = customer_data['email']
    customer.phone = customer_data['phone']
    db.session.commit()
    return jsonify({"message": "Customer details updated successfully"}), 200

@app.route('/customers/<int:id>', methods=['DELETE']) 
def delete_customer(id):
    customer = Customer.query.get_or_404(id)
    db.session.delete(customer)
    db.session.commit()
    return jsonify({"message": "Customer removed successfully"}), 200

@app.route('/products', methods=['POST'])
def add_product():
    try:
        product_data = product_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400 
    
    new_product = Product(name=product_data['name'], price=product_data['price'])
    db.session.add(new_product)
    db.session.commit()
    return jsonify({"message": "Product added successfully"}), 201

@app.route('/products', methods=['GET'])
def get_products():
    products = Product.query.all()
    return products_schema.jsonify(products)

@app.route('/products/<int:id>', methods=['GET'])
def get_products_by_id(id):
    
    product = Product.query.get_or_404(id)
    if product:
        return product_schema.jsonify(product)
    else:
        return jsonify({"message": "Customer not found"}), 404


@app.route('/products/<int:id>', methods=['PUT'])
def update_product(id):
    product = Product.query.get_or_404(id)
    try:
        product_data = product_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    product.name = product_data['name']
    product.price = product_data['price']
    db.session.commit()
    return jsonify({"message": "Product updated successfully"}), 200

@app.route('/products/<int:id>', methods=['DELETE'])
def delete_product(id):
    product = Product.query.get_or_404(id)
    db.session.delete(product)
    db.session.commit()
    return jsonify({"message": "Product deleted successfully"}), 200




@app.route('/customers/by-email', methods=['GET'])
def query_customer_by_email():
    email = request.args.get('email')
    customer = Customer.query.filter_by(email=email).first()
    if customer:
        return customer_schema.jsonify(customer)
    else:
        return jsonify({"message": "Customer not found"}), 404

@app.route('/customers/<int:id>', methods=['GET'])
def query_customer_by_id(id):
    customer = Customer.query.get_or_404(id)
    if customer:
        return customer_schema.jsonify(customer)
    else:
        return jsonify({"message": "Customer not found"}), 404
  
    
@app.route('/products/by-name', methods=['GET'])
def query_customer_by_name():
    name = request.args.get('name')
    product = Product.query.filter(Product.name == name).first()
    if product:
        return product_schema.jsonify(product)
    else:
        return jsonify({"message": "Product not found"}), 404


@app.route('/customer-accounts', methods=['POST'])
def add_customer_account():
    try:
        
        customer_account_data = customer_account_schema.load(request.json)
        
        new_customer_account = CustomerAccount(username=customer_account_data['username'], password=customer_account_data['password'])
        db.session.add(new_customer_account)
        db.session.commit()
        
        return jsonify({"message": "New customer account created successfully"}), 201
    
    except ValidationError as err:
        return jsonify(err.messages), 400
    
@app.route('/customer-accounts/<int:id>', methods=['GET'])
def get_customer_account(id):
    customer_account = CustomerAccount.query.get_or_404(id)
    return customer_account_schema.jsonify(customer_account)

@app.route('/customer-accounts/<int:id>', methods=['DELETE'])
def delete_customer_account(id):
    customer_account = CustomerAccount.query.get_or_404(id)
    db.session.delete(customer_account)
    db.session.commit()
    return jsonify({"message": "Customer account deleted successfully"}), 200

@app.route('/orders', methods=['POST'])
def create_order():
    try:
       
        order_data = order_schema.load(request.json)

        new_order = Order(date=order_data['date'], customer_id=order_data['customer_id'])
        db.session.add(new_order)
        db.session.commit()

        return jsonify({"message": "New order placed successfully"}), 201

    except ValidationError as err:
        return jsonify(err.messages), 400
    
@app.route('/orders/<int:id>', methods=['GET'])
    
def get_order_details(id):
    
    order = Order.query.get_or_404(id)
    if order:
        
        order_details = {
            'order_id': order.id,
            'date': order.date,
            'products': order.products
        }
        return order_details_schema.jsonify(order_details)
    
    else:
        return jsonify({"message": "Order not found"}), 404

 
with app.app_context():
    db.create_all()
    
if __name__ == '__main__':
    app.run(debug=True)
    
    
    
