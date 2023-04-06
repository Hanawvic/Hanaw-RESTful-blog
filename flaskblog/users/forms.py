from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, Email, Length


# WTForm register
class RegisterForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField('Password',
                             validators=[DataRequired(),
                                         Length(min=8, message="Password should be at least 8 characters")])
    name = StringField("Name", validators=[DataRequired()])
    recaptcha = RecaptchaField()
    submit = SubmitField("Sign me up!")


# WTForm login
class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password",
                             validators=[DataRequired(),
                                         Length(min=8, message="Password should be at least 8 characters")])
    submit = SubmitField("Let me In!")


# Define Flask-WTF form for password reset request
class PasswordResetRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Submit')


# Define Flask-WTF form for password reset
class PasswordResetForm(FlaskForm):
    password = PasswordField('New Password',
                             validators=[DataRequired(),
                                         Length(min=8, message="Password should be at least 8 characters")])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(),
                                                 Length(min=8, message="Password should be at least 8 characters")])
    submit = SubmitField('Reset Password')
