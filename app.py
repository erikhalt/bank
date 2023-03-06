from flask import Flask, render_template, request, redirect, url_for, flash,jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, upgrade
import os
from model import db, seedData, Customer, Account, Transaction,user_datastore
from forms import *
from flask_security import roles_accepted, auth_required, logout_user, Security,SQLAlchemyUserDatastore
from datetime import datetime

# from wtforms import Form

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://bankroute:Salahf98@inlbank22.mysql.database.azure.com/bank'
db.app = app
db.init_app(app)
migrate = Migrate(app,db)
app.config['SECRET_KEY'] = os.urandom(32)

app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY", 'pf9Wkove4IKEAXvy-cQkeDPhv9Cb3Ag-wyJILbq_dFw')
app.config['SECURITY_PASSWORD_SALT'] = os.environ.get("SECURITY_PASSWORD_SALT", '146585145368132386173505678016728509634')
app.config["REMEMBER_COOKIE_SAMESITE"] = "strict"
app.config["SESSION_COOKIE_SAMESITE"] = "strict"
app.config['SECURITY_RECOVERABLE'] = True
app.security = Security(app, user_datastore)


SECURITY_FRESHNESS_GRACE_PERIOD = 1

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

    newTransaction = Transaction()
    newTransaction.Date = datetime.now()
    newTransaction.Amount = Amount
    newTransaction.AccountId = AccountId
    newTransaction.NewBalance = account.Balance - Amount
    newTransaction.Operation = "Withdrawl"
    newTransaction.Type = "Credit"
    
    db.session.add(newTransaction)
    db.session.commit()

def create_transaction_Transfer(Amount,To_AccountId,from_AccountId):
    to_account = Account.query.filter_by(Id=To_AccountId).first()

    newTransaction = Transaction()
    newTransaction.Date = datetime.now()
    newTransaction.Amount = Amount
    newTransaction.AccountId = To_AccountId
    newTransaction.NewBalance = to_account.Balance + Amount
    newTransaction.Operation = "Transfer"
    newTransaction.Type = "Debit"
    
    db.session.add(newTransaction)
    db.session.commit()

    from_account = Account.query.filter_by(Id=from_AccountId).first()

    newTransaction = Transaction()
    newTransaction.Date = datetime.now()
    newTransaction.Amount = Amount
    newTransaction.AccountId = from_AccountId
    newTransaction.NewBalance = from_account.Balance - Amount
    newTransaction.Operation = "Transfer"
    newTransaction.Type = "Credit"
    
    db.session.add(newTransaction)
    db.session.commit()

@app.route("/")
def startpage():
    customer = Customer.query.all()
    idsearchform = id_search()
    search = request.args.get('id_search', '')
    customerAmount = len(Customer.query.all())
    accountAmount = len(Account.query.all())
    if search.isnumeric():
        return redirect(url_for('customer', id=search))
    return render_template('home.html', customer=customer, idsearchform = idsearchform, customerAmount=customerAmount, accountAmount=accountAmount)

