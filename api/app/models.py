from . import db
import hashlib
from datetime import datetime, timedelta, date
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, AnonymousUserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app, request, flash, url_for, g
from .emails import send_email

from app.exceptions import ValidationError


# Create the permission class to handle user permissions.
class Permission:
    COMPLETE=1
    ADD_USER=2
    CREATE=4
    UNCOMPLETE=8
    ADMIN=16


# Create the role class for different user roles.
class Role(db.Model):
    __tablename__ = 'roles'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    users = db.relationship('User', backref='role',lazy='dynamic')
    default = db.Column(db.Boolean, default=False, index=True)
    permissions=db.Column(db.Integer)

    # Run upon object instantiation.
    def __init__(self,**kwargs):
        super(Role,self).__init__(**kwargs)
        if self.permissions is None:
            self.permissions = 0

    # Insert roles into the database.
    @staticmethod
    def insert_roles():
#################################### ACTION ####################################
# Add additional roles, if required.
################################################################################
        roles = {
            'User': [Permission.COMPLETE],
            'Leader':[Permission.COMPLETE,  Permission.CREATE, Permission.ADD_USER],
            'Administrator': [Permission.COMPLETE,
                            Permission.CREATE,
                            Permission.ADMIN,
                            Permission.ADD_USER]}
        default_role = 'User'

        for r in roles:
            role = Role.query.filter_by(name=r).first()

            # Create a new role if not in the datbase.
            if role is None:
                role = Role(name=r)

            # Update role permissions.
            role.reset_permissions()
            for perm in roles[r]:
                role.add_permission(perm)
            role.default = (role.name == default_role)
            db.session.add(role)
        db.session.commit()

    # Add a permission to a role.
    def add_permission(self,perm):
        if not self.has_permission(perm):
            self.permissions += perm

    # Remove a permission from a role.
    def remove_permission(self,perm):
        if self.has_permission(perm):
            self.permissions -= perm

    # Remove all permissions from a role.
    def reset_permissions(self):
        self.permissions = 0

    # Use bitwise to determine if a role has a specific permission.
    def has_permission(self,perm):
        return self.permissions & perm == perm

    # Provide a readable string for debugging/testing.
    def __repr__(self):
        return '<Role %r>' % self.name


