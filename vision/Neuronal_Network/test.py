import cv2 as cv
from ultralytics import YOLO

model = YOLO("/home/danieldrg/Documents/CNN/best.pt")
min_area = 200
max_area = 10000

cap = cv.VideoCapture(1)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    results = model(frame, verbose=False)[0]

    for box in results.boxes:
        cls_id = int(box.cls[0])
        conf = box.conf[0]
        label = model.names[cls_id]
        x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
        area = (x2 - x1) * (y2 - y1)

        if conf > 0.5 and min_area < area < max_area and label in ["ripe", "unripe"]:
            print(conf, "area:", area)
            cv.rectangle(frame, (x1, y1), (x2, y2), (255,0,0), 2)
            cv.putText(frame, label.upper(), (x1, y1 - 10), cv.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)
            break  # Solo el primer objeto detectado

    resized_frame = cv.resize(frame, (1920, 1080))
    cv.imshow("YOLOv8 Inference", resized_frame)

    if cv.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv.destroyAllWindows()