@app.route("/forgot", methods=['GET','POST'])
def forgotpassword():
    form = forgotpasswordform()
    if form.validate_on_submit():
        pass
    return render_template('forgot.html',form = form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect("/")

@app.route("/Customers")
@auth_required()
@roles_accepted("Admin","Staff")
def customers():
    page = int(request.args.get('page', 1))
    searchword = request.args.get('search','')
    sortColumn = request.args.get('sortColumn','Name')
    sortOrder = request.args.get('sortOrder','asc')
    
    list_of_customers = Customer.query
    list_of_customers = list_of_customers.filter(Customer.GivenName.like('%' + searchword + '%') | Customer.City.like('%' + searchword + '%'))
    
    
    search = request.args.get('id_search', '')
    if search.isnumeric():
        return redirect(url_for('customer', id=search))

    if sortColumn == "Name":
        if sortOrder == 'asc':
            list_of_customers = list_of_customers.order_by(Customer.GivenName.asc())
        else:
            list_of_customers = list_of_customers.order_by(Customer.GivenName.desc())

    
    elif sortColumn == "Surname":
        if sortOrder == 'asc':
            list_of_customers = list_of_customers.order_by(Customer.Surname.asc())
        else:
            list_of_customers = list_of_customers.order_by(Customer.Surname.desc())
    
    elif sortColumn == "Address":
        if sortOrder == 'asc':
            list_of_customers = list_of_customers.order_by(Customer.Streetaddress.asc())
        else:
            list_of_customers = list_of_customers.order_by(Customer.Streetaddress.desc())

    elif sortColumn == "City":
        if sortOrder == 'asc':
            list_of_customers = list_of_customers.order_by(Customer.City.asc())
        else:
            list_of_customers = list_of_customers.order_by(Customer.City.desc())    
    
    paginationObject = list_of_customers.paginate(page=page, per_page=20, error_out=False)
    #Har suttit 20per page enbart för att det blir jättefult med 50....
    idsearchform = id_search()
    return render_template('customers.html', 
                        customers = paginationObject.items,
                        has_next = paginationObject.has_next,
                        has_prev = paginationObject.has_prev,
                        pages = paginationObject.pages,
                        page = page,
                        search = searchword,
                        sortColumn = sortColumn,
                        sortOrder = sortOrder,
                        idsearchform = idsearchform)



@app.route("/<id>")
@auth_required()
@roles_accepted("Admin","Staff")
def customer(id):
    customer = Customer.query.filter_by(Id=id).first()
    accounts = Account.query.filter_by(CustomerId=id)
    totalbalance = 0
    for account in accounts:
        totalbalance += account.Balance

    search = request.args.get('id_search', '')
    if search.isnumeric():
        return redirect(url_for('customer', id=search))

    return render_template('customer.html', totalbalance=totalbalance, customer=customer, accounts=accounts)



@app.route("/<id>/Deposit<accountid>", methods=['GET','POST'])
@auth_required()
@roles_accepted("Admin","Staff")
def deposit(id,accountid):
    customer = Customer.query.filter_by(Id=id).first()
    accounts = Account.query.filter_by(Id=accountid).first()

    depositform = widthdrawldeposit()
    
    search = request.args.get('id_search', '')
    if search.isnumeric():
        return redirect(url_for('customer', id=search))

    if depositform.validate_on_submit():
        if depositform.amount.data < 0:
            depositform.amount.errors += "du kan ej sätta in ett negativt belopp"
        else:
            accounts.Balance += float(depositform.amount.data)
            db.session.commit()
            create_transaction_deposit(depositform.amount.data,float(accountid))

            return redirect(url_for('customer',id=id))
    return render_template('customerdeposit.html', customer=customer, account=accounts, form=depositform)

@app.route("/<id>/<accountid>transactions")
@auth_required()
@roles_accepted("Admin","Staff")
def transaction(id,accountid):
    accountTransaction = Transaction.query.filter_by(AccountId=accountid).order_by(Transaction.Date.desc())
    customer = Customer.query.filter_by(Id=id).first()

    search = request.args.get('id_search', '')
    if search.isnumeric():
        return redirect(url_for('customer', id=search))

    
    return render_template('transactions.html', accountTransaction=accountTransaction, customer=customer)


@app.route("/<id>/Withdrawl<accountid>", methods=['GET','POST'])
@auth_required()
@roles_accepted("Admin","Staff")
def withdrawl(id,accountid):

    search = request.args.get('id_search', '')
    if search.isnumeric():
        return redirect(url_for('customer', id=search))


    customer = Customer.query.filter_by(Id=id).first()
    accounts = Account.query.filter_by(Id=accountid).first()

    withdrawlform = widthdrawldeposit()
    
    if withdrawlform.validate_on_submit():
        if withdrawlform.amount.data < 0:
            withdrawlform.amount.errors += 'du kan ej ta ut ett negativt belopp'
        else:    
            if  accounts.Balance >= withdrawlform.amount.data:
                accounts.Balance -= float(withdrawlform.amount.data)
                db.session.commit()
                print(accounts.Balance)
                create_transaction_withdrawl(float(withdrawlform.amount.data),float(accountid))
                return redirect(url_for('customer', id=id))
            elif accounts.Balance < withdrawlform.amount.data:
                errormessage = 'Belopp för stort'
                withdrawlform.amount.errors += errormessage
    return render_template('customerwithdrawl.html', customer=customer, account=accounts, form=withdrawlform)



@app.route("/<id>/Transfer", methods=['GET','POST'])
@auth_required()
@roles_accepted("Admin","Staff")
def transfer(id):
    customer = Customer.query.filter_by(Id=id).first()
    accounts = Account.query.filter_by(CustomerId=id)

    listofaccounttypes = []

    search = request.args.get('id_search', '')
    if search.isnumeric():
        return redirect(url_for('customer', id=search))


    for element in accounts:
        stringinselectfield = f'{element.Id}:{element.AccountType}:{element.Balance}'
        listofaccounttypes.append(stringinselectfield)

    transfere_form = transfere()
    transfere_form.fromaccount.choices = listofaccounttypes
    transfere_form.recievingaccount.choices = listofaccounttypes

    if transfere_form.validate_on_submit():
        to_account_id = 0
        from_account_id = 0

        for element in accounts:
            fromaccountparts = transfere_form.fromaccount.data.split(':')
            if str(element.Id) == fromaccountparts[0]:
                from_account_id = element.Id

        for element in accounts:
            recievingaccountparts = transfere_form.recievingaccount.data.split(':')
            if str(element.Id) == recievingaccountparts[0]:
                to_account_id = element.Id

        from_account = Account.query.filter_by(Id=from_account_id).first()
        to_account = Account.query.filter_by(Id=to_account_id).first()
        if from_account_id == to_account_id:
            transfere_form.fromaccount.errors += 'Kan inte överföra till pengar mellan samma konto'
        elif transfere_form.fromamount.data < 0:
            transfere_form.fromamount.errors += 'Kan inte överföra ett negativt belopp'

        else:
            if from_account.Balance >= transfere_form.fromamount.data:
                from_account.Balance -= float(transfere_form.fromamount.data)
                to_account.Balance += float(transfere_form.fromamount.data)
                create_transaction_Transfer(transfere_form.fromamount.data,to_account_id,from_account_id)

                return redirect(url_for('customer',id=id))
            if from_account.Balance < transfere_form.fromamount.data:
                errormessage = 'Belopp för stort'
                transfere_form.fromamount.errors += errormessage

    return render_template('customertransfere.html', customer=customer, accounts=accounts, form = transfere_form)



@app.route('/api/<id>')
def customerAPI(id):
    customer = Customer.query.filter_by(Id=id).first()
    accounts = Account.query.filter_by(CustomerId=id)
    customerData = []
    customerAccountinfo = []
    for element in accounts:
        customerAccountinfo.append({"Type":element.AccountType,
                                    "Balance":element.Balance})
    
    customerinfo = {"Id":customer.Id,
                    "Name":customer.GivenName,
                    "Surname":customer.Surname,
                    "Address":customer.Streetaddress,
                    "City":customer.City,
                    "Zipcode":customer.Zipcode,
                    "Country":customer.Country,
                    "CountryCode":customer.CountryCode,
                    "Birthday":customer.Birthday,
                    "NationalId":customer.NationalId,
                    "TelephoneCountryCode":customer.TelephoneCountryCode,
                    "Telephone":customer.Telephone,
                    "Email":customer.EmailAddress,
                    }
    customerData.append(customerAccountinfo)
    customerData.append(customerinfo)
    return jsonify(customerData)


if __name__  == "__main__":
    with app.app_context():
        upgrade()
    
        seedData(app,db)
        app.run(debug=True)