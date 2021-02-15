import unittest
import time
from app import create_app, db
from app.models import User, Role, Permission, AnonymousUser

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

    # This test verifies the password is only set by the password setter.
    def test_password_setter(self):
        u = User()
        self.assertTrue(u.password_hash is None)
        u.password = 'x'
        self.assertTrue(u.password_hash is not None)

    # Test that password cannot be read.
    def test_no_password_getter(self):
        u = User(password='x')
        with self.assertRaises(AttributeError):
            u.password

    # Test password verification.
    def test_password_verification(self):
        u = User(password='x')
        self.assertTrue(u.verify_password('x'))
        self.assertFalse(u.verify_password('nope'))

    # Test that password hashes are unique.
    def test_unique_hash(self):
        u=User(password='x')
        u2=User(password='x')
        self.assertFalse(u.password_hash == u2.password_hash)

    # Test confirm tokens.
    def test_confirm_tokens(self):
        u = User(password='x',email='confm_tok1@example.com')
        db.session.add(u)
        db.session.commit()
        token = u.generate_email_token(email='confm_tok2@example.com')
        self.assertTrue(u.confirm_email(token)[0])

    # Test expired tokens.
    def test_expired_tokens(self):
        u = User(password='x',email='expir_tok1@example.com')
        u2 = User(password='x',email='expir_tok2@example.com')
        db.session.add(u,u2)
        db.session.commit()
        token = u.generate_email_token(email=u.email,expires_in=1)
        time.sleep(2)
        self.assertFalse(u.confirm_email(token)[0])

    # Test invalid tokens.
    def test_invalid_tokens(self):
        u = User(password='x',email='inval_tok1@example.com')
        u2 = User(password='x',email='inval_tok2@example.com')
        db.session.add(u,u2)
        db.session.commit()
        token = u.generate_email_token(email=u.email)
        self.assertFalse(u2.confirm_email(token)[0])

    # Test that users are assigned default as role.
    def test_default_role(self):
        u = User()
        self.assertTrue(u.role == Role.query.filter_by(default=True).first())

    # Test user permissions.
    def test_user_permissions(self):
        u = User(role=Role.query.filter_by(name='User').first())
        self.assertTrue(u.can(Permission.COMPLETE))

    # Test moderator permissions.
    def test_leader_permissions(self):
        u = User(role=Role.query.filter_by(name='Leader').first())
        self.assertTrue(u.can(Permission.COMPLETE))
        self.assertTrue(u.can(Permission.CREATE))
        self.assertTrue(u.can(Permission.ADD_USER))

    # Test admin permissions.
    def test_admin_permissions(self):
        u = User(role=Role.query.filter_by(name='Administrator').first())
        self.assertTrue(u.can(Permission.COMPLETE))
        self.assertTrue(u.can(Permission.CREATE))
        self.assertTrue(u.can(Permission.ADMIN))
        self.assertTrue(u.can(Permission.ADD_USER))

    # Test anonymous permissions.
    def test_anonymous_permissions(self):
        u = AnonymousUser()
        self.assertFalse(u.can(Permission.COMPLETE))
        self.assertFalse(u.can(Permission.CREATE))
        self.assertFalse(u.can(Permission.ADD_USER))
        self.assertFalse(u.can(Permission.ADMIN))
