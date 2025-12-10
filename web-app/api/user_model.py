import os

import bcrypt
from mongomock import DuplicateKeyError
from pymongo import MongoClient


MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("MONGO_DB_NAME")

client = MongoClient(MONGO_URI)
db = client[DB_NAME]


def create_user(email, password, name):
    """Create a new user with full structure.
    Returns the inserted user or None if already exists."""

    # Hash password
    hashed_pw = bcrypt.hashpw(
        password.encode(), bcrypt.gensalt()
    ).decode()  # store as string

    new_user = {
        "name": name,
        "netid": email.split("@")[0],
        "email": email,
        "password": hashed_pw,  # store hashed password
        "year": "",
        "major": "",
        "interests": [],
        "completed_courses": [],
        "planned_semesters": [],
    }

    try:
        db.students.insert_one(new_user)
        return new_user
    except DuplicateKeyError:
        return None


def verify_user(email, password):
    user = db.students.find_one({"email": email})
    if not user:
        return None

    # Check hashed password
    if not bcrypt.checkpw(password.encode(), user["password"].encode()):
        return None

    return user


def get_user_by_email(email):
    """
    Get user by email (without password verification).

    Args:
        email: User's email address

    Returns:
        User dictionary or None if not found
    """
    return db.students.find_one({"email": email})


def update_user_profile(email, updates):
    """
    Update user profile fields.

    Args:
        email: User's email
        updates: Dictionary of fields to update (e.g., {"major": "CS", "year": "Sophomore"})

    Returns:
        True if successful, False otherwise
    """
    try:
        result = db.students.update_one({"email": email}, {"$set": updates})
        return result.modified_count > 0
    except Exception as e:
        print(f"Error updating user profile: {e}")
        return False


def add_completed_course(email, course_code):
    """
    Add a course to user's completed courses list.

    Args:
        email: User's email
        course_code: Course code to add

    Returns:
        True if successful, False otherwise
    """
    try:
        result = db.students.update_one(
            {"email": email},
            {
                "$addToSet": {"completed_courses": course_code}
            },  # $addToSet prevents duplicates
        )
        return result.modified_count > 0 or result.matched_count > 0
    except Exception as e:
        print(f"Error adding completed course: {e}")
        return False


def remove_completed_course(email, course_code):
    """
    Remove a course from user's completed courses list.

    Args:
        email: User's email
        course_code: Course code to remove

    Returns:
        True if successful, False otherwise
    """
    try:
        result = db.students.update_one(
            {"email": email},
            {"$pull": {"completed_courses": course_code}},
        )
        return result.modified_count > 0
    except Exception as e:
        print(f"Error removing completed course: {e}")
        return False
