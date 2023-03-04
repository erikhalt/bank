import unittest
from model import Customer,Account,db
from app import app
import barnum
from forms import *
from datetime import datetime

class TransactionsTest(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(TransactionsTest,self).__init__(*args, **kwargs)
        self.ctx = app.app_context()
        self.ctx.push()
        self.client = app.test_client()
        app.config["SERVER_NAME"] = "stefan.se"
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['WTF_CSRF_METHODS'] = []  # This is the magic
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
        app.config['SECURITY_FRESHNESS_GRACE_PERIOD'] = 123454
        db.init_app(app)
        db.create_all()

        
        customer = Customer()
        customer.Id = 1
        customer.GivenName, customer.Surname = barnum.create_name()
        customer.Streetaddress = barnum.create_street()
        customer.Zipcode, customer.City, _  = barnum.create_city_state_zip()
        customer.Country = "USA"
        customer.CountryCode = "US"
        customer.Birthday = barnum.create_birthday()
        n = barnum.create_cc_number()
        customer.NationalId = customer.Birthday.strftime("%Y%m%d-") + n[1][0][0:4]
        customer.TelephoneCountryCode = 55
        customer.Telephone = barnum.create_phone()
        customer.EmailAddress = barnum.create_email().lower()
        
        account = Account()
        account.Id = 1
        account.AccountType = 'Test'
        account.Created = datetime.now()
        account.CustomerId = 1
        account.Balance = 200
        account2 = Account()
        account2.Id = 2
        account2.AccountType = 'Test2'
        account2.Created = datetime.now()
        account2.CustomerId = 1
        account2.Balance = 200

        
        db.session.add(customer)
        db.session.add(account)
        db.session.add(account2)

    def test_that_withdraw_cant_be_more_than_balance(self):
        test_client = app.test_client()
        with test_client:
            url = "/1/Withdrawl1"
            response = test_client.post(url, data={"amount":"300"})
            s = response.data.decode("utf-8").replace(', ','') 
            ok = 'Belopp för stort' in s
            self.assertTrue(ok)                

    def test_that_you_cant_transfere_more_than_balance(self):
        test_client = app.test_client()
        with test_client:
            url = "/1/Transfer"
            response = test_client.post(url, data={"fromamount":"300","fromaccount":"1:Test:200","recievingaccount":"2:Test2:200"})
            s = response.data.decode("utf-8").replace(', ','') 
            ok = 'Belopp för stort' in s
            self.assertTrue(ok)                

    def test_that_you_cant_deposit_negative_amount(self):
        test_client = app.test_client()
        with test_client:
            url = "/1/Deposit1"
            response = test_client.post(url, data={"amount":"-100"})
            s = response.data.decode("utf-8").replace(', ','') 
            ok = 'du kan ej sätta in ett negativt belopp' in s
            self.assertTrue(ok)                

    def test_that_you_cant_withdrawl_negative_amount(self):
        test_client = app.test_client()
        with test_client:
            url = "/1/Withdrawl1"
            response = test_client.post(url, data={"amount":"-100"})
            s = response.data.decode("utf-8").replace(', ','') 
            ok = 'du kan ej ta ut ett negativt belopp' in s
            self.assertTrue(ok)                
            
if __name__ == "__main__":
    unittest.main()
