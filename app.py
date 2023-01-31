from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, upgrade
import os
from model import db, seedData, Customer, Account, Transaction
from forms import *
from flask_security import roles_accepted, auth_required, logout_user


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:Password123@localhost/Bank'
db.app = app
db.init_app(app)
migrate = Migrate(app,db)
app.config['SECRET_KEY'] = os.urandom(32)

app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY", 'pf9Wkove4IKEAXvy-cQkeDPhv9Cb3Ag-wyJILbq_dFw')
app.config['SECURITY_PASSWORD_SALT'] = os.environ.get("SECURITY_PASSWORD_SALT", '146585145368132386173505678016728509634')
app.config["REMEMBER_COOKIE_SAMESITE"] = "strict"
app.config["SESSION_COOKIE_SAMESITE"] = "strict"



@app.route("/")
def startpage():
    customer = Customer.query.all()
    return render_template('basetemplate.html', customer=customer)



@app.route("/Customers")
@auth_required()
@roles_accepted("Admin","Staff")
def custeomers():
    customers = Customer.query
    page = int(request.args.get('page', 1))
    paginationObject = customers.paginate(page=page, per_page=20, error_out=False)

    return render_template('customers.html', 
                        customers = paginationObject.items,
                        has_next = paginationObject.has_next,
                        has_prev = paginationObject.has_prev,
                        pages = paginationObject.pages,
                        page = page,)



@app.route("/<id>")
def customer(id):
    customer = Customer.query.filter_by(Id=id).first()
    accounts = Account.query.filter_by(CustomerId=id)

    return render_template('customer.html', customer=customer, accounts=accounts)



@app.route("/<id>/Deposit<accountid>")
def deposit(id,accountid):
    customer = Customer.query.filter_by(Id=id).first()
    account = Account.query.filter_by(Id=accountid).first()

    return render_template('customerdeposit.html', customer=customer, account=account)



@app.route("/<id>/Withdrawl<accountid>", methods=['GET','POST'])
def withdrawl(id,accountid):
    
    customer = Customer.query.filter_by(Id=id).first()
    accounts = Account.query.filter_by(Id=accountid).first()
    form = widthdrawldeposit()

    if form.validate_on_submit():
        if  accounts.Balance >= form.amount.data:
            accounts.Balance -= form.amount.data
            db.session.commit()
            # return redirect(url_for('customer', id=customer.Id))
            return redirect('/Customer')
    
    return render_template('customerdeposit.html', customer=customer, account=accounts, form=form)



@app.route("/<id>/Transfer")
def transfer(id):
    customer = Customer.query.filter_by(Id=id).first()
    accounts = Account.query.filter_by(CustomerId=id)

    return render_template('customer.html', customer=customer, accounts=accounts)











# @app.route("/newcustomer", methods=['GET','POST'])
# def newcustomer():
#         form = newcustomerForm()

#         if form.validate_on_submit():
        
#             #spara i databas
#             customer = Customer()
#             customer.GivenName = form.city.data
#             customer.City = form.city.data
#             customer.CountryCode = form.countryCode.data
#             db.session.add(customer)
#             db.session.commit()
#             return redirect("/Customers" )
#         return render_template('newcustomer.html', form=form)

if __name__  == "__main__":
    with app.app_context():
        upgrade()
    
        seedData(app,db)
        app.run(debug=True)