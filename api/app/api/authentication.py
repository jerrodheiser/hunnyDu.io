from . import api
from .. import db
import ast
from flask import g, jsonify, current_app, request
from ..models import User, Role, Family
from ..emails import send_email
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from .decorators import permission_required, leader_required, \
        login_required


# Route for user login.
# Response will indicate successful login or failure.
# If successful, user session information is provided.
@api.route('/auth/login', methods=['POST'])
def login():
    email_or_token = request.json.get('auth')['email_or_token']
    password = request.json.get('auth')['password']

    # Return a bad request message if required data is not provided.
    if email_or_token == '' or password == '':
        response = jsonify({'error':'bad request','message':'Provide user credentials.'})
        response.status_code = 400
        return response
    else:
        user = User.verify_api_credentials(email_or_token, password)
        if user is None:
            response = jsonify({'error':'unauthorized','message':'User credentials invalid.'})
            response.status_code = 401
            return response

        # Generate the response.
        if user.family:
            family_name = user.family.family_name
            family_id = user.family.id
            leaders = user.family.count_leaders()
            members = [{'name':member.username,
                        'id':member.id,
                        'isLeader': member.role.name == 'Leader',
                        'isOnlyLeader': leaders == 1 and  member.role.name == 'Leader'
                        }
                for member in user.family.members.all()]
        else:
            family_name = ''
            family_id = ''
            members = []
            leaders = 0
        response = jsonify({'token': user.generate_auth_token(),
                        'confirmed': user.confirmed,
                        'id': user.id,
                        'family_name': family_name,
                        'family_id': family_id,
                        'members': members,
                        'isLeader': user.role.name == 'Leader',
                        'leaders': leaders})
        response.status_code = 200
        return response


# Route to retrieve a user's family info.
@api.route('/auth/getFamily', methods=['POST'])
@login_required
def get_family():
    if g.current_user.family:
        family_name = g.current_user.family.family_name
        family_id = g.current_user.family.id
        leaders = g.current_user.family.count_leaders()
        members = [{'name':member.username,
                    'id':member.id,
                    'isLeader': member.role.name == 'Leader',
                    'isOnlyLeader': leaders == 1 and  member.role.name == 'Leader'}
            for member in g.current_user.family.members.all()]
    else:
        family_name = ''
        family_id = ''
        members = []
        leaders = 0
    isLeader = g.current_user.role.name == 'Leader'
    # Generate the response.
    response = jsonify({'family_name':family_name,
                    'family_id':family_id,
                    'members':members,
                    'isLeader':isLeader,
                    'leaders':leaders})
    response.status_code = 200
    return response


# Route for user registration.
# If the username or email exist in the database, code 207 will be returned
#   identifying the subject values.
# Response code 200 and confirmation email will be sent upon success.
@api.route('/auth/registration', methods=['POST'])
def register_user():
    # Determine if user credentials are available.
    user_json = ast.literal_eval(request.json.get('body'))
    u_email = User.query.filter_by(email=user_json['email']).first()
    u_username = User.query.filter_by(username=user_json['username']).first()
    if u_email and u_username:
        response = jsonify({'email':u_email.email, 'username':u_username.username})
        response.status_code = 207
        return response
    if u_email:
        response = jsonify({'email':u_email.email})
        response.status_code = 207
        return response
    if u_username:
        response = jsonify({'username':u_username.username})
        response.status_code = 207
        return response

    # Create new user in the db.
    user = User.from_json(user_json)
    db.session.add(user)
    db.session.commit()

    # Send confirmation email and generate the response.
    token = user.generate_confirmation_token()
    send_email(
        user.email,
        'Confirm Registration',
        'auth/mail/confirm_user_api',
        user=user,
        token=token
        )
    response = jsonify({'message':f'Successfully created user {user_json["username"]}'})
    response.status_code = 201
    return response


# Route to resend a user's confirmation email.
@api.route('/auth/resendConfirmationEmail', methods=['POST'])
def resend_confirmation_email():
    user_id = ast.literal_eval(request.json.get('body'))['id']
    user = User.query.get_or_404(user_id)

    # Send confirmation email and generate the response.
    token = user.generate_confirmation_token()
    send_email(
        user.email,
        'Confirm Registration',
        'auth/mail/confirm_user_api',
        user=user,
        token=token
        )
    response = jsonify({'message':'Confirmation email sent.'})
    response.status_code = 200
    return response


