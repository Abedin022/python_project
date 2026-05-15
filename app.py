from flask import Flask, redirect, render_template, request
import os
import threading
from services.video_analyzer import process_video
from pymongo import MongoClient
from dotenv import load_dotenv
from bson.objectid import ObjectId
from datetime import datetime

current_time = datetime.now().strftime("%d-%b-%Y, %I:%M %p")

load_dotenv()

client = MongoClient(os.getenv("MONGO_URI"))

try:
    client.admin.command("ping")
    print("MongoDB connected")
except Exception as e:
    print(e)

db = client["video_analyzer_db"]
analysis_collection = db["analysis_results"]

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/video-input")
def video_input():
    return render_template("video_input.html")


@app.route("/analyze", methods=["POST"])
def analyze():
    video_url = request.form.get("youtube_url")
    existing_data = analysis_collection.find_one({"process_video_url": video_url})
    if existing_data:
        print("Data already exists for this URL, returning existing data.")
        return render_template("analyze_result.html", result=existing_data)

    thread = threading.Thread(
        target=process_video, args=(video_url, analysis_collection)
    )
    if "shorts" in video_url:
        youtube_id = video_url.split("/shorts/")[1].split("?")[0]
    else:
        youtube_id = video_url.split("v=")[1].split("&")[0]
    print(youtube_id)
    analysis_collection.insert_one(
        {
            "process_video_url": video_url,
            "status": "processing",
            "timestamp": current_time,
            "video_id": youtube_id,
        }
    )

    thread.start()

    return redirect("/videos")
    # return render_template("analyze_result.html", youtube_url=video_url, result=result)


@app.route("/videos")
def videos():

    processing = list(analysis_collection.find({"status": "processing"}))

    processed = list(analysis_collection.find({"status": "processed"}))

    return render_template("videos.html", processing=processing, processed=processed)


@app.route("/video/<video_id>")
def video_details(video_id):

    result = analysis_collection.find_one({"_id": ObjectId(video_id)})

    return render_template(
        "analyze_result.html",
        result=result,
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
