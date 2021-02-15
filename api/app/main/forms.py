from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, BooleanField,\
                    SelectField, DateField
from wtforms.validators import DataRequired,Length,EqualTo,Regexp,Email
from ..models import User, Role, Permission, Family
from flask_pagedown.fields import PageDownField
from flask_login import current_user

# Form used to create a new task.
class TaskForm(FlaskForm):
    taskname = StringField("Name:",validators=[DataRequired()])
    #assigned_user = StringField("assigned_user_id")
    #period = StringField("period")
    assigned_user = SelectField("Assigned to:",validators=[DataRequired()],coerce=int)
    period = SelectField("Due:",validators=[DataRequired()])
    submit = SubmitField("Submit")

    def __init__(self,*args,**kwargs):
        super(TaskForm,self).__init__(*args,**kwargs)
        self.assigned_user.choices = []
        for user in User.query.filter_by(family_id=current_user.family_id).all():
            if user.can(Permission.CREATE):
                self.assigned_user.choices.append((user.id,f'{user.username} - Leader'))
            else:
                self.assigned_user.choices.append((user.id,user.username))
        self.period.choices = [
                ('d','daily'),
                ('w','weekly'),
                ('m','monthly')]

# Form used to create a new subtask.
class SubtaskForm(FlaskForm):
    subtask_name = StringField("Name:",validators=[DataRequired()])
    submit = SubmitField("Submit")

# Form to edit a profile.
class EditProfileAdminForm(FlaskForm):
    username = StringField('Username', validators=[
        DataRequired(), Length(1, 64),
        Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
            'Usernames must have start with a letter, and only '
            'contain letters, numbers, dots or underscores.')])
    confirmed = BooleanField('Confirmed')
    email = StringField('Email', validators=[DataRequired(),Email(),Length(1,64)])
    # This is a drop down option.
    # Choices must be presented as a list of tuples. where (input, display)
    # coerce=int tells it to store the data in the form as an int vice the default
    #   which is a string.
    # This id will be used to query the db later to assign the desired role.
    role = SelectField('Role',coerce=int)
    family = SelectField('Family',coerce=int)
    submit = SubmitField("Submit")

    def __init__(self,user,*args,**kwargs):
        super(EditProfileAdminForm,self).__init__(*args,**kwargs)
        self.role.choices = [(role.id,role.name)
            for role in Role.query.order_by(Role.name).all()]
        self.family.choices = [(family.id, family.family_name)
            for family in Family.query.order_by(Family.family_name).all()]
        self.user = user

    def validate_email(self,field):
        if field.data != self.user.email and \
                User.query.filter_by(email=field.data.lower()).first():
            raise ValidationError('Email already registered.')

    def validate_username(self,field):
        if field.data != self.user.username and \
                User.query.filter_by(username=field.data).first():
            raise ValidationError('Username not available.')
