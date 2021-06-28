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


    # General add user function to simplify code.
    def add_user(self):
        r = Role.query.filter_by(name='User').first()
        self.assertIsNotNone(r)
        u = User(email='john@example.com',role=r,password='cat',confirmed=True)
        db.session.add(u)
        db.session.commit()

    # Test api authorization.
    def test_no_auth(self):
        # Test no credentials
        response = self.client.get('/api/v1/comments/',
        content_type='application/json')
        self.assertEqual(response.status_code,401)

        # Add unconfirmed user
        r = Role.query.filter_by(name='User').first()
        self.assertIsNotNone(r)
        u = User(email='john@example.com',role=r,password='cat',confirmed=False)
        db.session.add(u)
        db.session.commit()

        response = self.client.get(
            '/api/v1/posts/',
            headers = self.get_api_headers('john@example.com','cat'))
        self.assertEqual(response.status_code,403)

    # This tests writing and getting posts
    def test_posts(self):
        self.add_user()
        response = self.client.post(
            '/api/v1/posts/',
            headers = self.get_api_headers('john@example.com','cat'),
            data = json.dumps({'body':'body of the blog post'}))
        self.assertEqual(response.status_code,201)
        url = response.headers.get('Location')
        self.assertIsNotNone(url)

        # Get all posts.
        response = self.client.get(
        '/api/v1/posts/',
        headers = self.get_api_headers('john@example.com','cat'))
        self.assertEqual(response.status_code,200)

        # Get post by id.
        response = self.client.get(
            url,
            headers = self.get_api_headers('john@example.com','cat'))
        self.assertEqual(response.status_code,200)
        json_response = json.loads(response.get_data(as_text=True))
        self.assertEqual('http://localhost' + json_response['url'],url)
        self.assertEqual(json_response['body'],'body of the blog post')
        self.assertEqual(json_response['body_html'],
            '<p>body of the blog post</p>')

        # Change the subject post.
        response = self.client.put(
            url,
            headers = self.get_api_headers('john@example.com','cat'),
            data = json.dumps({'body':'new body'}))
        self.assertEqual(response.status_code,204)
        self.assertEqual(response.headers.get('Location'),url)
        self.assertEqual(response.headers.get('newBody'),'new body')

        # Attempt to change the subject post when not the author.
        r = Role.query.filter_by(name='User').first()
        self.assertIsNotNone(r)
        u = User(email='peggy@example.com',role=r,password='cat',confirmed=True)
        db.session.add(u)
        db.session.commit()
        response = self.client.put(
            url,
            headers = self.get_api_headers('peggy@example.com','cat'),
            data = json.dumps({'body':'new body'}))
        self.assertEqual(response.status_code,403)


    # Test the token functions.
    def test_auth_token(self):
        self.add_user()

        # Get the token.
        response = self.client.post(
            '/api/v1/tokens/',
            headers = self.get_api_headers('john@example.com','cat')
            )
        json_response = json.loads(response.get_data(as_text=True))
        token = json_response['token']

        # Now to use it to access the posts page
        response = self.client.get(
            '/api/v1/posts/',
            headers = self.get_api_headers(token,'')
            )
        self.assertEqual(response.status_code,200)

        # This will make sure you cannot use a token to get a token
        response = self.client.post(
            '/api/v1/tokens/',
            headers = self.get_api_headers(token,'')
            )
        self.assertEqual(response.status_code,401)


    # This will test the comment section of the api.
    def test_comment(self):
        self.add_user()

        # First to write a post to comment on
        response = self.client.post(
            '/api/v1/posts/',
            headers = self.get_api_headers('john@example.com','cat'),
            data = json.dumps({'body':'body of the blog post'}))
        self.assertEqual(response.status_code,201)
        url = response.headers.get('Location') + '/comments/'
        self.assertIsNotNone(url)

        # Test writing comments
        response = self.client.post(
            url,
            headers = self.get_api_headers('john@example.com','cat'),
            data = json.dumps({'body':'comment body'})
            )
        self.assertEqual(response.status_code,201)
        url = response.headers.get('Location')

        # Test getting comments
        response = self.client.get(
            '/api/v1/comments/',
            headers = self.get_api_headers('john@example.com','cat'))
        self.assertEqual(response.status_code,200)

        # Testing getting specific comments
        response = self.client.get(
            url,
            headers = self.get_api_headers('john@example.com','cat')
            )
        self.assertEqual(response.status_code,200)
        json_response = json.loads(response.get_data(as_text=True))
        self.assertEqual(json_response['body'],'comment body')


    # This will test the user api functions.
    def test_user(self):
        self.add_user()
        u = User.query.filter_by(email='john@example.com').first()

        # get the user's page
        response = self.client.get(
            f'/api/v1/users/{u.id}',
            headers = self.get_api_headers('john@example.com','cat')
            )
        self.assertEqual(response.status_code,200)

        # Create a post from the user
        response = self.client.post(
            '/api/v1/posts/',
            headers = self.get_api_headers('john@example.com','cat'),
            data = json.dumps({'body':'body of the blog post'}))
        self.assertEqual(response.status_code,201)

        # get the post
        response = self.client.get(
            f'/api/v1/users/{u.id}/posts/',
            headers = self.get_api_headers('john@example.com','cat')
            )
        json_response = json.loads(response.get_data(as_text=True))
        self.assertEqual(json_response['posts'][0]['body'],'body of the blog post')

        # get the users timeline, which should have their post
        response = self.client.get(
            f'/api/v1/users/{u.id}/timeline/',
            headers = self.get_api_headers('john@example.com','cat')
            )
        json_response = json.loads(response.get_data(as_text=True))
        self.assertEqual(json_response['posts'][0]['body'],'body of the blog post')
