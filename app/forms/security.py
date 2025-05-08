from flask_wtf import FlaskForm
from wtforms import PasswordField, SubmitField

class ProtectPDFForm(FlaskForm):
    class Meta:
        csrf = False
    
    # Your form fields here...