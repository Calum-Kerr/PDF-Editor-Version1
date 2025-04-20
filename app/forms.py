from flask_wtf import FlaskForm
from wtforms import FileField, SelectField, SubmitField, PasswordField
from wtforms.validators import DataRequired, EqualTo, Length

class ImageToPdfForm(FlaskForm):
    class Meta:
        csrf = False  # Disable CSRF protection for this form
        
    file = FileField('Select Image File', validators=[DataRequired()])
    page_size = SelectField('Page Size', choices=[
        ('a4', 'A4'),
        ('letter', 'Letter'),
        ('legal', 'Legal'),
        ('a3', 'A3'),
        ('a5', 'A5'),
        ('original', 'Original Image Size')
    ])
    orientation = SelectField('Orientation', choices=[
        ('portrait', 'Portrait'),
        ('landscape', 'Landscape')
    ])
    submit = SubmitField('Convert to PDF')

# Update ProtectPDFForm similarly
class ProtectPDFForm(FlaskForm):
    class Meta:
        csrf = False  # Disable CSRF protection for this form
        
    file = FileField('Select PDF File', validators=[DataRequired()])
    user_password = PasswordField('User Password', validators=[Length(min=1, max=32)])
    owner_password = PasswordField('Owner Password', validators=[Length(min=1, max=32)])
    confirm_password = PasswordField('Confirm User Password', 
                                   validators=[EqualTo('user_password', message='Passwords must match')])