# Create a user class.
class User(UserMixin,db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    confirmed = db.Column(db.Boolean,default=False)
    password_hash = db.Column(db.String(128))
    tasks = db.relationship('Task', backref='assigned_user',lazy='dynamic')
    family_id = db.Column(db.Integer, db.ForeignKey('families.id'))


    # Run upon object instantiation.
    def __init__(self,**kwargs):
        super(User,self).__init__(**kwargs)
        if self.role is None:
            if self.email == current_app.config['APP_ADMIN']:
                self.role = Role.query.filter_by(name='Administrator').first()
            else:
                self.role = Role.query.filter_by(default=True).first()

    # Detemine if a user has a specific permission.
    def can(self,perm):
        return self.role is not None and self.role.has_permission(perm)

    # Determine if the user is an administrator.
    def is_administrator(self):
        return self.role.has_permission(Permission.ADMIN)

    # This creates the password property, which cannot be interacted with.
    @property
    def password(self):
        raise AttributeError('Password cannot be read.')

    # This function sets the password_hash once a password is set, using werkzeug.
    @password.setter
    def password(self,password):
        self.password_hash=generate_password_hash(password)

    # This function verifies password input.
    def verify_password(self,password):
        return check_password_hash(self.password_hash,password)

    # Provide a confirmation token for user email confirmation.
    def generate_confirmation_token(self,expires_in=300):
        s = Serializer(current_app.config['SECRET_KEY'],expires_in)
        return s.dumps({'confirm':self.id}).decode('utf-8')

    # Provide a confirmation token to verify a user email change.
    def generate_email_token(self, email,expires_in=600):
        s = Serializer(current_app.config['SECRET_KEY'],expires_in)
        return s.dumps({'email':email,'id':self.id}).decode('utf-8')

    # Confirm the email token, and update the db with the user.
    def confirm_email(self,token):
        s = Serializer(current_app.config['SECRET_KEY'])

        # Reject invalid or expired tokens.
        try:
            data=s.loads(token.encode('utf-8'))
        except:
            return False,'Code invalid or expired.'

        # Ensures the email address is still available.
        if User.query.filter_by(email=data['email']).first():
            return False,"Email address is no longer available"

        # Ensures the current user is logged in to update their email.
        if self.id == data['id']:
            if self.email == data['email']:
                return False,'Email already confirmed.'
            self.email=data['email']
            db.session.add(self)
            return True,'Email has been updated.'
        else:
            return False,'You must be logged in to update your email.'


    # Provide an auth token for api clients.
    def generate_auth_token(self, expires_in=86400):
        s = Serializer(current_app.config['SECRET_KEY'], expires_in=expires_in)
        return s.dumps({'id':self.id}).decode('utf-8')

    # Generate a token to send to an email requesting to join their family.
    def generate_join_request_token(self,leader_id,expires_in=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expires_in=expires_in)
        return s.dumps({'joiner_id':self.id,'leader_id':leader_id}).decode('utf-8')

    # Verify an api clients token, and provide a user if valid.
    @staticmethod
    def verify_auth_token(token):
        s = Serializer(current_app.config['SECRET_KEY'], expires_in=86400)
        try:
            data = s.loads(token) #RESERVED, why not .encode('utf-8')?
        except:
            return None
        return User.query.get(data['id'])

    # This is the function used to confirm a user's credentials provided from
    #   the front end request.
    # Returns a user if validated, and None if incorrect.
    @staticmethod
    def verify_api_credentials(u_email, p_word):
        user = User.query.filter_by(email=u_email).first()
        if user and user.verify_password(p_word):
            return user
        else:
            return None

    # This function will check if a provided key is valid, and then return a
    #   User which will be assigned to the context variable g.
    # This will return a user
    @staticmethod
    def verify_api_token(token):
        s = Serializer(
        current_app._get_current_object().config['SECRET_KEY'])

        # Validate the provided token.
        try:
            data = s.loads(token.encode('utf-8'))
        except:
            return None

        # Troubleshooting aid.
        print (data)

        # Return the user object.
        return User.query.get(data['user_id'])

    # This function will serialize json information is stored for the user.
    def to_json(self):
        json_user = {
            'url':url_for('api.get_user', id=self.id),
            'username': self.username,
            'tasks': [task.to_json() for task in self.tasks],
            'email': self.email
        }
        return json_user

    # This function will create a User object from provided json.
    @staticmethod
    def from_json(json_user):
        username = json_user['username']
        email = json_user['email']
        password = json_user['password']
        return User(username=username, email=email, password=password)

    # Provide a readable string for debugging/testing.
    def __repr__(self):
        return '<User %r>' % self.username


# Create a task class
class Task(db.Model):
    __tablename__='tasks'

    id = db.Column(db.Integer,primary_key=True)
    taskname = db.Column(db.String(64))
    period = db.Column(db.String(7))
    assigned_user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    next_due = db.Column(db.DateTime())
    subtasks = db.relationship('Subtask', backref='task',lazy='dynamic')

    # This establishes the due date based on when the task is assigned.
    # Midnight is assigned as the due time to aid in determining overdue tasks.
    def __init__(self,
                 today=datetime.today().replace(hour=23,minute=59,second=59),
                 **kwargs):
        super(Task,self).__init__(**kwargs)
        #today = datetime.today()
        if self.period == "d":
            self.next_due = today
        elif self.period == "w":
            weekday = 5 #due on saturdays
            if today.weekday() == weekday:
                self.next_due = today
            elif today.weekday() < weekday:
                self.next_due = today + timedelta(days = weekday - today.weekday())
            else:
                self.next_due = today + timedelta(days = (weekday + 7) - today.weekday())
        elif self.period == "m":
            if today.day == 1:
                self.next_due = today
            else:
                if today.month == 12:
                    self.next_due = today.replace(month = 1, year = today.year+1, day=1)
                else:
                    self.next_due = today.replace(month = today.month + 1, day = 1)

    # This function will update the completion date when a task is marked complete
    #   by completing all of its subtasks.
    # It retains the current due date for instances of reopening.
    def update_next_due(self,
                        today=datetime.today().replace(hour=23,minute=59,second=59, microsecond=0)):
        # today = datetime.today()
        if self.period == 'd':
            self.next_due = today + timedelta(days=1)
        elif self.period == 'w':
            while self.next_due < today \
                    or (self.next_due - today) < timedelta(days=7):
                print (self.next_due,today)
                self.next_due = self.next_due + timedelta(days=7)
        elif self.period == "m":
            if today.month==11:
                self.next_due = self.next_due.replace(month=1, year = today.year + 1)
            elif today.month==12:
                self.next_due = self.next_due.replace(month=2, year = today.year + 1)
            else:
                self.next_due = self.next_due.replace(month=today.month + 2)
        db.session.add(self)
        db.session.commit()

    # This function will determine if all subtasks under a task are complete.
    def determine_complete(self):
        for subtask in self.subtasks:
            if not subtask.is_complete:
                return
        self.complete()

    # This function is provided to remove a task and all of its subtasks from
    #   the db.
    # An associated function is not provided for subtasks since they are
    #   able to be deleted one by one.
    def delete(self):
        for subtask in self.subtasks:
            db.session.delete(subtask)
        db.session.delete(self)
        db.session.commit()

    # This will do all the actions required to complete a task.
    # It will also send an email to the leaders in the family that
    #   the task has been complete.
    def complete(self):
        for subtask in self.subtasks:
            subtask.is_complete = False
            db.session.add(subtask)
            db.session.commit()
        self.update_next_due()
        st = self
        leader = Role.query.filter_by(name='Leader').first()
        # Send the email to the leader, and flash a message unless in testing.
        # Testing mode does not allow for threading or flash.
        if current_app.config['TESTING']:
            pass
        else:
            flash(f'{self.taskname} is marked complete!')
            for leader in User.query.filter_by(\
                    role = leader,family_id=st.assigned_user.family_id).all():
                send_email(
                    leader.email,
                    f'{self.assigned_user.username} just completed {self.taskname}!',
                    'mail/task_completed',
                    user = self.assigned_user,
                    task = self
                    )

    # This will return json data for the subject post.
    def to_json(self):
        json_task = {
            'id':self.id,
            'taskname':self.taskname,
            'next_due':self.next_due.strftime('%x'),
            'subtasks':[subtask.to_json() for subtask in self.subtasks],
            'assignee':self.assigned_user.username,
            'overdue':self.next_due < datetime.today()
        }
        return json_task

    # This will create a task and commit it to the db.
    def from_json(json_task):
        taskname = json_task.get('taskname')
        period = json_task.get('period')
        assigned_user_id = json_task.get('assignee')
        if taskname is None or assigned_user_id is None or period is None:
            return None
        else:
            return Task(taskname=taskname,
                        assigned_user_id=assigned_user_id,
                        period=period)

# This defines the subtask class, which holds subtasks identified under tasks.
class Subtask(db.Model):
    __tablename__='subtasks'

    id = db.Column(db.Integer,primary_key=True)
    subtask_name = db.Column(db.String(64))
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'))
    is_complete = db.Column(db.Boolean,default=False)

    # This will mark the subtask as complete.
    # It will also kick the parent task to determine if it is complete.
    def complete(self):
        if self.is_complete:
            flash("Subtask is already complete")
            flash(f'{self.subtask_name}; {self.is_complete}')
            return
        self.is_complete = True
        db.session.add(self)
        db.session.commit()
        self.task.determine_complete()

    def uncomplete(self):
        if not self.is_complete:
            flash('Subtask is not complete yet.')
        else:
            self.is_complete = False
            db.session.add(self)
            db.session.commit()

    # This function returns all pertinent info for a subtask.
    def to_json(self):
        json_subtask = {
            'id':self.id,
            'task_id':self.task_id,
            'subtask_name': self.subtask_name,
            'is_complete':self.is_complete,

        }
        return json_subtask

    # This function receives data from the application api, and creates a
    #   a subtask.
    # The input to this function is handled in the api/tasks.py file in order
    #   to convert the json string literal into a list of dictionaries.
    def from_json(st_json, task_id):
        return Subtask(subtask_name=st_json,
                       task_id=task_id)


class Family(db.Model):
    __tablename__='families'

    id = db.Column(db.Integer,primary_key=True)
    family_name = db.Column(db.String(64))
    members = db.relationship('User', backref='family',lazy='dynamic')

    def add_member(user):
        if user.family_id == self.id:
            return
        else:
            user.family = self
            db.session.add(user)
            db.session.commit()

    def get_family_tasks(self):
        tasks = Task.query.join(User, User.id == Task.assigned_user_id)\
                .filter(User.family_id == self.id).order_by(Task.next_due.asc()).all()
        return tasks

    def generate_family_token(self,email,expires_in=86400):
        s = Serializer(current_app.config['SECRET_KEY'],expires_in)
        return s.dumps({'family_id':self.id,'email':email}).decode('utf-8')

    # This function will return an integer with the nubmer of leaders.
    def count_leaders(self):
        leader_role = Role.query.filter_by(name='Leader').first()
        leaders = len(self.members.filter_by(role=leader_role).all())
        return leaders


# Create an anonymous user class.
class AnonymousUser(AnonymousUserMixin):
    def can(self,perm):
        return False

    def is_administrator(self):
        return False


from . import login_manager


# BUG: THIS DOES NOT ACCOUNT FOR UPDATES IN PERSONAL INFORMATION, but I dont use it yet.
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# This tells the login manager to use the AnonymousUser class for the current_user
login_manager.anonymous_user = AnonymousUser
