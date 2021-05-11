import cv2
import numpy as np
import easyocr
from app.services.plate_service import is_valid_plate_format
from app import models
import os
import tempfile
from app.__init__ import App
import re


class Detector():

    def __init__(self, stream_type, stream_id, stream_file, stream_url):
        self.stream_id = stream_id
        self.stream_type = stream_type
        self.yolo = cv2.dnn.readNet("app\detection\weights\model.weights", "app\detection\weights\darknet-yolov3.cfg")
        self.classes = []
        with open("app\detection\weights\classes.names", "r") as file:
            self.classes = [line.strip() for line in file.readlines()]
        self.plates = []
        self.plates_values = []
        self.reader = easyocr.Reader(['en'])
        self.NUMBER_OF_DETECTED_PLATES = 0
        self.stream_file = stream_file
        self.stream_url = stream_url
    
    def detect_on_image(self, image):
        image = self.detect_plate_on_image(image)
        self.ocr_on_image()
        _, jpg = cv2.imencode('.jpg', image)
        hash_values = {"detected_plates": self.plates_values, "image": jpg}
        self.save_detected_plates()
        return hash_values

    def detect_on_video(self):
        if self.stream_type == "video":
            temp = tempfile.TemporaryFile(mode="w+b")
            temp.write(self.stream_file)
            path = temp.name
        else:
            path = self.stream_url

        cap = cv2.VideoCapture(path)
        SKIP_FRAMES = 100
        CURRENT_PLATES_COUNT = len(self.plates)
        count = 0
        while True:
            ret, img = cap.read()
            count += 1
            if ret:
                if(count % SKIP_FRAMES == 0):
                    cv2.putText(img, "Detectando...", (10,35), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 3, cv2.LINE_AA)
                    img = self.detect_plate_on_image(img)
                    if len(self.plates) > CURRENT_PLATES_COUNT:
                        self.ocr_on_image()
                        self.save_detected_plates()
                        CURRENT_PLATES_COUNT = len(self.plates)
                frame = cv2.imencode('.jpg', img)[1].tobytes()
                yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            else:
                if self.stream_type == "video":
                    temp.close()
                break
        
    def save_detected_plates(self):
        with App.get_app().app_context():
            for p in self.plates_values:
                count_plate = models.Plate.query.filter_by(stream_id=self.stream_id, plate_number=p).count()
                if count_plate == 0:
                    plate = models.Plate(p, self.stream_id)
                    models.db.session.add(plate)
                    models.db.session.commit()


    def ocr_on_image(self):
        for plate in self.plates:
            result = self.reader.readtext(plate)
            for probabily_plate in result:
                if probabily_plate[2] > 0.5:
                    plate = probabily_plate[1].replace(" ", "")
                    plate = plate.upper()
                    plate = re.sub(r'\W+', '', plate)
                    if is_valid_plate_format(plate) and not any(plate in p for p in self.plates_values):
                        self.plates_values.append(plate)


    def detect_plate_on_image(self, img):
        clean_image = img.copy()
        layer_names = self.yolo.getLayerNames()
        output_layers = [layer_names[i[0] - 1] for i in self.yolo.getUnconnectedOutLayers()]

        colorRed = (0,0,255)
        colorGreen = (0,255,0)
        colorWhite = (255,255,255)

        height, width, channels = img.shape

        # # Detecting objects
        blob = cv2.dnn.blobFromImage(img, 0.00392, (416, 416), (0, 0, 0), True, crop=False)

        self.yolo.setInput(blob)
        outputs = self.yolo.forward(output_layers)

        class_ids = []
        confidences = []
        boxes = []
        for output in outputs:
            for detection in output:
                scores = detection[5:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]
                if confidence > 0.3:
                    center_x = int(detection[0] * width)
                    center_y = int(detection[1] * height)
                    w = int(detection[2] * width)
                    h = int(detection[3] * height)

                    x = int(center_x - w / 2)
                    y = int(center_y - h / 2)

                    boxes.append([x, y, w, h])
                    confidences.append(float(confidence))
                    class_ids.append(class_id)

        indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)
        for i in range(len(boxes)):
            if i in indexes:
                x, y, w, h = boxes[i]
                label = str(self.classes[class_ids[i]])
                self.plates.append(clean_image[y:y + h, x:x + w])
                cv2.rectangle(img, (x, y), (x + w, y + h), colorGreen, 3)
                cv2.putText(img, label, (x, y - 30), cv2.FONT_HERSHEY_PLAIN, 3, colorWhite, 2)
        return img