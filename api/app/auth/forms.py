from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField,\
    SelectField, ValidationError
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo
from ..models import User

# This form is used to log in.
class LoginForm(FlaskForm):
    email = StringField('Email:', validators=[DataRequired(),
        Email(message='Please provide a valid email address.'),Length(1,64)])
    password = PasswordField('Password:',validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Submit')

# This form is used to register a new user.
class RegistrationForm(FlaskForm):
    email = StringField('Email:', validators=[DataRequired(),Email(),Length(1,64)])
    username = StringField('Username', validators=[
        DataRequired(), Length(1, 64),
        Regexp('^[A-Za-z][A-Za-z0-9_.]*$',
               0,
               'Usernames must have start with a letter, and only '
               'contain letters, numbers, dots or underscores.')])
    password = PasswordField('Password:',validators=[DataRequired()])
    password2 = PasswordField('ReenterPassword:',validators=[
        DataRequired(),EqualTo('password',message='Passwords must match.')])
    submit = SubmitField('Register')

    def validate_email(self,field):
        if User.query.filter_by(email=field.data.lower()).first():
            raise ValidationError('Email already registered.')

    def validate_username(self,field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Username not available.')

# This form is used to resend the confirmation email.
class ResendEmailForm(FlaskForm):
        submit = SubmitField('Resend confirmation email')

# This form is used to change a user's email.
class ChangeEmailForm(FlaskForm):
    new_email = StringField('New Email:', validators=[DataRequired(),Email(),Length(1,64)])
    submit = SubmitField("Send confirmation code")

    def validate_new_email(self,field):
        if User.query.filter_by(email=field.data.lower()).first():
            raise ValidationError('Email already registered.')

# This form is used to request a token to reset a user's password.
class ForgotPasswordForm(FlaskForm):
    email = StringField('Registered Email:', validators=[DataRequired(),Email(),Length(1,64)])
    submit = SubmitField("Send confirmation code.")

# This form is used to reset a user's password.
class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password:',validators=[DataRequired()])
    password2 = PasswordField('ReenterPassword:',validators=[
        DataRequired(),EqualTo('password',message='Passwords must match.')])
    submit = SubmitField('Update password')

# This form is used to change a user's password.
class ChangePasswordForm(FlaskForm):
    crt_pword = PasswordField("Current Password:",validators=[DataRequired()])
    new_pword = PasswordField("New Password:",validators=[DataRequired()])
    new_pword2 = PasswordField("Reenter New Password:",validators=[DataRequired(),
        EqualTo('new_pword',message="Passwords must match.")])
    submit = SubmitField('Change password')

# This form is used to send an email to the family leader, requesting to join.
class RequestToJoinFamilyForm(FlaskForm):
    leader_email = StringField("Leader email address:", validators=[DataRequired(),Email(),Length(1,64)])
    submit = SubmitField("Send Request")

# This form is used to create a family.
class CreateFamilyForm(FlaskForm):
    family_name = StringField("Family Name:")
    submit = SubmitField('Get started with hunnyDu!')

class SendFamilyEmailForm(FlaskForm):
    email = StringField('New Member\'s Email:', validators=[DataRequired(),Email(),Length(1,64)])
    submit = SubmitField('Send registration email!')