# Route for user confirmation.
# Response code will be 200 for success, or 401 for unauthorized.
@api.route('/auth/confirmUser/<token>', methods=['POST'])
def confirm_user(token):
    s = Serializer(
        current_app._get_current_object().config['SECRET_KEY'],
        expires_in=60)

    # Validate the token.
    try:
        data = s.loads(token.encode('utf-8'))
    except:
        response = jsonify({'errMessage':'Invalid confirmation token.'})
        response.status_code = 401
        return response

    # Confirm the user, and generate the response.
    user = User.query.filter_by(id=data['confirm']).first()
    if user.confirmed is False:
        user.confirmed = True
        db.session.add(user)
        db.session.commit()
        response = jsonify({'message':f'User {user.username} confirmed.'})
        response.status_code = 200
    else:
        response = jsonify({'message':f'User {user.username} already confirmed.'})
        response.status_code = 202
    return response


# Route for sending invitations to join a family.
# Response code 200 and invitation email sent upon success.
@api.route('/auth/sendFamilyInvite', methods=['POST'])
@leader_required
def send_family_invite():
    email = ast.literal_eval(request.json.get('body'))['email']
    fam_id = g.current_user.family.id
    token = g.current_user.family.generate_family_token(email)
    send_email(
        email,
        'HunnyDU: Join the family!',
        'auth/mail/join_family_api',
        user=g.current_user,
        token=token
        )
    # Generate the response.
    response = jsonify({'message':f'Join request email sent to {email} for family {g.current_user.family.family_name}.'})
    response.status_code = 200
    return response


# Route to confirm a invitation to join a family.
# Response code 200 for success.
@api.route('/auth/confirmInviteToken/<token>', methods=['POST'])
def confirm_join_family(token):
    s = Serializer(
        current_app._get_current_object().config['SECRET_KEY'],
        expires_in=86400)

    # Validate the token.
    try:
        data = s.loads(token.encode('utf-8'))
    except:
        response = jsonify({'errMessage':'Invalid confirmation token.'})
        response.status_code = 401
        return response

    u = User.query.filter_by(email=data['email']).first()

    # Update the user, and generate the response.
    if u:
        # BUGZ: Will reassign family no matter what.
        u.family_id = data['family_id']
        u.role = Role.query.filter_by(name='User').first()
        db.session.add(u)
        db.session.commit()
        response = jsonify({'message':f'User ({u.username}) family updated.'})
        response.status_code = 200
        return response
    # Generate response for no user found.
    # else:
    #     response = jsonify({'message':f'User not found with the target email.'})
    #     response.status_code = 404
    #     return response


# Route to send a password reset email.
# Response code 200 always sent.
@api.route('/auth/sendResetRequest', methods=['POST'])
def send_reset_request():
    email = ast.literal_eval(request.json.get('body'))['email']
    user = User.query.filter_by(email=email).first()
    # Send the password reset request.
    if user:
        token = user.generate_confirmation_token()
        send_email(
            email,
            'HunnyDU: Password Reset',
            'auth/mail/reset_password_api',
            user=user,
            token=token
            )
    # Generate the response.
    response = jsonify({'message':f'Password reset email sent to {email}.'})
    response.status_code = 200
    return response


# Route to determine validity of password reset tokens.
# Response is code 200 for valid, and 401 for invalid.
@api.route('/auth/validateResetRequest/<token>', methods=['POST'])
def validate_reset_request(token):
    s = Serializer(
        current_app._get_current_object().config['SECRET_KEY'],
        expires_in=300)

    # Validate the token.
    try:
        data = s.loads(token.encode('utf-8'))
    except:
        response = jsonify({'errMessage':'Invalid token.'})
        response.status_code = 401
        return response

    # Confirm the user, and generate the response.
    if User.query.get_or_404(data['confirm']):
        response = jsonify({'message':'Token validated.'})
        response.status_code = 200
        return response


# Route to reset a users forgotten password.
# Response code is 200 for success, and 401 for invalid token.
@api.route('/auth/processPasswordReset', methods=['POST'])
def process_reset_request():
    token = ast.literal_eval(request.json.get('body'))['token']
    s = Serializer(
        current_app._get_current_object().config['SECRET_KEY'],
        expires_in=300)

    # Validate the token.
    try:
        data = s.loads(token.encode('utf-8'))
    except:
        response = jsonify({'errMessage':'Invalid token.'})
        response.status_code = 401
        return response

    # Update user information, and generate the response.
    user = User.query.filter_by(id=data['confirm']).first()
    if user:
        user.password = ast.literal_eval(request.json.get('body'))['password']
        db.session.add(user)
        db.session.commit()
        response = jsonify({'message':'Success'})
        response.status_code = 200
    else:
        response = jsonify({'errMessage':f'Invalid token.'})
        response.status_code = 401
    return response


