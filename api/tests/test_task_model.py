import unittest
import time
from app import create_app, db
from app.models import User, Role, Permission, Task, Subtask, Family
from datetime import datetime, timedelta, date

# Function for equating dates (excludes times)
def is_date(date1, date2):
    if date1.day == date2.day and\
        date1.month == date2.month and\
        date1.year == date2.year:
        return True
    else:
        return False

# Function for loading tasks.
def load_tasks():
    f = Family(family_name='f')
    db.session.add(f)
    db.session.commit()
    u = User(username='u',family=f)
    db.session.add(u)
    db.session.commit()
    td = Task(taskname='daily',period='d', assigned_user=u)
    tw = Task(taskname='weekly',period='w', assigned_user=u)
    tm = Task(taskname='monthly',period='m', assigned_user=u)
    db.session.add(td)
    db.session.add(tw)
    db.session.add(tm)
    db.session.commit()
    return td,tw,tm

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

    # Tests is_date()
    def test_is_date(self):
        self.assertTrue(is_date(datetime(month=1,day=1, year=2000),
                                datetime(month=1,day=1, year=2000)))
        self.assertFalse(is_date(datetime(month=1,day=1, year=2000),
                                datetime(month=2,day=1, year=2000)))
        self.assertFalse(is_date(datetime(month=1,day=1, year=2000),
                                datetime(month=1,day=2, year=2000)))
        self.assertFalse(is_date(datetime(month=1,day=1, year=2000),
                                datetime(month=1,day=1, year=2001)))

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

    # Tests update_next_due.
    def test_update_next_due(self):
        td,tw,tm = load_tasks()

        # Test daily task td
        # Completed on day due
        td.next_due = datetime(month=1, day=1, year=2021)
        sim_day = datetime(month=1, day=1, year=2021)
        td.update_next_due(today=sim_day)
        self.assertTrue(is_date(td.next_due,datetime(month=1, day=2, year=2021)))

        # Completed a day early
        td.next_due = datetime(month=1, day=2, year=2021)
        sim_day = datetime(month=1, day=1, year=2021)
        td.update_next_due(today=sim_day)
        self.assertTrue(is_date(td.next_due,datetime(month=1, day=2, year=2021)))

        # Completed if overdue by one day
        td.next_due = datetime(month=1, day=1, year=2021)
        sim_day = datetime(month=1, day=2, year=2021)
        td.update_next_due(today=sim_day)
        self.assertTrue(is_date(td.next_due,datetime(month=1, day=3, year=2021)))

        # Completed if overdue by 3 days
        td.next_due = datetime(month=1, day=1, year=2021)
        sim_day = datetime(month=1, day=4, year=2021)
        td.update_next_due(today=sim_day)
        self.assertTrue(is_date(td.next_due,datetime(month=1, day=5, year=2021)))


        # Test weekly task tw
        # Completed during week due
        tw.next_due = datetime(month=1, day=8, year=2021)
        sim_day = datetime(month=1, day=4, year=2021)
        tw.update_next_due(today=sim_day)
        self.assertTrue(is_date(tw.next_due,datetime(month=1, day=15, year=2021)))

        # Completed on saturday before due
        tw.next_due = datetime(month=1, day=8, year=2021)
        sim_day = datetime(month=1, day=2, year=2021)
        tw.update_next_due(today=sim_day)
        self.assertTrue(is_date(tw.next_due,datetime(month=1, day=15, year=2021)))

        # Completed a week early
        tw.next_due = datetime(month=1, day=8, year=2021)
        sim_day = datetime(month=1, day=1, year=2021)
        tw.update_next_due(today=sim_day)
        self.assertTrue(is_date(tw.next_due,datetime(month=1, day=8, year=2021)))

        # Completed at the end of a month
        tw.next_due = datetime(month=1, day=29, year=2021)
        sim_day = datetime(month=1, day=26, year=2021)
        tw.update_next_due(today=sim_day)
        self.assertTrue(is_date(tw.next_due,datetime(month=2, day=5, year=2021)))

        # Completion results in shifting the year by one
        tw.next_due = datetime(month=12, day=25, year=2020)
        sim_day = datetime(month=12, day=23, year=2020)
        tw.update_next_due(today=sim_day)
        self.assertTrue(is_date(tw.next_due,datetime(month=1, day=1, year=2021)))

        # Due date is in next year, completion date is a year behind
        tw.next_due = datetime(month=1, day=1, year=2021)
        sim_day = datetime(month=12, day=31, year=2020)
        tw.update_next_due(today=sim_day)
        self.assertTrue(is_date(tw.next_due,datetime(month=1, day=8, year=2021)))

        # Completed if overdue by less than a week
        tw.next_due = datetime(month=1, day=8, year=2021)
        sim_day = datetime(month=1, day=9, year=2021)
        tw.update_next_due(today=sim_day)
        self.assertTrue(is_date(tw.next_due,datetime(month=1, day=22, year=2021)))

        # Completed if overdue for 3 weeks
        tw.next_due = datetime(month=1, day=8, year=2021)
        sim_day = datetime(month=1, day=31, year=2021)
        tw.update_next_due(today=sim_day)
        self.assertTrue(is_date(tw.next_due,datetime(month=2, day=12, year=2021)))


        # Test monthly task tm
        # Completed earlier in the month
        tm.next_due = datetime(month=2, day=1, year=2021)
        sim_day = datetime(month=1, day=1, year=2021)
        tm.update_next_due(today=sim_day)
        self.assertTrue(is_date(tm.next_due,datetime(month=3, day=1, year=2021)))

        # Completed a month early
        tm.next_due = datetime(month=3, day=1, year=2021)
        sim_day = datetime(month=1, day=31, year=2021)
        tm.update_next_due(today=sim_day)
        self.assertTrue(is_date(tm.next_due,datetime(month=3, day=1, year=2021)))

        # Completed if overdue by less than a month
        tm.next_due = datetime(month=1, day=1, year=2021)
        sim_day = datetime(month=1, day=31, year=2021)
        tm.update_next_due(today=sim_day)
        self.assertTrue(is_date(tm.next_due,datetime(month=3, day=1, year=2021)))

        # Completed if overdue for 3 months
        tm.next_due = datetime(month=1, day=1, year=2021)
        sim_day = datetime(month=4, day=12, year=2021)
        tm.update_next_due(today=sim_day)
        self.assertTrue(is_date(tm.next_due,datetime(month=6, day=1, year=2021)))

        # Completed at the end of a year
        tm.next_due = datetime(month=12, day=1, year=2020)
        sim_day = datetime(month=11, day=25, year=2020)
        tm.update_next_due(today=sim_day)
        self.assertTrue(is_date(tm.next_due,datetime(month=1, day=1, year=2021)))

        # Completed late at the end of a year
        tm.next_due = datetime(month=11, day=1, year=2020)
        sim_day = datetime(month=11, day=24, year=2020)
        tm.update_next_due(today=sim_day)
        self.assertTrue(is_date(tm.next_due,datetime(month=1, day=1, year=2021)))

        # Completed over a year late
        tm.next_due = datetime(month=11, day=1, year=2020)
        sim_day = datetime(month=12, day=24, year=2021)
        tm.update_next_due(today=sim_day)
        self.assertTrue(is_date(tm.next_due,datetime(month=2, day=1, year=2022)))


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
