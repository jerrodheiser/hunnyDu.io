from ..models import User
from flask import jsonify, url_for
from . import api


# Route to return a users information.
@api.route('/users/<int:id>', methods=['POST'])
def get_user(id):
    user = User.query.get_or_404(id)
    if user:
        response = jsonify(user.to_json())
        response.status_code = 200
        return response
