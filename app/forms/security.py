from flask_wtf import FlaskForm
from wtforms import FileField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, EqualTo, Length

class ProtectPDFForm(FlaskForm):
    file = FileField('Select PDF File', validators=[DataRequired()])
    user_password = PasswordField('User Password', validators=[Length(min=1, max=32)])
    owner_password = PasswordField('Owner Password', validators=[Length(min=1, max=32)])
    confirm_password = PasswordField('Confirm User Password', 
                                   validators=[EqualTo('user_password', message='Passwords must match')])
    
    # Permission checkboxes
    allow_print = BooleanField('Allow Printing', default=True)
    allow_modify = BooleanField('Allow Modification', default=False)
    allow_copy = BooleanField('Allow Copying', default=True)
    allow_annotate = BooleanField('Allow Annotations', default=True)
    allow_forms = BooleanField('Allow Form Filling', default=True)
    allow_accessibility = BooleanField('Allow Accessibility', default=True)
    allow_assemble = BooleanField('Allow Document Assembly', default=False)
    allow_print_hq = BooleanField('Allow High Quality Printing', default=True)
    
    submit = SubmitField('Protect PDF')