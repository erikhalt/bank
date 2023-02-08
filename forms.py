from flask_wtf import FlaskForm
from wtforms import Form, BooleanField, StringField, PasswordField, validators, ValidationError
from wtforms.fields import IntegerField, TelField, EmailField,RadioField, SelectField, SelectMultipleField

def emailVaild(form, field):
    if not field.data.endswith('.se'):
        raise ValidationError('Invalid Email!')

def toHighAmount():
    raise ValidationError('Insufficient funds')


class newcustomerForm(FlaskForm):
    name = StringField('name', validators=[validators.DataRequired(),emailVaild])
    city = StringField('city', validators=[validators.DataRequired()])
    age = IntegerField('age')
    countryCode = SelectField('countryCode', choices=[('SE','+46'),('NO','+41'),('FI','+42')])

class widthdrawldeposit(FlaskForm):
    amount = IntegerField('amount', validators=[validators.DataRequired()])


def choicestransfere(list):
    return list

class transfere(FlaskForm):
    fromaccount = SelectField('fromaccount',validators=[validators.DataRequired()])
    recievingaccount = SelectField('recievingaccount',validators=[validators.DataRequired()])
    fromamount = IntegerField('fromamount', validators=[validators.DataRequired()])
