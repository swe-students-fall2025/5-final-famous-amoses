"""
plan_routes.py

Flask blueprint for semester plan management API endpoints.
Requires JWT authentication.
"""

import os
from functools import wraps

import jwt
from flask import Blueprint, g, jsonify, request

from .plan_utils import (
    get_all_semester_plans,
    get_semester_plan,
    update_semester_plan,
)
from .user_model import db

SECRET = os.getenv("JWT_SECRET", "defaultsecret")


def require_auth(f):
    """
    Decorator to require JWT authentication for a route.
    Same as in recommendation_routes.py - could be extracted to shared module later.
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


plans = Blueprint("plans", __name__)


@plans.route("/save", methods=["POST"])
@require_auth
def save_semester_plan():
    """
    Save courses for a semester.

    Requires JWT authentication.
    Request body:
    {
        "semester": "Freshman Fall",
        "courses": ["CSCI-UA.0101 Introduction to Computer Science (4 credits)", ...]
    }

    Returns:
    {
        "message": "Semester plan saved successfully",
        "semester": "Freshman Fall",
        "courses_count": 4
    }
    """
    # Get authenticated user
    user = g.user
    user_email = user.get("email")

    # Get request data
    data = request.json
    if not data:
        return jsonify({"error": "Missing request body"}), 400

    semester = data.get("semester")
    courses = data.get("courses", [])

    if not semester:
        return jsonify({"error": "Missing required field: semester"}), 400

    if not isinstance(courses, list):
        return jsonify({"error": "courses must be a list"}), 400

    # Update semester plan in database
    success = update_semester_plan(user_email, semester, courses, db)

    if not success:
        return (
            jsonify({"error": "Failed to save semester plan"}),
            500,
        )

    return (
        jsonify(
            {
                "message": "Semester plan saved successfully",
                "semester": semester,
                "courses_count": len(courses),
            }
        ),
        200,
    )


@plans.route("/load", methods=["GET"])
@require_auth
def load_all_plans():
    """
    Load all semester plans for the authenticated user.

    Requires JWT authentication.

    Returns:
    {
        "Freshman Fall": ["CSCI-UA.0101 Introduction to Computer Science (4 credits)", ...],
        "Freshman Spring": [...],
        ...
    }
    """
    # Get authenticated user
    user = g.user
    user_email = user.get("email")

    # Get all semester plans
    all_plans = get_all_semester_plans(user_email, db)

    return jsonify(all_plans), 200
