import unittest
import time
from app import create_app, db
from app.models import User, Role, Permission, Task, Subtask, Family
from datetime import datetime, timedelta, date

def is_date(date1, date2):
    if date1.day == date2.day and\
        date1.month == date2.month and\
        date1.year == date2.year:
        return True
    else:
        return False

# Test the user model.
class TaskModelTestCase(unittest.TestCase):


    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        Role.insert_roles()
        f = Family(family_name='f')
        db.session.add(f)
        db.session.commit()
        u1 = User(username='u1',family=f)
        u2 = User(username='u2', family=f)
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    # tests is_date()
    def test_is_date(self):
        today = datetime.today()
        tomorrow = today+timedelta(days=1)
        next_month = today+timedelta(days=31)
        next_year = today+timedelta(days=366)
        self.assertTrue(is_date(today,today))
        self.assertFalse(is_date(today,tomorrow))
        self.assertFalse(is_date(today,next_month))
        self.assertFalse(is_date(today,next_year))

    # Tests task generation for assigning due dates.
    def test_task_init(self):
        # daily
        t = Task(period='d')
        self.assertTrue(is_date(t.next_due,datetime.today()))

        # weekly
        t = Task(period='w')
        delta = t.next_due - datetime.today()
        self.assertTrue(t.next_due.weekday() == 5)
        self.assertTrue(delta.days < 7)
        self.assertTrue(delta.days >= 0)

        # monthly
        today = datetime(month=1,day=1,year=2000)
        t = Task(period='m',today = today)
        self.assertTrue(is_date(t.next_due,today))

        today = datetime(month=1,day=2,year=2000)
        t = Task(period='m',today = today)
        self.assertTrue(is_date(t.next_due,today.replace(month=2,day=1)))

        today = datetime(month=12,day=2,year=2000)
        t = Task(period='m',today = today)
        self.assertTrue(is_date(t.next_due,datetime(day=1,month=1,year=2001)))

    # Tests updating due dates.
    def test_update_next_due(self):
        # Daily
        t = Task(period='d')
        t.update_next_due()
        self.assertTrue(is_date(t.next_due,datetime.today() + timedelta(days=1)))
        t.update_next_due()
        self.assertTrue(is_date(t.next_due,datetime.today() + timedelta(days=1)))

        # Weekly
        t = Task(period='w')
        t.update_next_due()
        delta = t.next_due - datetime.today()
        self.assertTrue(t.next_due.weekday() == 5)
        self.assertTrue(delta.days >= 7)
        self.assertTrue(delta.days < 14)
        t.update_next_due()
        delta = t.next_due - datetime.today()
        self.assertTrue(t.next_due.weekday() == 5)
        self.assertTrue(delta.days >= 7)
        self.assertTrue(delta.days < 14)

        # Monthly
        t = Task(period='m')
        t.update_next_due()
        if datetime.today().month == 12:
            should_be = datetime.today().replace(day=1,month=2,year=datetime.today().year + 1)
        elif datetime.today().month ==11:
            should_be = datetime.today().replace(day=1,month=1,year=datetime.today().year + 1)
        else:
            should_be = datetime.today().replace(day=1,month=datetime.today().month + 1)
        self.assertTrue(is_date(t.next_due,should_be),f'{t.next_due} &-& {should_be}')
        t.update_next_due()
        self.assertTrue(is_date(t.next_due,should_be))

        # Edge monthly cases
        today = datetime(month=11,day=10,year=2020)
        t = Task(period='m',today=today)
        db.session.add(t)
        db.session.commit()
        t.update_next_due(today=today)
        should_be = datetime(day=1,month=1,year=2021)
        self.assertTrue(is_date(t.next_due,should_be),t.next_due)
        t.update_next_due(today=today)
        self.assertTrue(is_date(t.next_due,should_be))

        today = datetime(month=12,day=10,year=2020)
        t = Task(period='m',today=today)
        db.session.add(t)
        db.session.commit()
        t.update_next_due(today=today)
        should_be = datetime(day=1,month=2,year=2021)
        self.assertTrue(is_date(t.next_due,should_be),t.next_due)
        t.update_next_due(today=today)
        self.assertTrue(is_date(t.next_due,should_be),f'{t.next_due} *** {should_be}')



    # Test Task and Subtask completion methods.
    def test_completion(self):
        t = Task(period='d')
        db.session.add(t)
        db.session.commit()
        s1 = Subtask(task_id=t.id)
        s2 = Subtask(task_id=t.id)
        db.session.add(s1)
        db.session.add(s2)
        db.session.commit()
        first_due = t.next_due

        # Completing one subtask
        self.assertFalse(s1.is_complete)
        self.assertFalse(s2.is_complete)
        s1.complete()
        self.assertTrue(s1.is_complete)
        self.assertFalse(s2.is_complete)
        self.assertTrue(is_date(t.next_due,first_due))

        # Completing both subtasks
        s2.complete()
        self.assertFalse(s1.is_complete)
        self.assertFalse(s2.is_complete)
        self.assertFalse(is_date(t.next_due,first_due))
