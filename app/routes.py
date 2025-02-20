from flask import Blueprint, request, jsonify
from .models import User
from .auth import auth
from .errors import notFoundError, badRequestError
from . import db

main = Blueprint('main', __name__)

@main.route('/users', methods=['POST'])
def createUser():
    data = request.get_json()
    if not data or not 'username' in data or not 'email' in data:
        return badRequestError('Missing username or email')
    
    newUser = User(username=data['username'], email=data['email'])
    db.session.add(newUser)
    db.session.commit()
    return jsonify({'message': 'User created'}), 201

@main.route('/users', methods=['GET'])
@auth.login_required
def getUsers():
    users = User.query.all()
    if len(users) == 0:
        return notFoundError('No users found')
    return jsonify([{'id':user.id, 'username': user.username, 'email': user.email} for user in users])

@main.route('/users/<int:id>', methods=['GET'])
@auth.login_required
def getUser(id):
    user = db.session.get(User, id)
    if not user:
        return notFoundError('User not found')
    return jsonify({'username': user.username, 'email': user.email})

@main.route('/users/<int:id>', methods=['PUT'])
def updateUser(id):
    user = db.session.get(User, id)
    if not user:
        return notFoundError('User not found')
    data = request.get_json()
    if not data or not 'username' in data or not 'email' in data:
        return badRequestError('Missing username or email')
    user.username = data['username']
    user.email = data['email']
    db.session.commit()
    return jsonify({'message': 'User updated'}), 200

@main.route('/users/<int:id>', methods=['DELETE'])
def deleteUser(id):
    user = db.session.get(User, id)
    if not user:
        return notFoundError('User not found')
    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': 'User deleted'}), 200