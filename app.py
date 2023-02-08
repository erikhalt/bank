from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, upgrade
import os
from model import db, seedData, Customer, Account, Transaction
from forms import *
from flask_security import roles_accepted, auth_required, logout_user
from datetime import datetime

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


def create_transaction_deposit(Amount,AccountId):
    account = Account.query.filter_by(Id=AccountId).first()

    newTransaction = Transaction()
    newTransaction.Date = datetime.now()
    newTransaction.Amount = Amount
    newTransaction.AccountId = AccountId
    newTransaction.NewBalance = account.Balance + Amount
    newTransaction.Operation = "Deposit"
    newTransaction.Type = "Debit"
    db.session.add(newTransaction)
    db.session.commit()

def create_transaction_withdrawl(Amount,AccountId):
    account = Account.query.filter_by(Id=AccountId).first()

    newTransaction = Transaction
    newTransaction.Date = datetime.now()
    newTransaction.Amount = Amount
    newTransaction.AccountId = AccountId
    newTransaction.NewBalance = account.Balance - Amount
    newTransaction.Operation = "Withdrawl"
    newTransaction.Type = "Credit"
    
    # db.session.add(newTransaction)
    db.session.commit()

def create_transaction_Transfer(Amount,To_AccountId,from_AccountId):
    to_account = Account.query.filter_by(Id=To_AccountId).first()

    newTransaction = Transaction
    newTransaction.Date = datetime.now()
    newTransaction.Amount = Amount
    newTransaction.AccountId = To_AccountId
    newTransaction.NewBalance = to_account.Balance + Amount
    newTransaction.Operation = "Transfer"
    newTransaction.Type = "Debit"
    
    # db.session.add(newTransaction)
    db.session.commit()

    from_account = Account.query.filter_by(Id=from_AccountId).first()

    newTransaction = Transaction
    newTransaction.Date = datetime.now()
    newTransaction.Amount = Amount
    newTransaction.AccountId = from_AccountId
    newTransaction.NewBalance = from_account.Balance - Amount
    newTransaction.Operation = "Transfer"
    newTransaction.Type = "Credit"
    
    # db.session.add(newTransaction)
    db.session.commit()

@app.route("/")
def startpage():
    customer = Customer.query.all()
    return render_template('basetemplate.html', customer=customer)

@app.route("/logout")
def logout():
    logout_user()
    return redirect("/")

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
@auth_required()
@roles_accepted("Admin","Staff")
def customer(id):
    customer = Customer.query.filter_by(Id=id).first()
    accounts = Account.query.filter_by(CustomerId=id)
    totalbalance = 0
    for account in accounts:
        totalbalance += account.Balance

    return render_template('customer.html', totalbalance=totalbalance, customer=customer, accounts=accounts)



@app.route("/<id>/Deposit<accountid>", methods=['GET','POST'])
@auth_required()
@roles_accepted("Admin","Staff")
def deposit(id,accountid):
    customer = Customer.query.filter_by(Id=id).first()
    accounts = Account.query.filter_by(Id=accountid).first()

    depositform = widthdrawldeposit()
    
    if depositform.validate_on_submit():
        accounts.Balance += depositform.amount.data
        db.session.commit()
        create_transaction_deposit(depositform.amount.data,int(accountid))

        return redirect(url_for('customer',id=id))
    return render_template('customerdeposit.html', customer=customer, account=accounts, form=depositform)



@app.route("/<id>/Withdrawl<accountid>", methods=['GET','POST'])
@auth_required()
@roles_accepted("Admin","Staff")
def withdrawl(id,accountid):
    
    customer = Customer.query.filter_by(Id=id).first()
    accounts = Account.query.filter_by(Id=accountid).first()

    withdrawlform = widthdrawldeposit()
    
    if withdrawlform.validate_on_submit():
        if  accounts.Balance >= withdrawlform.amount.data:
            accounts.Balance -= withdrawlform.amount.data
            db.session.commit()
            create_transaction_withdrawl(withdrawlform.amount.data,int(accountid))
        return redirect(url_for('customer', id=id))
    return render_template('customerwithdrawl.html', customer=customer, account=accounts, form=withdrawlform)



@app.route("/<id>/Transfer", methods=['GET','POST'])
@auth_required()
@roles_accepted("Admin","Staff")
def transfer(id):
    customer = Customer.query.filter_by(Id=id).first()
    accounts = Account.query.filter_by(CustomerId=id)

    listofaccounttypes = []

    for element in accounts:
        stringinselectfield = f'{element.Id}:{element.AccountType}:{element.Balance}'
        listofaccounttypes.append(stringinselectfield)

    form = transfere()
    form.fromaccount.choices = listofaccounttypes
    form.recievingaccount.choices = listofaccounttypes

    if form.validate_on_submit():
        to_account_id = 0
        from_account_id = 0

        for element in accounts:
            fromaccountparts = form.fromaccount.data.split(':')
            if element.Id == fromaccountparts[0]:
                from_account_id = element.Id

        for element in accounts:
            recievingaccountparts = form.recievingaccount.data.split(':')
            if element.Id == recievingaccountparts[0]:
                to_account_id = element.Id

        from_account = Account.query.filter_by(Id=from_account_id).first()
        to_account = Account.query.filter_by(Id=to_account_id).first()

        if from_account.Balance >= form.fromamount.data:
            from_account.Balance -= form.fromamount.data
            to_account.Balance += form.fromamount.data
            create_transaction_Transfer(form.fromamount.data,to_account_id,from_account_id)

            return redirect(url_for('customer',id=id))
        else:
            form.fromamount.errors += "Belopp för stort"

    return render_template('customertransfere.html', customer=customer, accounts=accounts, form = form)






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