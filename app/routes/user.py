"""User routes for managing user accounts and authentication in the application.

This module provides REST API endpoints for user operations including:
- User registration and authentication
- User profile management (create, read, update, delete)
- User search functionality
"""

from http import HTTPStatus
import sqlite3
from flask import Blueprint, jsonify, request
from marshmallow import ValidationError

from app.models.user import UserModel
from app.schemas.user import LoginSchema, UserSchema, UserUpdateSchema

user_bp = Blueprint('user', __name__)
user_model = UserModel()
user_schema = UserSchema()
user_update_schema = UserUpdateSchema()
login_schema = LoginSchema()

@user_bp.route('/')
def home():
    """Health check endpoint for the User Management System."""
    return jsonify({"message": "User Management System"}), HTTPStatus.OK

@user_bp.route('/users', methods=['GET'])
def get_all_users():
    """Retrieve all users from the system.

    Returns:
        tuple: JSON response containing list of users and HTTP status code
    """
    try:
        users = user_model.get_all_users()
        return jsonify(users), HTTPStatus.OK
    except (ValueError, KeyError) as e:
        return jsonify({"error": str(e)}), HTTPStatus.BAD_REQUEST
    except sqlite3.Error:
        return jsonify({"error": "Database error"}), HTTPStatus.INTERNAL_SERVER_ERROR

@user_bp.route('/user/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """Retrieve a specific user by their ID.

    Args:
        user_id (int): The ID of the user to retrieve

    Returns:
        tuple: JSON response containing user data and HTTP status code
    """
    try:
        user = user_model.get_user_by_id(user_id)
        if user:
            return jsonify(user), HTTPStatus.OK
        return jsonify({"error": "User not found"}), HTTPStatus.NOT_FOUND
    except (ValueError, KeyError) as e:
        return jsonify({"error": str(e)}), HTTPStatus.BAD_REQUEST
    except sqlite3.Error:
        return jsonify({"error": "Database error"}), HTTPStatus.INTERNAL_SERVER_ERROR

@user_bp.route('/users', methods=['POST'])
def create_user():
    """Create a new user in the system.

    Returns:
        tuple: JSON response containing result message and HTTP status code
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No input data provided"}), HTTPStatus.BAD_REQUEST

        validated_data = user_schema.load(data)
        user_id = user_model.create_user(
            validated_data['name'],
            validated_data['email'],
            validated_data['password']
        )

        return jsonify({
            "message": "User created successfully",
            "user_id": user_id
        }), HTTPStatus.CREATED
    except ValidationError as err:
        return jsonify({
            "error": "Validation error",
            "messages": err.messages
        }), HTTPStatus.BAD_REQUEST
    except sqlite3.IntegrityError:
        return jsonify({"error": "User with this email already exists"}), HTTPStatus.CONFLICT
    except sqlite3.Error:
        return jsonify({"error": "Database error"}), HTTPStatus.INTERNAL_SERVER_ERROR

@user_bp.route('/user/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    """Update an existing user's information.

    Args:
        user_id (int): The ID of the user to update

    Returns:
        tuple: JSON response containing result message and HTTP status code
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No input data provided"}), HTTPStatus.BAD_REQUEST

        validated_data = user_update_schema.load(data)
        success = user_model.update_user(
            user_id,
            validated_data['name'],
            validated_data['email']
        )

        if success:
            return jsonify({"message": "User updated successfully"}), HTTPStatus.OK
        return jsonify({"error": "User not found"}), HTTPStatus.NOT_FOUND
    except ValidationError as err:
        return jsonify({
            "error": "Validation error",
            "messages": err.messages
        }), HTTPStatus.BAD_REQUEST
    except sqlite3.IntegrityError:
        return jsonify({"error": "Email already in use"}), HTTPStatus.CONFLICT
    except sqlite3.Error:
        return jsonify({"error": "Database error"}), HTTPStatus.INTERNAL_SERVER_ERROR

@user_bp.route('/user/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    """Delete a user from the system.

    Args:
        user_id (int): The ID of the user to delete

    Returns:
        tuple: JSON response containing result message and HTTP status code
    """
    try:
        success = user_model.delete_user(user_id)
        if success:
            return jsonify({"message": "User deleted successfully"}), HTTPStatus.OK
        return jsonify({"error": "User not found"}), HTTPStatus.NOT_FOUND
    except sqlite3.Error:
        return jsonify({"error": "Database error"}), HTTPStatus.INTERNAL_SERVER_ERROR

@user_bp.route('/search', methods=['GET'])
def search_users():
    """Search for users by name.

    Returns:
        tuple: JSON response containing list of matching users and HTTP status code
    """
    try:
        name = request.args.get('name')
        if not name:
            return jsonify({"error": "Please provide a name to search"}), HTTPStatus.BAD_REQUEST

        users = user_model.search_users(name)
        return jsonify(users), HTTPStatus.OK
    except sqlite3.Error:
        return jsonify({"error": "Database error"}), HTTPStatus.INTERNAL_SERVER_ERROR

@user_bp.route('/login', methods=['POST'])
def login():
    """Authenticate user credentials.

    Returns:
        tuple: JSON response containing authentication result and HTTP status code
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No input data provided"}), HTTPStatus.BAD_REQUEST

        validated_data = login_schema.load(data)
        user = user_model.verify_login(
            validated_data['email'],
            validated_data['password']
        )

        if user:
            return jsonify({
                "status": "success",
                "user_id": user['id'],
                "message": "Login successful"
            }), HTTPStatus.OK

        return jsonify({
            "status": "failed",
            "error": "Invalid credentials"
        }), HTTPStatus.UNAUTHORIZED
    except ValidationError as err:
        return jsonify({
            "error": "Validation error",
            "messages": err.messages
        }), HTTPStatus.BAD_REQUEST
    except sqlite3.Error:
        return jsonify({"error": "Database error"}), HTTPStatus.INTERNAL_SERVER_ERROR
