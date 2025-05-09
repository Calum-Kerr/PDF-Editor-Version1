from flask_wtf import FlaskForm
from wtforms import PasswordField, SubmitField

class ProtectPDFForm(FlaskForm):
    class Meta:
        csrf = False
    
    user_password = PasswordField('User Password')
    owner_password = PasswordField('Owner Password')
    submit = SubmitField('Protect PDF')

class ComparePDFForm:
    """Simple form class without CSRF protection"""
    pass
