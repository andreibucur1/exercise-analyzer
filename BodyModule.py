import cv2
import mediapipe as mp
import time

class PostureDetector():
    def __init__(self, mode=False, upBody=False, smooth = True,
                 detectCon = 0.5, trackCon = 0.5):
        self.mode = mode
        self.upBody = upBody
        self.smooth = smooth
        self.detectCon = detectCon
        self.trackCon = trackCon

        self.mpDraw = mp.solutions.drawing_utils
        self.mpPose = mp.solutions.pose
        self.hands = self.mpPose.Pose(static_image_mode=self.mode,
               enable_segmentation=self.upBody,
               smooth_segmentation=self.smooth,
               min_detection_confidence=self.detectCon,
               min_tracking_confidence=self.detectCon)
    def findPose(self, img, draw = True):
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(imgRGB)
        if self.results.pose_landmarks:
            if draw:
                self.mpDraw.draw_landmarks(img, self.results.pose_landmarks,
                                 self.mpPose.POSE_CONNECTIONS)
        return img

    def getPosition(self, img, draw = True):
        landmarks_list = []

        if self.results.pose_landmarks:
            for id, lm in enumerate(self.results.pose_landmarks.landmark):

                h, w, c = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                landmarks_list.append([id, cx, cy, lm.visibility])
                if draw:
                    cv2.circle(img, (cx, cy), 5, (255, 0, 255), cv2.FILLED)
        return landmarks_list


