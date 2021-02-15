import unittest
import time
from app import create_app, db
from app.models import User, Role, Permission, AnonymousUser, Family

# Test the user model.
class UserModelTestCase(unittest.TestCase):

    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        Role.insert_roles()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    # Tests default family_id
    def user_assign(self):
        u = User()
        assertTrue(u.family_id==None)

    # Tests adding a member to a family
    def add_member(self):
        u = User()
        f = Family()
        db.session.add(f)
        db.session.add(u)
        db.session.commit()

        f.add_member(u)
        assertTrue(u.family.id==f.id)
