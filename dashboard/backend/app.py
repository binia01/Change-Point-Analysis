from flask import Flask, jsonify, request
from flask_cors import CORS
from data_service import DataService
import config


def create_app() -> Flask:
    app = Flask(__name__)
    CORS(app, origins=config.CORS_ORIGINS)

    svc = DataService()

    # ── Health check ──────────────────────────────────────────────────────────
    @app.route("/api/health")
    def health():
        return jsonify({"status": "ok"})

    # ── Historical prices (with optional date range) ──────────────────────────
    @app.route("/api/prices")
    def prices():
        start = request.args.get("start")
        end = request.args.get("end")
        return jsonify(svc.prices_json(start, end))

    # ── Summary statistics ────────────────────────────────────────────────────
    @app.route("/api/stats")
    def stats():
        start = request.args.get("start")
        end = request.args.get("end")
        return jsonify(svc.summary_stats(start, end))

    # ── Events ────────────────────────────────────────────────────────────────
    @app.route("/api/events")
    def events():
        category = request.args.get("category")
        return jsonify(svc.events_json(category))

    # ── Event categories ──────────────────────────────────────────────────────
    @app.route("/api/events/categories")
    def event_categories():
        return jsonify(svc.categories())

    # ── Event impacts (price change around events) ────────────────────────────
    @app.route("/api/events/impacts")
    def event_impacts():
        category = request.args.get("category")
        return jsonify(svc.event_impacts_json(category))

    # ── Change point results ──────────────────────────────────────────────────
    @app.route("/api/changepoints")
    def changepoints():
        return jsonify(svc.change_point_json())

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host=config.HOST, port=config.PORT, debug=config.DEBUG)
