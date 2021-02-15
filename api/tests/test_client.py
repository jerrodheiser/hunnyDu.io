import unittest
import re
from app import create_app, db
from app.models import User, Role, Task
from flask import url_for

class FlaskClientTestCase(unittest.TestCase):

    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        Role.insert_roles()
        self.client = self.app.test_client(use_cookies=True)

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    # This tests the homepage.
    def test_home_page(self):
        response = self.client.get('/',follow_redirects=True)
        self.assertEqual(response.status_code,200)
        self.assertTrue('New user?' in response.get_data(as_text=True))

    # Test registering and logging in.
    def test_register_and_use(self):
        # Create an account
        response = self.client.post('/auth/register',data={
            'email':'john@example.com',
            'username':'John',
            'password':'cat',
            'password2':'cat'
        })
        self.assertEqual(response.status_code,302)

        # log in with the new account
        response = self.client.post('/auth/login',data = {
            'email':'john@example.com',
            'password':'cat'
            },follow_redirects=True)
        self.assertEqual(response.status_code,200)
        self.assertTrue('You have not confirmed' in response.get_data(as_text=True))

        # send confirmation token
        user = User.query.filter_by(email='john@example.com').first()
        token = user.generate_confirmation_token()
        response = self.client.get(f'/auth/confirm/{token}',follow_redirects=True)
        self.assertEqual(response.status_code,200)
        self.assertTrue('User email confirmed.' in response.get_data(as_text=True))

        # Create a family
        response = self.client.get('/',follow_redirects=True)
        self.assertTrue('Not part of a family?' in response.get_data(as_text=True), response.get_data(as_text=True))
        response = self.client.get('/auth/createfamily',follow_redirects=True)
        self.assertEqual(response.status_code,200)
        response = self.client.get('/auth/joinfamily',follow_redirects=True)
        self.assertEqual(response.status_code,200)
        response = self.client.post('/auth/createfamily', data={
            'family_name': 'John Family'
        })
        self.assertEqual(response.status_code,302)
        response = self.client.get('/dashboard')
        self.assertTrue('John Family' in response.get_data(as_text=True))

        # Create a task, verify it shows on the dashboard
        response = self.client.get('/newtask',follow_redirects=True)
        self.assertEqual(response.status_code,200)
        response = self.client.post('/newtask',data = {
                'taskname': 'New Task',
                'period': 'w',
                'assigned_user': User.query.filter_by(username='John').first().id})
        response = self.client.get('/dashboard')
        self.assertTrue('New Task' in response.get_data(as_text=True))
        response = self.client.get(f'/task/{Task.query.filter_by(taskname="New Task").first().id}')
        self.assertEqual(response.status_code,200)

        # Create a subtask
        response = self.client.get(f'/newsubtask/{Task.query.filter_by(taskname="New Task").first().id}')
        self.assertEqual(response.status_code,200)
        response = self.client.post(f'/newsubtask/{Task.query.filter_by(taskname="New Task").first().id}',
                data = {'subtask_name': 'New Subtask'})
        response = self.client.get(f'/newsubtask/{Task.query.filter_by(taskname="New Task").first().id}')
        self.assertTrue('New Subtask' in response.get_data(as_text=True))

        # Delete a Task
        response = self.client.get(f'/deletetask/{Task.query.filter_by(taskname="New Task").first().id}')
        self.assertFalse('New Task' in response.get_data(as_text=True))

        # logout
        response = self.client.get('/auth/logout',follow_redirects=True)
        self.assertEqual(response.status_code,200)
        self.assertTrue('You have been logged out.' in response.get_data(as_text=True))
