"""Flask application exposing a retro-styled calculator UI and API."""

from __future__ import annotations

import datetime as _dt
from dataclasses import dataclass
from http import HTTPStatus
from typing import Dict, Callable

from flask import Flask, jsonify, render_template, request


_OPERATIONS: Dict[str, Callable[[float, float], float]] = {
    "+": lambda a, b: a + b,
    "-": lambda a, b: a - b,
    "×": lambda a, b: a * b,
    "*": lambda a, b: a * b,
    "÷": lambda a, b: a / b,
    "/": lambda a, b: a / b,
}


@dataclass
class CalculationRequest:
    """Container for calculator inputs."""

    left: float
    right: float
    operator: str

    @classmethod
    def from_payload(cls, payload: dict) -> "CalculationRequest":
        try:
            left = float(payload["left"])
            right = float(payload["right"])
            operator = str(payload["operator"])
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError("Invalid calculation payload") from exc

        if operator not in _OPERATIONS:
            raise ValueError(f"Unsupported operator {operator!r}")
        return cls(left=left, right=right, operator=operator)


def create_app() -> Flask:
    """Create and configure the Flask application."""

    app = Flask(__name__, static_folder="static", template_folder="templates")

    @app.context_processor
    def inject_timestamp():
        """Provide the current timestamp to templates."""

        return {"generated_at": _dt.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")}

    @app.route("/", methods=["GET"])
    def index():
        """Serve the calculator UI."""

        return render_template("index.html")

    @app.route("/api/calculate", methods=["POST"])
    def calculate():
        """Perform a calculation based on JSON payload."""

        payload = request.get_json(silent=True) or {}
        try:
            calc_req = CalculationRequest.from_payload(payload)
            result = _OPERATIONS[calc_req.operator](calc_req.left, calc_req.right)
        except ValueError as exc:
            return (
                jsonify({"status": "error", "message": str(exc)}),
                HTTPStatus.BAD_REQUEST,
            )
        except ZeroDivisionError:
            return (
                jsonify({"status": "error", "message": "Cannot divide by zero."}),
                HTTPStatus.BAD_REQUEST,
            )

        return jsonify(
            {
                "status": "ok",
                "left": calc_req.left,
                "right": calc_req.right,
                "operator": calc_req.operator,
                "result": result,
                "evaluated_at": _dt.datetime.utcnow().isoformat() + "Z",
            }
        )

    @app.route("/api/time", methods=["GET"])
    def current_time():
        """Expose server-side time for the live clock."""

        now = _dt.datetime.utcnow()
        return jsonify({"iso": now.isoformat() + "Z"})

    @app.route("/healthz", methods=["GET"])
    def healthcheck():
        """Health endpoint for uptime checks."""

        return jsonify({"status": "ok", "time": _dt.datetime.utcnow().isoformat() + "Z"})

    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
