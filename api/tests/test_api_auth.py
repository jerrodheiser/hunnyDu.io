import unittest
import re
from base64 import b64encode
import json
from flask import url_for
from app import create_app, db
from app.models import User, Role, Family


# This will load a user and family for testing.
# This is not included in teh setup since some tests require testing these
#       elements individually.
def load_user(with_family=False, confirmed=True, other_user=False):
    f = Family(family_name='f')
    db.session.add(f)
    db.session.commit()
    u = User(username='u', email='u', password='u',
             family_id=f.id if with_family==True else None,
             role = Role.query.filter_by(name='Leader').first() if \
                    with_family==True else None,
             confirmed=confirmed)
    db.session.add(u)
    db.session.commit()
    if other_user:
        u2 = User(username='u2', email='u2', password='u2',
                 family_id=f.id, confirmed=True)
        db.session.add(u2)
        db.session.commit()
        return u,f,u2
    return u,f


# This will test the api functions of this app.
class APITestCase(unittest.TestCase):

    #  Setup for the test.
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        Role.insert_roles()
        self.client = self.app.test_client(use_cookies=True)


    # Remove upon completion of the test.
    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()


    # Test the /api/auth/login route.
    def test_login(self):
        u,f = load_user()

        # No username or password
        response = self.client.post('/api/auth/login',
                data=json.dumps({
                    'auth':
                        {"email_or_token":'', "password":''}
                    }),
                content_type='application/json')
        self.assertEqual(response.status_code, 400)

        # No password
        response = self.client.post('/api/auth/login',
                data=json.dumps({
                    'auth':
                        {"email_or_token":'fake_token', "password":''}
                    }),
                content_type='application/json')
        self.assertEqual(response.status_code, 400)

        # Invalid username/password combo
        response = self.client.post('/api/auth/login',
                data=json.dumps({
                    'auth':{"email_or_token":"u", "password":"f"}
                }),
                content_type='application/json')
        self.assertEqual(response.status_code, 401)

        # Valid username/password combo, no family assigned
        response = self.client.post('/api/auth/login',
                data=json.dumps({
                    'auth':{"email_or_token":"u", "password":"u"}
                }),
                content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()['family_name'],'')
        self.assertEqual(response.get_json()['family_id'],'')
        self.assertEqual(response.get_json()['members'],[])
        self.assertEqual(response.get_json()['leaders'],0)
        self.assertNotEqual(response.get_json()['token'],'')

        # Assign user a family
        f = Family(family_name='f')
        db.session.add(f)
        db.session.commit()
        u.family = f
        u.role = Role.query.filter_by(name='Leader').first()
        db.session.add(u)
        db.session.commit()

        # Valid username/password combo, no family assigned
        response = self.client.post('/api/auth/login',
                data=json.dumps({
                    'auth':{"email_or_token":"u", "password":"u"}
                }),
                content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(response.get_json()['family_name'],'')
        self.assertNotEqual(response.get_json()['family_id'],'')
        self.assertNotEqual(response.get_json()['members'],[])
        self.assertNotEqual(response.get_json()['leaders'],0)


    # Test the /api/auth/getFamily route.
    def test_getFamily(self):
        u,f = load_user()
        token = u.generate_auth_token()

        # Test for a User with no family assigned.
        response = self.client.post('/api/auth/getFamily',
                data=json.dumps({
                    'auth':{"email_or_token":token}
                }),
                content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()['family_name'],'')
        self.assertEqual(response.get_json()['family_id'],'')
        self.assertEqual(response.get_json()['members'],[])
        self.assertEqual(response.get_json()['leaders'],0)
        self.assertEqual(response.get_json()['isLeader'],False)

        # Assign the user family.
        u.family = f
        u.role = Role.query.filter_by(name='Leader').first()
        db.session.add(u)
        db.session.commit()

        # Test for a User with a family assigned.
        response = self.client.post('/api/auth/getFamily',
                data=json.dumps({
                    'auth':{"email_or_token":token}
                }),
                content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()['family_name'],'f')
        self.assertEqual(response.get_json()['family_id'],1)
        self.assertEqual(response.get_json()['members'],[
                {'name':'u', 'id':1, 'isLeader':True, 'isOnlyLeader':True}])
        self.assertEqual(response.get_json()['leaders'],1)
        self.assertEqual(response.get_json()['isLeader'],True)


    # Test the /api/auth/registration route.
    def test_registerUser(self):
        u,f = load_user(True)

        # Test username and email unavailable.

        # The communication of api body is through string literals to facilitate
        #       handling multi-layered json objects (subtasks specifically).
        post_body = '{"username":"u","email":"u","password":"new"}'

        response = self.client.post('/api/auth/registration',
                data=json.dumps({
                    'auth':{"email_or_token":""},
                    'body':post_body
                }),
                content_type='application/json')
        self.assertEqual(response.status_code,207)
        self.assertEqual(response.get_json()["email"], "u")
        self.assertEqual(response.get_json()["username"], "u")

        # Test email unavailable.
        post_body = '{"username":"new","email":"u","password":"new"}'
        response = self.client.post('/api/auth/registration',
                data=json.dumps({
                    'auth':{"email_or_token":""},
                    'body':post_body
                }),
                content_type='application/json')
        self.assertEqual(response.status_code,207)
        self.assertEqual(response.get_json()["email"], "u")
        self.assertIsNone(response.get_json().get("username"))

        # Test username and email unavailable.
        post_body = '{"username":"u","email":"new","password":"new"}'
        response = self.client.post('/api/auth/registration',
                data=json.dumps({
                    'auth':{"email_or_token":""},
                    'body':post_body
                }),
                content_type='application/json')
        self.assertEqual(response.status_code,207)
        self.assertEqual(response.get_json()["username"], "u")
        self.assertIsNone(response.get_json().get("email"))

        # Test correct registration.
        post_body = '{"username":"new","email":"new","password":"new"}'
        response = self.client.post('/api/auth/registration',
                data=json.dumps({
                    'auth':{"email_or_token":""},
                    'body':post_body
                }),
                content_type='application/json')
        self.assertEqual(response.status_code,201)
        self.assertEqual(response.get_json()["message"], "Successfully created user new")

        user = User.query.filter_by(username='new').first()
        self.assertIsNotNone(user)
        self.assertEqual(user.username,'new')
        self.assertEqual(user.email,'new')
        self.assertTrue(user.verify_password,'new')


    # Tests the /api/auth/resendConfirmationEmail route.
    def test_resendConfirmationEmail(self):
        u,f = load_user(False, False)

        # Test for bad user id
        post_body = '{"id":0}'
        response = self.client.post('/api/auth/resendConfirmationEmail',
                data=json.dumps({
                    'auth':{"email_or_token":""},
                    'body':post_body
                }),
                content_type='application/json')
        self.assertEqual(response.status_code,404)

        # Test for good user id
        # u.id will equal 1
        post_body = '{"id":1}'
        response = self.client.post('/api/auth/resendConfirmationEmail',
                data=json.dumps({
                    'auth':{"email_or_token":""},
                    'body':post_body
                }),
                content_type='application/json')
        self.assertEqual(response.status_code,200)
        self.assertEqual(response.get_json()['message'],'Confirmation email sent.')


    # Tests the /api/auth/confirmUser/<token> route.
    def test_confirmUser(self):
        u,f = load_user(False, False)
        token = u.generate_confirmation_token()
        self.assertFalse(u.confirmed)

        # Test incorrect token
        response = self.client.post('/api/auth/confirmUser/bum_token',
                data=json.dumps({
                    'auth':{"email_or_token":""},
                    'body':''
                }),
                content_type='application/json')
        self.assertEqual(response.status_code, 401)

        # Test correct token and user unconfirmed.
        response = self.client.post(f'/api/auth/confirmUser/{token}',
                data=json.dumps({
                    'auth':{"email_or_token":""},
                    'body':''
                }),
                content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(u.confirmed)
        self.assertEqual(response.get_json()['message'], 'User u confirmed.')

        # Test correct token and user confirmed.
        response = self.client.post(f'/api/auth/confirmUser/{token}',
                data=json.dumps({
                    'auth':{"email_or_token":""},
                    'body':''
                }),
                content_type='application/json')
        self.assertEqual(response.status_code, 202)
        self.assertEqual(response.get_json()['message'], 'User u already confirmed.')


    # Tests the /api/auth/sendFamilyInvite route.
    def test_sendFamilyInvite(self):
        u,f = load_user(True, False)
        token = u.generate_auth_token()
        post_body = '{"email":"none"}'
        response = self.client.post('/api/auth/sendFamilyInvite',
                data=json.dumps({
                    'auth':{"email_or_token":token},
                    'body':post_body
                }),
                content_type='application/json')
        self.assertEqual(response.status_code,200)
        self.assertEqual(response.get_json()['message'],
                'Join request email sent to none for family f.')


    # Tests the /api/auth/confirmInviteToken/<token> route.
    def test_confirmJoinFamily(self):
        u,f = load_user(False, False)
        token = f.generate_family_token('u')
        self.assertIsNone(u.family)

        # Test invalid token.
        post_body = '{"email":"none"}'
        response = self.client.post('/api/auth/confirmInviteToken/bum_token',
                data=json.dumps({
                    'auth':{"email_or_token":""},
                    'body':post_body
                }),
                content_type='application/json')
        self.assertEqual(response.status_code,401)


        # Test valid token.
        post_body = '{"email":"none"}'
        response = self.client.post(f'/api/auth/confirmInviteToken/{token}',
                data=json.dumps({
                    'auth':{"email_or_token":""},
                    'body':post_body
                }),
                content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(u.family.id, f.id)
        self.assertEqual(u.role, Role.query.filter_by(name='User').first())


    # Tests the /api/auth/sendResetRequest route.
    def test_sendResetRequest(self):

        # Test for non-existent user.
        # Response will be identical for existing user.
        post_body = '{"email":"nobody"}'
        response = self.client.post('/api/auth/sendResetRequest',
                data=json.dumps({
                    'auth':{"email_or_token":""},
                    'body':post_body
                }),
                content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()['message'],
                'Password reset email sent to nobody.')

        # Test for existing user.
        u,f = load_user()
        post_body = '{"email":"u"}'
        response = self.client.post('/api/auth/sendResetRequest',
                data=json.dumps({
                    'auth':{"email_or_token":""},
                    'body':post_body
                }),
                content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()['message'],
                'Password reset email sent to u.')

    # Tests the /api/auth/validateResetRequest route.
    def test_validateResetRequest(self):
        u,f = load_user()
        token = u.generate_confirmation_token()

        # Test for invalid token.
        post_body = '{"email":"nobody"}'
        response = self.client.post('/api/auth/validateResetRequest/bum_token',
                data=json.dumps({
                    'auth':{"email_or_token":""},
                    'body':post_body
                }),
                content_type='application/json')
        self.assertEqual(response.status_code,401)

        # Test for valid token.
        post_body = '{"email":"nobody"}'
        response = self.client.post(f'/api/auth/validateResetRequest/{token}',
                data=json.dumps({
                    'auth':{"email_or_token":""},
                    'body':post_body
                }),
                content_type='application/json')
        self.assertEqual(response.status_code, 200)

    # Tests the /api/auth/processPasswordReset route.
    def test_processPasswordReset(self):
        u,f = load_user()
        token = u.generate_confirmation_token()

        # Test for invalid token.
        post_body = '{"token":' + 'None' + ',"password":"new"}'
        response = self.client.post('/api/auth/processPasswordReset',
                data=json.dumps({
                    'auth':{"email_or_token":""},
                    'body':post_body
                }),
                content_type='application/json')
        self.assertEqual(response.status_code,401)

        # Test for valid token.
        post_body = '{"token":' + f'{token}' + ',"password":"new"}'
        response = self.client.post(f'/api/auth/validateResetRequest/{token}',
                data=json.dumps({
                    'auth':{"email_or_token":""},
                    'body':post_body
                }),
                content_type='application/json')
        self.assertEqual(response.status_code, 200)

    # Tests the /api/auth/removeFamilyMember route.
    def test_removeFamilyMember(self):
        u,f,u2 = load_user(True,True,True)
        token = u.generate_auth_token()

        # Test for invalid user id.
        post_body = '{"id":' + '""}'
        response = self.client.post('/api/auth/removeFamilyMember',
                data=json.dumps({
                    'auth':{"email_or_token":token},
                    'body':post_body
                }),
                content_type='application/json')
        self.assertEqual(response.status_code, 404)

        # Test for valid user id.
        self.assertEqual(u2.family_id, f.id)
        post_body = '{"id":' + f'{u2.id}' + '}'
        response = self.client.post('/api/auth/removeFamilyMember',
                data=json.dumps({
                    'auth':{"email_or_token":token},
                    'body':post_body
                }),
                content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(u2.family_id, f.id)
        self.assertEqual(response.get_json(),{'user_removed':f'{u2.username}'})

    # Tests the /api/auth/makeLeader route.
    def test_makeLeader(self):
        u,f,u2 = load_user(True, True, True)
        token = u.generate_auth_token()

        # Test for invalid user id.
        post_body = '{"id":' + '""}'
        response = self.client.post('/api/auth/makeLeader',
                data=json.dumps({
                    'auth':{"email_or_token":token},
                    'body':post_body
                }),
                content_type='application/json')
        self.assertEqual(response.status_code, 404)

        # Test for valid user id.
        self.assertEqual(u2.role_id, Role.query.filter_by(name='User').first().id)
        post_body = '{"id":' + f'{u2.id}' + '}'
        response = self.client.post('/api/auth/makeLeader',
                data=json.dumps({
                    'auth':{"email_or_token":token},
                    'body':post_body
                }),
                content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(u2.role_id, Role.query.filter_by(name='Leader').first().id)
        self.assertEqual(response.get_json(),{'increased_privileges':f'{u2.username}'})

    # Tests the /api/auth/unmakeLeader route.
    def test_unmakeLeader(self):
        u,f,u2 = load_user(True, True, True)
        token = u.generate_auth_token()

        # Elevate u2 privaledges for test.
        u2.role = Role.query.filter_by(name='Leader').first()
        db.session.add(u2)
        db.session.commit()

        # Test for invalid user id.
        post_body = '{"id":' + '""}'
        response = self.client.post('/api/auth/unmakeLeader',
                data=json.dumps({
                    'auth':{"email_or_token":token},
                    'body':post_body
                }),
                content_type='application/json')
        self.assertEqual(response.status_code, 404)

        # Test for valid user id.
        post_body = '{"id":' + f'{u2.id}' + '}'
        response = self.client.post('/api/auth/unmakeLeader',
                data=json.dumps({
                    'auth':{"email_or_token":token},
                    'body':post_body
                }),
                content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(u2.role_id, Role.query.filter_by(name='User').first().id)
        self.assertEqual(response.get_json(),{'reduced_privileges':f'{u2.username}'})

    # Test the /api/auth/changeEmailRequest route.
    def test_sendChangeEmailRequest(self):
        u,f = load_user()
        token = u.generate_auth_token()

        # Test invalid email.
        post_body = '{"email":' + 'None' + '}'
        response = self.client.post('/api/auth/changeEmailRequest',
                data=json.dumps({
                    'auth':{"email_or_token":token},
                    'body':post_body
                }),
                content_type='application/json')
        self.assertEqual(response.status_code, 400)

        # Test valid email.
        post_body = '{"email":' + '"new_email"' + '}'
        response = self.client.post('/api/auth/changeEmailRequest',
                data=json.dumps({
                    'auth':{"email_or_token":token},
                    'body':post_body
                }),
                content_type='application/json')
        self.assertEqual(response.status_code, 200)

    # Test the /api/auth/confirmChangeEmail route.
    def test_confirmChangeEmail(self):
        u,f,u2 = load_user(True, True, True)

        # Test invalid token .
        token = 'Invalid'
        post_body = ''
        response = self.client.post(f'/api/auth/confirmChangeEmail/{token}',
        data=json.dumps({
                'auth':{"email_or_token":""},
                'body':post_body
            }),
            content_type='application/json')
        self.assertEqual(response.status_code, 401)

        # Test valid token.
        token = u.generate_email_token("new_email")
        post_body = ''
        response = self.client.post(f'/api/auth/confirmChangeEmail/{token}',
        data=json.dumps({
                'auth':{"email_or_token":""},
                'body':post_body
            }),
            content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(u.email,"new_email")

        # Test valid token, but unavailable email.
        token = u2.generate_email_token("new_email")
        post_body = ''
        response = self.client.post(f'/api/auth/confirmChangeEmail/{token}',
        data=json.dumps({
                'auth':{"email_or_token":""},
                'body':post_body
            }),
            content_type='application/json')
        self.assertEqual(response.status_code, 207)
        self.assertEqual(u2.email,"u2")

    # Test the /api/auth/createFamily route.
    def test_createFamily(self):
        u,f = load_user()
        token = u.generate_auth_token()

        # Test for invalid request.
        post_body = '{"familyName":""}'
        response = self.client.post('/api/auth/createFamily',
                data=json.dumps({
                    'auth':{"email_or_token":token},
                    'body':post_body
                }),
                content_type='application/json')
        self.assertEqual(response.status_code, 400)

        # Test for valid request.
        post_body = '{"familyName":' + '"new_family"}'
        response = self.client.post('/api/auth/createFamily',
                data=json.dumps({
                    'auth':{"email_or_token":token},
                    'body':post_body
                }),
                content_type='application/json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(u.family, Family.query.filter_by(family_name="new_family").first())

    # Test the /api/auth/changePassword route.
    def test_changePassword(self):
        u,f = load_user()
        token = u.generate_auth_token()

        # Test for invalid password.
        post_body = '{"oldPass":"bum_password","newPass":"new_pass"}'
        response = self.client.post('/api/auth/changePassword',
                data=json.dumps({
                    'auth':{"email_or_token":token},
                    'body':post_body
                }),
                content_type='application/json')
        self.assertEqual(response.status_code, 401)

        # Test for valid password.
        old_hash = u.password_hash
        post_body = '{"oldPass":"u","newPass":"new_pass"}'
        response = self.client.post('/api/auth/changePassword',
                data=json.dumps({
                    'auth':{"email_or_token":token},
                    'body':post_body
                }),
                content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(old_hash, u.password_hash)
        self.assertTrue(u.verify_password("new_pass"))
