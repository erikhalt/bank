from flask_wtf import FlaskForm
from wtforms import Form, BooleanField, StringField, PasswordField, validators, ValidationError
from wtforms.fields import IntegerField, TelField, EmailField,RadioField, SelectField, SelectMultipleField

def emailVaild(form, field):
    if not field.data.endswith('.se'):
        raise ValidationError('Invalid Email!')

def toHighAmount():
    raise ValidationError('Insufficient funds')

def onlyNumber(form, field):
    if not form.data.isnumeric():
        raise ValidationError('Kan enbart söka på siffror')


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

class id_search(FlaskForm):
    id_search = IntegerField('id_search', validators=[validators.DataRequired(),onlyNumber])

class forgotpasswordform(FlaskForm):
    email = EmailField('email',validators=[emailVaild,validators.DataRequired(),validators.Email()])
    newpassword = PasswordField('newpassword',validators=[validators.DataRequired(),validators.Length(min=4,max=20)])