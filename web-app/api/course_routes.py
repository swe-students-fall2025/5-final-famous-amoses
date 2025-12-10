"""
course_routes.py

Flask blueprint for course search and autocomplete API endpoints.
"""

from flask import Blueprint, jsonify, request

from .course_filtering import get_all_courses_from_db

courses = Blueprint("courses", __name__)


@courses.route("/search", methods=["GET"])
def search_courses():
    """
    Search courses by query string for autocomplete suggestions.

    Query parameters:
    - q: Search query (searches in course_code and title)
    - limit: Maximum number of results (default: 20)

    Returns:
    {
        "courses": [
            {
                "course_code": "CSCI-UA.0101",
                "title": "Introduction to Computer Science",
                "credits": 4
            },
            ...
        ]
    }
    """
    query = request.args.get("q", "").strip()
    limit = int(request.args.get("limit", 20))

    if not query:
        return jsonify({"courses": []}), 200

    try:
        # Get all courses from database
        all_courses = get_all_courses_from_db()

        # Filter courses by query (case-insensitive search in code and title)
        query_lower = query.lower()
        matching_courses = []

        for course in all_courses:
            course_code = course.get("course_code", "").lower()
            title = course.get("title", "").lower()

            # Check if query matches course code or title
            if query_lower in course_code or query_lower in title:
                matching_courses.append(
                    {
                        "course_code": course.get("course_code", ""),
                        "title": course.get("title", ""),
                        "credits": course.get("credits", 4),
                    }
                )

        # Sort by relevance: code matches starting with query first, then other code matches, then title matches
        matching_courses.sort(
            key=lambda c: (
                0 if c["course_code"].lower().startswith(query_lower) else 1,
                0 if query_lower in c["course_code"].lower() else 1,
            )
        )

        # Limit results
        matching_courses = matching_courses[:limit]

        return jsonify({"courses": matching_courses}), 200

    except Exception as e:
        print(f"Error searching courses: {e}")
        return jsonify({"error": "Failed to search courses"}), 500
