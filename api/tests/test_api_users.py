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


    # Test the /api/users/int route.
    def test_get_user(self):
        u,f = load_user(True, True)

        # Test for invalid id.
        response = self.client.post('/api/users/0',
                data=json.dumps({
                    'auth':
                        {"email_or_token":''}
                    }),
                content_type='application/json')
        self.assertEqual(response.status_code, 404)

        # Test for invalid id.
        response = self.client.post(f'/api/users/{u.id}',
                data=json.dumps({
                    'auth':
                        {"email_or_token":''}
                    }),
                content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()['username'], u.username)
