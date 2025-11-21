# Author: Daniel De Regules Gamboa
# Date: October 2025
# Description: This script uses a RealSense camera to capture color and depth frames,
# performs object detection using a YOLOv8 model, and estimates the 3D pose of detected strawberries
# using the PnP algorithm. 

import cv2 as cv
from ultralytics import YOLO
import numpy as np
import pyrealsense2 as rs

def robust_median_depth(depth_scale, depth_image, x1, y1, x2, y2):
    """Compute the robust median depth in the specified ROI in meters."""
    x1, y1 = max(0, x1), max(0, y1)
    x2, y2 = min(depth_image.shape[1] - 1, x2), min(depth_image.shape[0] - 1, y2)
    roi = depth_image[y1:y2+1, x1:x2+1]
    roi = roi[roi > 0]  # Remove zero values
    if len(roi) == 0:
        return None
    # Filter out outliers
    lo, hi = np.percentile(roi, [5, 95])
    roi = roi[(roi >= lo) & (roi <= hi)]
    if roi.size == 0:
        return None
    return np.median(roi) * depth_scale # Convert to meters

def main(second_iteration = False):
    T_4x4 = None
    # Initialize RealSense pipeline
    pipeline = rs.pipeline()
    config = rs.config()

    # Enable color and depth streams
    config.enable_stream(rs.stream.color, 1280, 720, rs.format.bgr8, 30)
    config.enable_stream(rs.stream.depth, 1280, 720, rs.format.z16, 30)
    profile = pipeline.start(config)
    align = rs.align(rs.stream.color)

    # Get stream intrinsics
    depth_stream = profile.get_stream(rs.stream.depth).as_video_stream_profile()
    color_stream = profile.get_stream(rs.stream.color).as_video_stream_profile()
    depth_intr = depth_stream.get_intrinsics()
    color_intr = color_stream.get_intrinsics()

    depth_scale = profile.get_device().first_depth_sensor().get_depth_scale()

    # Load YOLOv8 model
    model = YOLO("vision/best.pt")
    min_area = 500
    max_area = 50000

    width_strawberry = 0.0326 #m
    height_strawberry = 0.0342 #m

    # Construct camera matrix from RealSense intrinsics
    camera_matrix = np.array([[color_intr.fx,     0.0,     color_intr.ppx],
                [0.0,         color_intr.fy, color_intr.ppy],
                [0.0,         0.0,     1.0      ]], dtype=np.float64)

    #dist_coeffs = np.zeros(5, dtype=np.float32)
    dist_coeffs = np.array(color_intr.coeffs[:5], dtype=np.float64)

    for _ in range(20):
        frames = pipeline.wait_for_frames()
        frames = align.process(frames)

    # Wait for a coherent pair of frames: depth and color
    frames = pipeline.wait_for_frames()
    frames = align.process(frames)
    color_frame = frames.get_color_frame()
    depth_frame = frames.get_depth_frame()

    if not color_frame or not depth_frame:
        print("No frame")
        exit(1)

    # Convert images to numpy arrays
    frame = np.asanyarray(color_frame.get_data())
    depth = np.asanyarray(depth_frame.get_data())

    # Perform inference
    results = model(frame, verbose=False)[0]

    # Prepare candidate list (distance to image center) if second_iteration requested
    img_h, img_w = frame.shape[:2]
    img_cx, img_cy = img_w / 2.0, img_h / 2.0

    candidates = []
    for box in results.boxes:
        cls_id = int(box.cls[0])
        conf = float(box.conf[0])
        label = model.names[cls_id]
        x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
        area = (x2 - x1) * (y2 - y1)

        if conf > 0.60 and min_area < area < max_area and label in ["ripe"]:
            bx_cx = (x1 + x2) / 2.0
            bx_cy = (y1 + y2) / 2.0
            dist_center = np.hypot(bx_cx - img_cx, bx_cy - img_cy)
            candidates.append({
                "box": box,
                "x1": x1, "y1": y1, "x2": x2, "y2": y2,
                "conf": conf, "label": label, "area": area,
                "dist_center": dist_center
            })

    # If second_iteration requested, select the candidate closest to image center
    if second_iteration and len(candidates) > 0:
        candidates = [min(candidates, key=lambda c: c["dist_center"])]

    # Process the selected candidates (if any)
    for cand in candidates:
        x1, y1, x2, y2 = cand["x1"], cand["y1"], cand["x2"], cand["y2"]
        label = cand["label"]
        conf = cand["conf"]
        area = cand["area"]

        Z = robust_median_depth(depth_scale, depth, x1, y1, x2, y2) # Meters
        print("Depth (m):", Z)
        if Z is None:
            print(conf, "area:", area)
            cv.rectangle(frame, (x1, y1), (x2, y2), (255,0,0), 2)
            cv.putText(frame, f"{label} no depth", (x1, y1 - 10), cv.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)
            continue

        image_points = np.array([
            (x1, y1),         # Top-left
            (x2, y1),         # Top-right
            (x2, y2),         # Bottom-right
            (x1, y2)          # Bottom-left
        ], dtype="double")

        object_points = np.array([
            (-width_strawberry/2, -height_strawberry/2, 0.0),  # Top-left
            ( width_strawberry/2, -height_strawberry/2, 0.0),  # Top-right
            ( width_strawberry/2,  height_strawberry/2, 0.0),  # Bottom-right
            (-width_strawberry/2,  height_strawberry/2, 0.0)   # Bottom-left
        ])

        # PnP with Z guess
        rvec = np.zeros((3,1), dtype=np.float64)   # neutral initial orientation
        tvec = np.array([[0],[0],[Z]], dtype=np.float64)
        success, rvec, tvec = cv.solvePnP(
            objectPoints=object_points,
            imagePoints=image_points,
            cameraMatrix=camera_matrix,
            distCoeffs=dist_coeffs,
            rvec=rvec,
            tvec=tvec,
            useExtrinsicGuess=True,              
            flags=cv.SOLVEPNP_ITERATIVE
        )

        color = (0,255,255) if success else (0,0,255)
        cv.rectangle(frame, (x1,y1), (x2,y2), color, 2)
        cv.putText(frame, f"{label}", (x1, y1 - 10), cv.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)

        if success:
            tvec[2,0] = Z # Adjust depth to box center
            T_4x4 = np.eye(4)
            #T_4x4[:3, :3], _ = cv.Rodrigues(rvec)
            T_4x4[:3, 3] = tvec.reshape(3)*1000  # Convert to mm
            print("Pose (mm):")
            print(T_4x4)
            cv.imshow("Strawberry Detection", frame)
            cv.waitKey(0)
            break
                
    pipeline.stop()
    return T_4x4

if __name__ == "__main__":
    main()