from flask_wtf import FlaskForm
from wtforms import FileField, SelectField, SubmitField
from wtforms.validators import DataRequired

class ImageToPdfForm(FlaskForm):
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