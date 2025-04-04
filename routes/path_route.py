from controller.path_controller import (
    generate_path,
    save_path_data,
    delete_path_by_id,
    update_path_by_id,
)
from flask import Blueprint, jsonify, request
from utils.polyline import decode_polyline
from controller.auth_controller import authenticate_jwt


path_routes = Blueprint("path_routes", __name__)


@path_routes.route("/get-path", methods=["POST"])
def get_path():
    request_payload = request.get_json()

    if (
        not request_payload
        or "starting_point" not in request_payload
        or "distance" not in request_payload
    ):
        return jsonify({"error": "Missing either starting_point or distance"}), 400

    path_data = generate_path(
        starting_point=request_payload["starting_point"],
        distance_meters=request_payload["distance"],
    )

    encoded_polyline = path_data["routes"][0]["geometry"]
    decoded_polyline = decode_polyline(encoded_polyline)

    return jsonify({"path": decoded_polyline}), 200


@path_routes.route("/save-path", methods=["POST"])
def save_path():

    token = authenticate_jwt(request.cookies.get("token"))
    if not token["user_id"]:
        return jsonify({"error": "Token validation error"}), 400

    user_id = token["user_id"]

    request_payload = request.get_json()
    if (
        not request_payload
        or "waypoints" not in request_payload
        or "title" not in request_payload
        or "distance" not in request_payload
        or "time" not in request_payload
    ):
        return (
            jsonify({"error": "Missing either waypoints, title, distance or time"}),
            400,
        )

    new_path, error = save_path_data(request_payload, user_id)

    if error:
        return jsonify({"error": error}), 400
    return jsonify({"message": "Path saved successfully"}), 201


@path_routes.route("/delete-path/<path_id>", methods=["DELETE"])
def delete_user_path(path_id):

    token = authenticate_jwt(request.cookies.get("token"))

    if not token["user_id"]:
        return jsonify({"error": "Token validation error"}), 400

    result, error = delete_path_by_id(path_id)

    if error:
        return jsonify({"error": error}), 400

    return jsonify({"message": "Path successfully deleted"}), 201


@path_routes.route("/update-path/<path_id>", methods=["PUT"])
def update_user_path(path_id):

    token = authenticate_jwt(request.cookies.get("token"))

    if not token["user_id"]:
        return jsonify({"error": "Token validation error"}), 400

    request_payload = request.get_json()
    
    if (
        not request_payload
        or "waypoints" not in request_payload
        or "title" not in request_payload
        or "distance" not in request_payload
        or "time" not in request_payload
    ):
        return (
            jsonify({"error": "Missing either waypoints, title, distance or time"}),
            400,
        )

    result, error = update_path_by_id(path_id, request_payload)

    if error:
        return jsonify({"error": error}), 400

    return jsonify({"message": "Path successfully updated"}), 201
