"""ACEest Fitness & Gym - Flask service (in-memory store)."""
from flask import Flask, jsonify, request

PLANS = {"basic": 29.99, "premium": 49.99, "elite": 79.99}


def create_app():
    app = Flask(__name__)
    app.config["MEMBERS"] = {}
    app.config["WORKOUTS"] = []
    app.config["NEXT_ID"] = 1

    @app.get("/health")
    def health():
        return jsonify(status="ok"), 200

    @app.get("/plans")
    def plans():
        return jsonify(PLANS), 200

    @app.post("/members")
    def add_member():
        data = request.get_json(silent=True) or {}
        name = str(data.get("name", "")).strip()
        plan = str(data.get("plan", "basic")).lower()
        if not name:
            return jsonify(error="name is required"), 400
        if plan not in PLANS:
            return jsonify(error="invalid plan"), 400
        mid = app.config["NEXT_ID"]
        app.config["NEXT_ID"] += 1
        member = {"id": mid, "name": name, "plan": plan}
        app.config["MEMBERS"][mid] = member
        return jsonify(member), 201

    @app.get("/members")
    def list_members():
        return jsonify(list(app.config["MEMBERS"].values())), 200

    @app.get("/members/<int:mid>")
    def get_member(mid):
        member = app.config["MEMBERS"].get(mid)
        if member is None:
            return jsonify(error="member not found"), 404
        return jsonify(member), 200

    @app.delete("/members/<int:mid>")
    def delete_member(mid):
        if app.config["MEMBERS"].pop(mid, None) is None:
            return jsonify(error="member not found"), 404
        return "", 204

    @app.post("/members/<int:mid>/workouts")
    def log_workout(mid):
        if mid not in app.config["MEMBERS"]:
            return jsonify(error="member not found"), 404
        data = request.get_json(silent=True) or {}
        exercise = str(data.get("exercise", "")).strip()
        minutes = data.get("minutes")
        if not exercise or not isinstance(minutes, int) or minutes <= 0:
            return jsonify(error="exercise and positive integer minutes required"), 400
        workout = {"member_id": mid, "exercise": exercise, "minutes": minutes}
        app.config["WORKOUTS"].append(workout)
        return jsonify(workout), 201

    @app.get("/members/<int:mid>/summary")
    def summary(mid):
        if mid not in app.config["MEMBERS"]:
            return jsonify(error="member not found"), 404
        ws = [w for w in app.config["WORKOUTS"] if w["member_id"] == mid]
        return jsonify(member_id=mid, sessions=len(ws),
                       total_minutes=sum(w["minutes"] for w in ws)), 200

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
