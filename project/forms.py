from flask_wtf import Form
from wtforms import StringField, IntegerField, SelectField, \
        PasswordField, SelectMultipleField
from wtforms.validators import DataRequired, Length, NumberRange,\
        EqualTo, Email

class RegisterForm(Form):
    user = StringField(
            'Username',
            validators=[DataRequired(), Length(min=3, max=25)]
            )
    email = StringField(
            'Email',
            validators=[DataRequired(), Email(), Length(min=6, max=40)]
            )
    pwd = PasswordField(
            'Password',
            validators=[DataRequired(), Length(min=6, max=40)])
    repeat_pwd = PasswordField(
            'Repeat Password',
            validators=[DataRequired(), EqualTo('pwd', message='Passwords must match')]
            )

class LoginForm(Form):
    user = StringField('Username',
            validators=[DataRequired()]
            )
    pwd = PasswordField('Password',
            validators=[DataRequired()]
            )

class TestForm(Form):
    name = StringField('Name of test', 
            validators=[DataRequired()]
            )
    author = StringField('Test author',
            validators=[DataRequired()]
            )
    prob_num = IntegerField('Number of problems',
            validators=[DataRequired(), NumberRange(min=1, max=20, message="Please input an integer from 1 to 20.")]
            )
    min_diff = SelectField('Min difficulty',coerce=int,
            choices=[(5*i, str(5*i)) for i in range(11)])
    max_diff = SelectField('Max difficulty',coerce=int,
            validators=[DataRequired()],
            choices=[(5*i, str(5*i)) for i in range(11)])
    tags = SelectMultipleField('Tags',coerce=int)

    def validate(self):
        if not (Form.validate(self) and self.min_diff.data < self.max_diff.data \
                and len(self.tags.data) <= 3):
            return False
        return True
