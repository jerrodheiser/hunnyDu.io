from flask import jsonify, g, url_for, current_app, request
import ast # This will be used to turn a string literl into a usable list
from .. import db
from . import api
from ..models import Task, Subtask
import json
from .decorators import permission_required, leader_required, \
        login_required


# Route to get a user's tasks and family's tasks.
@api.route('/getTasks', methods=['GET', 'POST'])
@login_required
def get_tasks():
    tasks = g.current_user.tasks.order_by(Task.next_due.asc()).all()
    tz_offset = request.get_json()['tzOffset']
    if g.current_user.family:
        family_tasks = [task.to_json(tz_offset) for task in g.current_user.family.get_family_tasks()]
    else:
        family_tasks = []
    response = jsonify({
        'tasks':[task.to_json(tz_offset) for task in tasks],
        'familyTasks':family_tasks
        })
    response.status_code = 200
    return response


# Route to create a new task.
# Task is created first, then subtasks are created.
@api.route('/tasks', methods=['POST'])
@leader_required
def new_task():
    t_json = ast.literal_eval(request.json.get('body'))
    tz_offset = request.get_json()['tzOffset']
    task = Task.from_json(t_json. tz_offset)
    if task:
        db.session.add(task)
        db.session.commit()
        for subtask in ast.literal_eval(t_json['subtasks']):
            st = Subtask.from_json(subtask, task.id)
            db.session.add(st)
        db.session.commit()
        response = jsonify({'message':'Task added.'})
        response.status_code = 201
        return response
    else:
        response = jsonify({'errMessage':'Failed task generation.'})
        response.status_code = 400
        return response


# Route to mark/unmark a subtask as complete.
@api.route('/change_subtask_complete/<int:id>', methods=['POST'])
@login_required
def change_subtask_complete_subtask(id):
    st = Subtask.query.get_or_404(id)
    if st.is_complete:
        st.uncomplete()
    else:
        st.complete()
    response = jsonify({'message':'Subtask altered.'})
    response.status_code = 200
    return response


# Route to delete a subtask.
# Task is checked for completion upon subtask deletion.
# Response code 400 is sent if attempting to delete the only subtask.
@api.route('/delete_subtask/<int:id>', methods=['POST'])
@leader_required
def delete_subtask(id):
    st = Subtask.query.get_or_404(id)
    t = st.task
    if len(t.subtasks.all()) >= 2:
        db.session.delete(st)
        db.session.commit()
        t.determine_complete()
        response = jsonify({'message':'Subtask deleted.'})
        response.status_code = 200
        return response
    else:
        response = jsonify({"errMessage":"Cannot remove the only subtask."})
        response.status_code = 400
        return response


# Route to add a subtask.
# Response code 400 is sent if attempting to add more than 5 subtasks.
@api.route('/add_subtask/<int:id>',methods=['POST'])
@leader_required
def add_subtask(id):
    t = Task.query.get_or_404(id)
    if len(t.subtasks.all()) < 5:
        st_json = ast.literal_eval(request.json.get('body'))['subtask_name']
        st = Subtask.from_json(st_json, id)
        db.session.add(st)
        db.session.commit()
        response = jsonify({'message':'Subtask created.'})
        response.status_code = 200
        return response
    else:
        response = jsonify({"errMessage":"LImit of 5 subtasks."})
        response.status_code = 400
        return response


# Route to delete a task.
@api.route('/delete_task/<int:id>',methods=['POST'])
@leader_required
def delete_task(id):
    t = Task.query.get_or_404(id)
    t.delete()
    response =  jsonify({"message":"Task deleted."})
    response.status_code = 200
    return response
