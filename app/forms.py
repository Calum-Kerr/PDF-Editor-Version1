from flask_wtf import FlaskForm
from wtforms import FileField, SelectField, IntegerField, StringField, SubmitField
from wtforms.validators import DataRequired, NumberRange, Optional

class PageNumbersForm(FlaskForm):
    file = FileField('PDF File', validators=[DataRequired()])
    
    position = SelectField('Position', choices=[
        ('top-left', 'Top Left'),
        ('top-center', 'Top Center'),
        ('top-right', 'Top Right'),
        ('bottom-left', 'Bottom Left'),
        ('bottom-center', 'Bottom Center'),
        ('bottom-right', 'Bottom Right')
    ])
    
    font = SelectField('Font', choices=[
        ('helv', 'Helvetica'),
        ('tiro', 'Times Roman'),
        ('cour', 'Courier'),
        ('times', 'Times New Roman')
    ])
    
    font_size = IntegerField('Font Size', 
        validators=[NumberRange(min=6, max=72)],
        default=10
    )
    
    start_number = IntegerField('Start Number',
        validators=[NumberRange(min=1)],
        default=1
    )
    
    prefix = StringField('Prefix', validators=[Optional()])
    suffix = StringField('Suffix', validators=[Optional()])
    
    margin = IntegerField('Margin',
        validators=[NumberRange(min=0, max=144)],
        default=36
    )
    
    pages = StringField('Pages to Number',
        validators=[Optional()],
        default=''  # Changed from 'all' to empty string
    )
    
    submit = SubmitField('Add Page Numbers')