# Route to remove a family member from a family.
# Response code is 200 for success.
@api.route('/auth/removeFamilyMember', methods=['POST'])
@leader_required
def remove_family_member():
    id = ast.literal_eval(request.json.get('body'))['id']
    user = User.query.get_or_404(id)
    # Removes a user's tasks.
    for task in user.tasks:
        task.delete()
    user.family = None
    db.session.add(user)
    db.session.commit()
    # Generate the response.
    response = jsonify({'user_removed':f'{user.username}'})
    response.status_code = 200
    return response


# Route to give a user leader permissions.
# Response code is 200 for success.
@api.route('/auth/makeLeader', methods=['POST'])
@leader_required
def make_leader():
    id = ast.literal_eval(request.json.get('body'))['id']
    user = User.query.get_or_404(id)
    user.role = Role.query.filter_by(name='Leader').first()
    db.session.add(user)
    db.session.commit()
    # Generate the response.
    response = jsonify({'increased_privileges':f'{user.username}'})
    response.status_code = 200
    return response


# Route to remove a user leader permissions.
# Response code is 200 for success.
# If there is only one user, the function will not run.
@api.route('/auth/unmakeLeader', methods=['POST'])
@leader_required
def unmake_leader():
    id = ast.literal_eval(request.json.get('body'))['id']
    user = User.query.get_or_404(id)
    user.role = Role.query.filter_by(name='User').first()
    db.session.add(user)
    db.session.commit()
    # Generate the response.
    response = jsonify({'reduced_privileges':f'{user.username}'})
    response.status_code = 200
    return response


# Route to send a change email request.
# Response code 200 and email sent upon success.
@api.route('/auth/changeEmailRequest', methods=['POST'])
@login_required
def send_change_email_request():
    email = ast.literal_eval(request.json.get('body'))['email']
    if email:
        # Send email and generate the response.
        token = g.current_user.generate_email_token(email)
        send_email(
            email,
            'HunnyDU: Email Change',
            'auth/mail/confirm_email_api',
            user=g.current_user,
            token=token
            )
        response = jsonify({'message':'email sent'})
        response.status_code = 200
        return response
    else:
        response = jsonify({'errMessage':'Failed change email request.'})
        response.status_code = 400
        return response


# Route to update a user's email address.
# Response code 207 sent if email is not available.
# Response code 200 sent for successful update.
@api.route('/auth/confirmChangeEmail', methods=['POST'])
def confirm_change_email():
    token = ast.literal_eval(request.json.get('body'))['token']
    s = Serializer(
        current_app._get_current_object().config['SECRET_KEY'],
        expires_in=600)

    # Validate the token.
    try:
        data = s.loads(token.encode('utf-8'))
    except:
        response = jsonify({'errMessage':'Invalid token.'})
        response.status_code = 401
        return response

    user = User.query.filter_by(id=data['id']).first()
    email = data['email']
    if user:
        # Determine if email address is still available.
        if User.query.filter_by(email=email).all():
            response = jsonify({'message':'Duplicate email.'})
            response.status_code = 207
            return response
        else:
            # Update user, and generate the response.
            user.email = email
            db.session.add(user)
            db.session.commit()
            response = jsonify({'message':'Success'})
            response.status_code = 200
            return response


# Route used to create a new family.
# Response code 201 sent upon success.
@api.route('/auth/createFamily', methods=['POST'])
@login_required
def create_family():
    family_name = ast.literal_eval(request.json.get('body'))['familyName']
    if family_name:
        # Create new family, and assign current_user as the leader.
        fam = Family(family_name=family_name)
        db.session.add(fam)
        db.session.commit()
        g.current_user.family_id = fam.id
        g.current_user.role = Role.query.filter_by(name='Leader').first()
        db.session.add(g.current_user)
        db.session.commit()
        response = jsonify({'message':'Successful family creation.'})
        response.status_code = 201
        return response
    else:
        response = jsonify({'errMessage':'Failed family creation.'})
        response.status_code = 400
        return response


# This function will change a users provided password.
# Route to change a user's password.
# Response code 401 sent if old password invalid.
@api.route('/auth/changePassword', methods = ['POST'])
@login_required
def change_password():
    oldPass = ast.literal_eval(request.json.get('body'))['oldPass']
    if g.current_user.verify_password(oldPass):
        # Update user's password, and generate the response.
        g.current_user.password = ast.literal_eval(request.json.get('body'))['newPass']
        db.session.add(g.current_user)
        db.session.commit()
        response = jsonify({'message':'Successful password change.'})
        response.status_code = 200
        return response
    else:
        response = jsonify({'errMessage':'Failed password change.'})
        response.status_code = 401
        return response


# Function to run before auth routes.
# This will set g for the current request.
@api.before_request
def before_request():
    # print (request.get_json())
    user = User.verify_auth_token(request.get_json()['auth']['email_or_token'])
    if user:
        g.current_user = user
    else:
        g.current_user = None
