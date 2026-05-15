import yt_dlp
import cv2

from ultralytics import YOLO  # YOLO model

model = YOLO("yolov8n.pt")  # Load the YOLO model (you can choose different versions)


def process_video(video_url, analysis_collection):
    # do your logic here # example

    ydl_opts = {"format": "best[ext=mp4]"}

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(video_url, download=False)
        stream_url = info["url"]

    cap = cv2.VideoCapture(stream_url)
    frame_count = 0

    vehicle_count = {"car": 0, "motorcycle": 0, "bus": 0, "truck": 0}

    # COCO class mapping (YOLO)
    CLASS_MAP = {2: "car", 3: "motorcycle", 5: "bus", 7: "truck"}
    tracked_vehicle_ids = set()

    while True:
        ret, frame = cap.read()

        if not ret:
            break

        frame_count += 1
        # run YOLO here
        # detections = model(frame)

        results = model.track(frame, persist=True, verbose=False)[0]

        for box in results.boxes:

            if box.id is None:
                continue

            track_id = int(box.id[0])

            cls_id = int(box.cls[0])

            if cls_id in CLASS_MAP:

                vehicle_type = CLASS_MAP[cls_id]

                if track_id not in tracked_vehicle_ids:

                    tracked_vehicle_ids.add(track_id)

                    vehicle_count[vehicle_type] += 1

    cap.release()

    analysis_collection.update_one(
        {"process_video_url": video_url},
        {
            "$set": {
                "status": "processed",
                "frames_processed": frame_count,
                "vehicle_count": vehicle_count,
            }
        },
    )
