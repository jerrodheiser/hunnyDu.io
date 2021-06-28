import unittest
import re
from base64 import b64encode
import json
from flask import url_for
from app import create_app, db
from app.models import User, Role

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

    # Test verification of user credentials.
    def test_login(self):
        u = User(username="u", password="u", confirmed=True)
        db.session.add(u)
        db.session.commit()

        # No username or password
        response = self.client.post('/api/auth/login', data={
            'auth':{"email_or_token":None, "password":None}})
        self.assertEqual(response.status_code, 400)

        # Invalid username/password combo
        response = self.client.post('/api/auth/login', data={
            'auth':{"email_or_token":"u", "password":"f"}})
        self.assertEqual(response.status_code, 401)

        # Valid username/password combo, no family assigned
        response = self.client.post('/api/auth/login', data={
            'auth':{"email_or_token":"u", "password":"u"}})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response)['family_name'],'')
        self.assertEqual(json.loads(response)['family_id'],'')
        self.assertEqual(json.loads(response)['members'],[])
        self.assertEqual(json.loads(response)['leaders'],0)

        # Assign user a family
        f = Family(family_name='f')
        db.session.add(f)
        db.session.commit()
        u.family = f
        db.session.add(u)
        db.session.commit()

        # Valid username/password combo, no family assigned
        response = self.client.post('/api/auth/login', data={
            'auth':{"email_or_token":"u", "password":"u"}})
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(json.loads(response)['family_name'],'')
        self.assertNotEqual(json.loads(response)['family_id'],'')
        self.assertNotEqual(json.loads(response)['members'],[])
        self.assertNotEqual(json.loads(response)['leaders'],0)
