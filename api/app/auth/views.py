from datetime import datetime
from flask import render_template, session, redirect, url_for, flash, request,\
    current_app
from . import auth
from .forms import LoginForm, RegistrationForm,ResendEmailForm,ChangeEmailForm,\
    ForgotPasswordForm,ResetPasswordForm,ChangePasswordForm, RequestToJoinFamilyForm,\
    CreateFamilyForm,SendFamilyEmailForm
from .. import db
from ..models import User, Family, Role, Permission
from flask_login import login_required, login_user, logout_user, current_user
from ..emails import send_email
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from ..decorators import leader_required, permission_required

# View function for logging users in.
@auth.route('/login', methods=['GET','POST'])
def login():

    #This view function serves as a means to verify users credentials.

    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user,form.remember_me.data)
            next = request.args.get('next')
            if next is None or not next.startswith('/'):
                next = url_for('main.dashboard')
            return redirect(next)
        else:
            flash('Invalid username or password.')
    return render_template('auth/login.html',form=form)

# View function for logging users out.
@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('auth.login'))

# View function for registering new users, and send a confirmation token.
###############################################################################
################## Potential mod, pass in family if sent from the outside.
@auth.route('/register',methods=['GET','POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data,
            email=form.email.data.lower(),
            password=form.password.data,
            role_id=None)
        # This part will only run if sent from an external link.
        if session.get('family_id'):
            user.family_id = session.get('family_id')
            session['family_id'] = None
        db.session.add(user)
        db.session.commit()
        user = User.query.filter_by(username=form.username.data).first()
        token = user.generate_confirmation_token()
        send_email(
            user.email,
            'Confirm Email',
            'auth/mail/confirm_user',
            user=user,
            token=token
            )
        flash("A confirmation request has been sent to your email!")
        return redirect(url_for('auth.login'))
    var = session.get('family_id')
    return render_template('auth/register.html',form=form)


# This is the route which is used to assign family_id's to users.
# 2 Cases: user has registered, or user has not registered.
# If the query for the user's email succeeds, the family_id is assigned.
# Otherwise, a session variable is stored, and the user is redirected to registry.
@auth.route('/register/<token>',methods=['GET'])
def register_from_email(token):
    s = Serializer(
        current_app._get_current_object().config['SECRET_KEY'],
        expires_in=60)

    # Validate the token.
    try:
        data = s.loads(token.encode('utf-8'))
    except:
        flash('Invalid or expired confirmation token.')
        return redirect(url_for('.login'))

    # Assigned the family id to an existing user.
    u = User.query.filter_by(email=data['email']).first()
    if u:
        # BUGZ: Will reassign family no matter what.
        u.family_id = data['family_id']
        db.session.add(u)
        db.session.commit()
        return redirect(url_for('auth.login'))

    # If no user exists yet with that email, then sends for registration.
    else:
        session['family_id'] = data['family_id']
        return redirect(url_for('auth.register'))


# This will be used to send emails to join a family for
@auth.route('/sendfamilyemail',methods=['GET','POST'])
@permission_required(Permission.ADD_USER)
def send_family_email():
    form = SendFamilyEmailForm()
    if form.validate_on_submit():
        email = form.email.data.lower()
        token = current_user.family.generate_family_token(email)
        send_email(
            email,
            'HunnyDU: Join the family!',
            'auth/mail/join_family',
            user=current_user,
            token=token
            )
        flash(f'Email sent to {email}')
        return redirect(url_for('main.dashboard'))
    return render_template('/auth/send_family_email.html',form=form)


# View function for confirming a confirmation token.
@auth.route('/confirm/<token>')
def confirm(token):
    s = Serializer(
        current_app._get_current_object().config['SECRET_KEY'],
        expires_in=60)

    # Validate the token.
    try:
        data = s.loads(token.encode('utf-8'))
    except:
        flash('Invalid or expired confirmation token.')
        return redirect(url_for('.login'))

    # Confirm the user.
    user = User.query.filter_by(id=data['confirm']).first()
    if user.confirmed is False:
        user.confirmed = True
        db.session.add(user)
        db.session.commit()
        flash('User email confirmed.')
    else:
        flash("Email already confirmed.")
    return redirect(url_for('.login'))


# View function for unconfirmed users.
@auth.route('/unconfirmed',methods=['GET','POST'])
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('main.index'))

    # Form for resending confirmtion email.
    form = ResendEmailForm()
    if form.validate_on_submit():
        token = current_user.generate_confirmation_token()
        send_email(
            current_user.email,
            'Confirm Email',
            'auth/mail/confirm_user',
            user=current_user,
            token=token
            )
        flash("A confirmation request has been sent to your email!")
        return redirect(url_for('.login'))
    return render_template('auth/unconfirmed.html',form=form)


# View function for viewing contact info.
@auth.route('/change_info',methods=["GET","POST"])
@login_required
def change_info():
    return render_template('auth/change_info.html',user=current_user)

