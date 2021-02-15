from datetime import datetime
from flask import render_template, session, redirect, url_for, request,\
    current_app, abort, flash, make_response
from . import main
from .forms import TaskForm, SubtaskForm, EditProfileAdminForm
from .. import db
from ..models import User, Permission, Role, Task, Subtask, Family
from ..emails import send_email
from flask_login import current_user, login_required
from ..decorators import admin_required, permission_required

# Redirects to the login or dashboard.
@main.route('/',methods=['GET'])
def index():
    return redirect(url_for('auth.login'))


# URL to add a new task
# Subtasks will be added from the subject task's page
@main.route('/newtask',methods=['GET','POST'])
@permission_required(Permission.CREATE)
def new_task():
    form = TaskForm()
    if form.validate_on_submit():
        t = Task(
            taskname=form.taskname.data,
            period=form.period.data,
            assigned_user_id=form.assigned_user.data)
        db.session.add(t)
        db.session.commit()
        return redirect(url_for('main.task',id=t.id))
    return render_template('new_task.html',form=form)


# URL to add a new subtask, where the id is the task.id
@main.route('/newsubtask/<int:id>',methods=['GET','POST'])
@permission_required(Permission.CREATE)
def new_subtask(id):
    t = Task.query.get_or_404(id)
    form = SubtaskForm()
    if form.validate_on_submit():
        s = Subtask(subtask_name = form.subtask_name.data,task_id=t.id)
        db.session.add(s)
        db.session.commit()
        flash(f'New subtask for {t.taskname.upper()}')
        return redirect(url_for('main.task',id=t.id))
    return render_template('new_subtask.html',form=form,task=t)


# URL to run the completion script for completing a subtask.
@main.route('/completesubtask/<int:id>', methods=['GET'])
@permission_required(Permission.COMPLETE)
def complete_subtask(id):
    st = Subtask.query.get_or_404(id)
    st.complete()
    return redirect(url_for("main.task",id = st.task.id))

# Page to show a task and its associated subtasks.
@main.route('/task/<int:id>',methods=['GET','POST'])
def task(id):
    task = Task.query.get_or_404(id)
    return render_template('task.html',task=task, Subtask=Subtask)


# This page will show all tasks for member in the current_user's family
@main.route('/dashboard')
@login_required
def dashboard():
    tasks = Task.query.join(User, User.id == Task.assigned_user_id)\
            .filter(User.family_id == current_user.family_id).order_by(Task.next_due.asc()).all()
    return render_template('dashboard.html', tasks=tasks, today=datetime.today())


# This view function will be used to delete tasks from the database.
@main.route('/deletetask/<int:id>')
@permission_required(Permission.CREATE)
def delete_task(id):
    t = Task.query.get_or_404(id)
    for subtask in t.subtasks:
        db.session.delete(subtask)
    db.session.delete(t)
    db.session.commit()
    flash(f'{t.taskname} (assigned to {t.assigned_user.username}) was deleted.')
    return redirect(url_for('main.dashboard'))

# The view function to view someone profile and the tasks assigned to them.
@main.route('/user/<int:id>')
@login_required
def profile(id):
    user = User.query.get_or_404(id)
    return render_template('user.html',user = user,today=datetime.today())

# View function used to edit one's profile information.
@main.route('/edit_profile')
@login_required
def edit_profile():
    return render_template('/auth/change_info.html',user=current_user)

# View function used to administratively edit anyone's profile information.
@main.route('/edit_profile_admin/<int:id>',methods=['GET','POST'])
@admin_required
def edit_profile_admin(id):
    user = User.query.get_or_404(id)
    form = EditProfileAdminForm(user=user)
    if form.validate_on_submit():
        user.username = form.username.data
        user.confirmed = form.confirmed.data
        user.email = form.email.data
        user.role = Role.query.get_or_404(form.role.data)
        user.family = Family.query.get(form.family.data)
        db.session.add(user)
        db.session.commit()
        flash(f'{user.username}\'s profile was saved.')
        return redirect(url_for('main.profile',id = user.id))
    form.username.data = user.username
    form.confirmed.data = user.confirmed
    form.email.data = user.email
    form.role.data = user.role_id
    form.family.data = user.family_id
    return render_template('/auth/edit_profile_admin.html',form=form,user=user)
