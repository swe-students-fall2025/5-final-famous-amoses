"""
user_routes.py

Flask blueprint for user profile management API endpoints.
Requires JWT authentication.
"""

import os
from functools import wraps

import jwt
from flask import Blueprint, g, jsonify, request

from .user_model import db

user_profile = Blueprint("user_profile", __name__)

SECRET = os.getenv("JWT_SECRET", "defaultsecret")


def require_auth(f):
    """
    Decorator to require JWT authentication for a route.
    Same as in recommendation_routes.py and plan_routes.py.
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return jsonify({"error": "Unauthorized: Missing token"}), 401

        try:
            token = auth_header.split(" ")[1]
        except IndexError:
            return jsonify({"error": "Unauthorized: Invalid token format"}), 401

        try:
            decoded = jwt.decode(token, SECRET, algorithms=["HS256"])
            email = decoded.get("email")
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Unauthorized: Token expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Unauthorized: Invalid token"}), 401

        if not email:
            return jsonify({"error": "Unauthorized: Invalid token payload"}), 401

        user = db.students.find_one({"email": email})
        if not user:
            return jsonify({"error": "Unauthorized: User not found"}), 401

        g.user = user
        return f(*args, **kwargs)

    return decorated_function


@user_profile.route("/profile", methods=["GET"])
@require_auth
def get_profile():
    """
    Get current user's profile.

    Requires JWT authentication.

    Returns:
    {
        "name": "...",
        "email": "...",
        "netid": "...",
        "major": "...",
        "year": "...",
        "interests": [...],
        "completed_courses": [...]
    }
    """
    user = g.user

    # Remove sensitive fields
    profile = {
        "name": user.get("name", ""),
        "email": user.get("email", ""),
        "netid": user.get("netid", ""),
        "major": user.get("major", ""),
        "year": user.get("year", ""),
        "interests": user.get("interests", []),
        "completed_courses": user.get("completed_courses", []),
    }

    return jsonify(profile), 200


@user_profile.route("/profile", methods=["PUT"])
@require_auth
def update_profile():
    """
    Update user's profile information.

    Requires JWT authentication.
    Request body:
    {
        "major": "Computer Science",
        "year": "Sophomore",
        "interests": ["AI", "Systems"]
    }

    Returns:
    {
        "message": "Profile updated successfully",
        "profile": { ... }
    }
    """
    user = g.user
    user_email = user.get("email")

    data = request.json
    if not data:
        return jsonify({"error": "Missing request body"}), 400

    # Build update dictionary (only update provided fields)
    update_fields = {}
    allowed_fields = ["major", "year", "interests"]

    for field in allowed_fields:
        if field in data:
            update_fields[field] = data[field]

    if not update_fields:
        return jsonify({"error": "No valid fields to update"}), 400

    # Validate interests is a list
    if "interests" in update_fields and not isinstance(
        update_fields["interests"], list
    ):
        return jsonify({"error": "interests must be a list"}), 400

    try:
        # Update user in database
        db.students.update_one({"email": user_email}, {"$set": update_fields})

        # Fetch updated user
        updated_user = db.students.find_one({"email": user_email})

        # Build response profile
        profile = {
            "name": updated_user.get("name", ""),
            "email": updated_user.get("email", ""),
            "netid": updated_user.get("netid", ""),
            "major": updated_user.get("major", ""),
            "year": updated_user.get("year", ""),
            "interests": updated_user.get("interests", []),
            "completed_courses": updated_user.get("completed_courses", []),
        }

        return (
            jsonify({"message": "Profile updated successfully", "profile": profile}),
            200,
        )
    except Exception as e:
        print(f"Error updating profile: {e}")
        return jsonify({"error": "Failed to update profile"}), 500


@user_profile.route("/completed-courses", methods=["PUT"])
@require_auth
def update_completed_courses():
    """
    Update user's completed courses list.

    Requires JWT authentication.
    Request body:
    {
        "completed_courses": ["CSCI-UA.0101", "CSCI-UA.0102", ...]
    }

    Returns:
    {
        "message": "Completed courses updated successfully",
        "completed_courses": [...]
    }
    """
    user = g.user
    user_email = user.get("email")

    data = request.json
    if not data:
        return jsonify({"error": "Missing request body"}), 400

    completed_courses = data.get("completed_courses", [])

    if not isinstance(completed_courses, list):
        return jsonify({"error": "completed_courses must be a list"}), 400

    try:
        # Update completed courses in database
        db.students.update_one(
            {"email": user_email},
            {"$set": {"completed_courses": completed_courses}},
        )

        return (
            jsonify(
                {
                    "message": "Completed courses updated successfully",
                    "completed_courses": completed_courses,
                }
            ),
            200,
        )
    except Exception as e:
        print(f"Error updating completed courses: {e}")
        return jsonify({"error": "Failed to update completed courses"}), 500