# View function for changing email.
@auth.route('/change_email',methods=["GET","POST"])
@login_required
def change_email():
    form=ChangeEmailForm()
    if form.validate_on_submit():
        token = current_user.generate_email_token(form.new_email.data.lower())
        send_email(
            form.new_email.data.lower(),
            'Confirm Email',
            'auth/mail/confirm_email',
            user=current_user,
            token=token
            )
        flash("A confirmation request has been sent to your email!")
        return redirect(url_for('.login'))
    return render_template('auth/change_email.html',form=form,user=current_user)


# View function for confirming email changes.
@auth.route('/update_email/<token>')
@login_required
def update_email(token):
    input = current_user.confirm_email(token)
    if input[0]:
        flash(f'{input[1]}')
        db.session.commit()
        return redirect(url_for('.change_info'))
    else:
        flash(f'{input[1]}')
        return redirect(url_for('.change_info'))

# View function for sending a password reset token.
@auth.route('/forgot_password',methods=['GET','POST'])
def forgot_password():
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user and user.confirmed:
            token = user.generate_confirmation_token()
            send_email(
                user.email,
                'Password Reset',
                'auth/mail/reset_password',
                user=current_user,
                token=token
                )
        elif user and not user.confirmed:
            flash("Please confirm your email address.")
            return redirect(url_for('auth.unconfirmed'))
        flash('Confirmation email sent.')
        return redirect(url_for('auth.login'))
    return render_template('auth/forgot_password.html',form=form)

# View function for verifying a password reset token.
@auth.route('/reset_password/<token>',methods=['GET','POST'])
def reset_password(token):
    s = Serializer(
        current_app._get_current_object().config['SECRET_KEY'],
        expires_in=60)
    try:
        data = s.loads(token.encode('utf-8'))
    except:
        flash('Invalid or expired confirmation token.')
        return redirect(url_for('.login'))
    session['temp_user_id'] = User.query.filter_by(id=data['confirm']).first().id
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(id=session.get('temp_user_id')).first()
        user.password = form.password.data
        db.session.add(user)
        db.session.commit()
        flash('Password reset.')
        return redirect(url_for('auth.login'))
    return render_template('auth/change_password.html',form=form)

# View function for changing a users password.
@auth.route('/change_password',methods=['GET','POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.crt_pword.data):
            current_user.password=form.new_pword.data
            db.session.add(current_user)
            db.session.commit()
            flash("Password has been updated.")
            return redirect(url_for('.change_info'))
        else:
            flash('Invalid password.')
    return render_template('auth/change_password_elective.html',form=form)

# View function to send a request to join email to a leader
# Will send a crypto token to the users email, and then kick them to a
#   view function that will add the user to the family.
@auth.route('/joinfamily',methods=['GET','POST'])
@login_required
def join_family():
    form = RequestToJoinFamilyForm()
    if form.validate_on_submit():
        target_email = form.leader_email.data.lower()
        leader = User.query.filter_by(email=target_email).first()
        if leader and leader.can(Permission.ADD_USER):
            send_email(
                leader.email,
                f'{current_user.username} wants to join your family',
                'auth/mail/request_join_family',
                user=current_user,
                token = current_user.generate_join_request_token(leader.id)
                )
        flash(f"Email request sent to \"{form.leader_email.data.lower()}\".")
        return redirect(url_for('main.dashboard'))
    return render_template('/auth/request_join_family.html',form=form)


# View function to add a user to a family from an email request to the leader.
@auth.route('/addfromemail/<token>', methods=['GET'])
@login_required # This processes first, so you won't get immediately booted
                # for anonymous user permissions.
@permission_required(Permission.ADD_USER)
def add_from_email(token):
    s = Serializer(
        current_app._get_current_object().config['SECRET_KEY'],
        expires_in=3600)
    try:
        data = s.loads(token.encode('utf-8'))
    except:
        flash('Invalid or expired confirmation token.')
        return redirect(url_for('.login'))
    if current_user.id == data['leader_id']:
        u = User.query.get_or_404(data['joiner_id'])
        u.family_id = current_user.family_id
        db.session.add(u)
        db.session.commit()
        flash(f'Added {u.username} to your family!')
    else:
        flash('You are not the leader for this family!')
    return redirect(url_for('main.dashboard'))

# View function to add a family to the database
@auth.route('/createfamily',methods=['GET','POST'])
@login_required
def create_family():
    form = CreateFamilyForm()
    if form.validate_on_submit():
        f = Family(family_name=form.family_name.data)
        db.session.add(f)
        db.session.commit()
        u = current_user._get_current_object()
        u.family = f
        if u.role.name == 'User':
            u.role = Role.query.filter_by(name='Leader').first()
        db.session.add(u)
        db.session.commit()
        return redirect(url_for('main.dashboard'))
    return render_template('auth/create_family.html',form=form)

# Verify user is confirmed before allowing full access.
@auth.before_app_request
def before_request():
    if current_user.is_authenticated:
        if not current_user.confirmed and \
            request.endpoint and \
            request.blueprint != 'auth' and \
            request.endpoint != 'static':
            return redirect(url_for('auth.unconfirmed'))
