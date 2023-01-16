from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, upgrade

from model import db, seedData, Customer, Account, Transaction

 
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:Password123@localhost/Bank'
db.app = app
db.init_app(app)
migrate = Migrate(app,db)
 
 

@app.route("/")
def startpage():
    customer = Customer.query.all()
    return render_template('start.html', customer=customer)

@app.route("/<id>")
def customer(id):
    return render_template('customer.html', id=int(id), Account=Account.query.all())

if __name__  == "__main__":
    with app.app_context():
        upgrade()
    
        # seedData(db)
        app.run(debug=True)