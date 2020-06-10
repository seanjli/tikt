from flask_wtf import Form
from wtforms import StringField, IntegerField, SelectField
from wtforms.validators import DataRequired, Length, NumberRange

class TestForm(Form):
    name = StringField('Name of test', 
            validators=[DataRequired()]
            )
    prob_num = IntegerField('Number of problems',
            validators=[DataRequired(), NumberRange(min=1, max=20, message="Please input an integer from 1 to 20.")]
            )
