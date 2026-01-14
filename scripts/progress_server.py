#!/usr/bin/env python3
"""
Progress Server for GitHub Actions
Provides real-time progress updates for subscription testing
"""

import os
import sys
import threading
import time
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

progress_data = {
    "status": "starting",
    "stage": "initializing",
    "overall_percentage": 0,
    "stage_percentage": 0,
    "total_nodes": 0,
    "processed_nodes": 0,
    "stages": {
        "startup": {"completed": 0, "total": 1},
        "subs_check": {"completed": 0, "total": 1},
        "results_processing": {"completed": 0, "total": 1},
        "file_generation": {"completed": 0, "total": 1},
    },
}


@app.route("/api/progress", methods=["GET"])
def get_progress():
    return jsonify(progress_data)


@app.route("/api/update-progress", methods=["POST"])
def update_progress():
    data = request.json
    if data:
        progress_data.update(data)
        print(f"[PROGRESS] Updated: {data}")
    return jsonify({"success": True})


def monitor_log():
    log_file = "/tmp/subs_check_progress.log"
    while True:
        try:
            if os.path.exists(log_file):
                with open(log_file, "r") as f:
                    content = f.read()
                    if "Stage:" in content:
                        # Parse progress from log
                        lines = content.strip().split("\n")
                        for line in lines[-5:]:  # Check last 5 lines
                            if "Stage:" in line and "%" in line:
                                try:
                                    parts = line.split("|")
                                    if len(parts) >= 3:
                                        stage = parts[0].split(":")[1].strip()
                                        percentage = (
                                            parts[1]
                                            .split(":")[1]
                                            .strip()
                                            .replace("%", "")
                                        )
                                        details = parts[2].strip()

                                        progress_data["stage"] = stage
                                        progress_data["stage_percentage"] = int(
                                            percentage
                                        )

                                        # Map stage to overall progress
                                        stage_mapping = {
                                            "startup": 5,
                                            "subs_check": 80,
                                            "results_processing": 10,
                                            "file_generation": 5,
                                        }
                                        if stage in stage_mapping:
                                            base_progress = sum(
                                                [
                                                    v
                                                    for k, v in stage_mapping.items()
                                                    if k < stage
                                                ]
                                            )
                                            current_stage_weight = stage_mapping[stage]
                                            progress_data["overall_percentage"] = (
                                                base_progress
                                                + (
                                                    current_stage_weight
                                                    * int(percentage)
                                                    // 100
                                                )
                                            )
                                except:
                                    pass
        except:
            pass
        time.sleep(2)


if __name__ == "__main__":
    # Start log monitoring in background
    monitor_thread = threading.Thread(target=monitor_log, daemon=True)
    monitor_thread.start()

    print("🌐 Progress server starting on http://localhost:19999...")
    print("📊 Progress monitoring active")

    app.run(host="0.0.0.0", port=19999, debug=False, threaded=True)
