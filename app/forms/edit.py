from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import SelectField, IntegerField, StringField, SubmitField
from wtforms.validators import DataRequired, NumberRange, Optional

class PageNumbersForm(FlaskForm):
    file = FileField('Select PDF', validators=[
        FileRequired(),
        FileAllowed(['pdf'], 'PDF files only!')
    ])
    position = SelectField('Position', choices=[
        ('bottom-right', 'Bottom Right'),
        ('bottom-left', 'Bottom Left'),
        ('bottom-center', 'Bottom Center'),
        ('top-right', 'Top Right'),
        ('top-left', 'Top Left'),
        ('top-center', 'Top Center')
    ])
    font = SelectField('Font', choices=[
        ('helv', 'Helvetica'),
        ('tiro', 'Times Roman'),
        ('cour', 'Courier'),
        ('times', 'Times New Roman')
    ])
    font_size = IntegerField('Font Size', validators=[
        DataRequired(),
        NumberRange(min=6, max=72)
    ], default=12)
    start_number = IntegerField('Start Number', validators=[
        DataRequired(),
        NumberRange(min=1)
    ], default=1)
    prefix = StringField('Prefix', validators=[Optional()])
    suffix = StringField('Suffix', validators=[Optional()])
    margin = IntegerField('Margin (points)', validators=[
        DataRequired(),
        NumberRange(min=1, max=100)
    ], default=36)
    pages = StringField('Pages (e.g., 1-5,8,11-13)', validators=[Optional()])
    submit = SubmitField('Add Page Numbers')