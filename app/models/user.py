"""
This module defines the UserModel class for interacting with a SQLite database
to manage user data, including creation, retrieval, updating, deletion,
searching, and login verification. It uses bcrypt for password hashing.
Author: Raj Kariya
"""
import sqlite3
from app import bcrypt

class UserModel:
    """UserModel is responsible for interacting with the SQLite database
    to perform CRUD operations on user data."""
    def __init__(self, db_path='users.db'):
        """
        Initializes the UserModel with the specified database path.

        Args:
            db_path (str): The path to the SQLite database file. Defaults to 'users.db'.
        """
        self.db_path = db_path

    def get_connection(self):
        """
        Establishes and returns a connection to the SQLite database.
        The connection is configured to return rows as dictionaries.

        Returns:
            sqlite3.Connection: A database connection object.
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def get_all_users(self):
        """
        Retrieves all users from the database, excluding their passwords.

        Returns:
            list: A list of dictionaries, where each dictionary represents a user
                  with 'id', 'name', and 'email' fields. Returns an empty list
                  if no users are found.
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, email FROM users")
            return [dict(row) for row in cursor.fetchall()]

    def get_user_by_id(self, user_id):
        """
        Retrieves a single user by their ID, excluding their password.

        Args:
            user_id (int): The ID of the user to retrieve.

        Returns:
            dict or None: A dictionary representing the user with 'id', 'name',
                          and 'email' fields if found, otherwise None.
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, email FROM users WHERE id = ?", (user_id,))
            user = cursor.fetchone()
            return dict(user) if user else None

    def create_user(self, name, email, password):
        """
        Creates a new user in the database with a hashed password.

        Args:
            name (str): The name of the user.
            email (str): The email address of the user (should be unique).
            password (str): The plain-text password of the user.

        Returns:
            int: The ID of the newly created user.
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
            cursor.execute(
                "INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
                (name, email, hashed_password)
            )
            conn.commit()
            return cursor.lastrowid

    def update_user(self, user_id, name, email):
        """
        Updates the name and email of an existing user.

        Args:
            user_id (int): The ID of the user to update.
            name (str): The new name for the user.
            email (str): The new email address for the user.

        Returns:
            bool: True if the user was updated successfully, False otherwise.
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE users SET name = ?, email = ? WHERE id = ?",
                (name, email, user_id)
            )
            conn.commit()
            return cursor.rowcount > 0

    def delete_user(self, user_id):
        """
        Deletes a user from the database by their ID.

        Args:
            user_id (int): The ID of the user to delete.

        Returns:
            bool: True if the user was deleted successfully, False otherwise.
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
            conn.commit()
            return cursor.rowcount > 0

    def search_users(self, name):
        """
        Searches for users whose names contain the given substring (case-insensitive).

        Args:
            name (str): The substring to search for in user names.

        Returns:
            list: A list of dictionaries, where each dictionary represents a user
                  with 'id', 'name', and 'email' fields. Returns an empty list
                  if no matching users are found.
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, name, email FROM users WHERE name LIKE ?",
                (f"%{name}%",)
            )
            return [dict(row) for row in cursor.fetchall()]

    def verify_login(self, email, password):
        """
        Verifies a user's login credentials (email and password).

        Args:
            email (str): The email address of the user attempting to log in.
            password (str): The plain-text password provided by the user.

        Returns:
            dict or None: A dictionary representing the user (including all fields
                          from the database, including hashed password) if credentials
                          are valid, otherwise None.
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
            user = cursor.fetchone()
            if user and bcrypt.check_password_hash(user['password'], password):
                return dict(user)
            return None
