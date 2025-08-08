import cv2
import mediapipe as mp
import time
from BodyModule import PostureDetector
import math
from scipy.signal import savgol_filter
import matplotlib. pyplot as plt
from scipy.signal import find_peaks
import os
import numpy as np
from openai import OpenAI
VISIBILITY = 0.5


class ExerciseAnalyzer():
    def __init__(self):
        self.detector = PostureDetector()
        self.client = OpenAI(
            base_url="https://models.github.ai/inference",
            api_key=os.environ["GITHUB_TOKEN"],
        )
    def analyzeVideo(self, video_path, exercise):
        cap = cv2.VideoCapture(video_path)
        l_arm_angles=[]
        r_arm_angles=[]
        l_shoulder_angles=[]
        r_shoulder_angles=[]
        l_leg_angles=[]
        r_leg_angles=[]
        left_arm_is_visible = True
        right_arm_is_visible = True
        left_leg_is_visible = True
        right_leg_is_visible = True
        while True:
            succes, img = cap.read()
            if not succes:
                print("End of video or failed to read frame.")
                break 
            img = self.detector.findPose(img, draw=True)
            self.lmlist = self.detector.getPosition(img, draw=False)
            if len(self.lmlist) != 0:
                l_arm_angles.append(self.getLeftArm())
                r_arm_angles.append(self.getRightArm())
                l_shoulder_angles.append(self.getLeftShoulder())
                r_shoulder_angles.append(self.getRightShoulder())
                l_leg_angles.append(self.getLeftLeg)
                r_leg_angles.append(self.getRightLeg)
                if(self.lmlist[13][3] < VISIBILITY):
                    left_arm_is_visible = False
                if(self.lmlist[14][3] < VISIBILITY):    
                    right_arm_is_visible = False
                if(self.lmlist[25][3] < VISIBILITY):
                    left_leg_is_visible = False
                if(self.lmlist[26][3] < VISIBILITY):
                    right_leg_is_visible = False
                
                

            cv2.imshow("Image", img)
            cv2.waitKey(1)
        
        
        match exercise:
            case "bicepCurl":
                mark, message = self.checkBicepCurl(l_arm_angles, r_arm_angles, left_arm_is_visible, right_arm_is_visible)
            case "tricepExtension":
                mark, message = self.checkTricepExtension(l_arm_angles, r_arm_angles, left_arm_is_visible, right_arm_is_visible)
            case "lateralRaise":
                mark, message = self.checkLateralRaises(l_shoulder_angles, r_shoulder_angles, left_arm_is_visible, right_arm_is_visible)
            case "shoulderPress":
                mark, message = self.checkShoudlerPress(l_shoulder_angles, r_shoulder_angles, left_arm_is_visible, right_arm_is_visible)
            case "legPress":
                mark, message = self.checkLegPress(l_leg_angles, r_leg_angles, left_leg_is_visible, right_leg_is_visible)
            case _:
                mark, message = 0, "Unknown exercise"
        

        return mark, message

    def findAngle(self, a, b, c):
        x1, y1 = a
        x2, y2 = b
        x3, y3 = c

        ba = (x1 - x2, y1 - y2)
        bc = (x3 - x2, y3 - y2)


        dot_product = ba[0]*bc[0] + ba[1]*bc[1]

        mag_ba = math.hypot(ba[0], ba[1])
        mag_bc = math.hypot(bc[0], bc[1])

        cos_angle = dot_product / (mag_ba * mag_bc + 1e-8)  # ca să nu împărți la 0
        angle = math.acos(cos_angle)

        return math.degrees(angle)
    


    def checkBicepCurl(self, left_arm_angles, right_arm_angles, left_arm_is_visible, right_arm_is_visible):

    
        max_left_angles = []
        max_right_angles = []
        min_left_angles = []    
        min_right_angles = []

        mistakes_left = 0
        mistakes_right = 0

        if left_arm_is_visible:
            filtered_left_angles = savgol_filter(left_arm_angles, window_length=20, polyorder=2, mode= "nearest")
            max_left_angles = np.round(filtered_left_angles[find_peaks(filtered_left_angles)[0]],0)
            min_left_angles = np.round(filtered_left_angles[find_peaks(-filtered_left_angles)[0]],0)
            for i in range(len(max_left_angles)):
                if max_left_angles[i] < 160 :
                    mistakes_left += 1
            for i in range(len(min_left_angles)):
                if min_left_angles[i] > 65:
                    mistakes_left += 1
        if right_arm_is_visible:
            filtered_right_angles = savgol_filter(right_arm_angles, window_length=20, polyorder=2,  mode= "nearest")
            max_right_angles = np.round(filtered_left_angles[find_peaks(filtered_right_angles)[0]],0)
            min_right_angles = np.round(filtered_right_angles[find_peaks(-filtered_right_angles)[0]],0)
            for i in range(len(max_right_angles)):
                if max_right_angles[i] < 160 :
                    mistakes_right += 1
            for i in range(len(min_right_angles)):
                if min_right_angles[i] > 65:
                    mistakes_right += 1
        if left_arm_is_visible and right_arm_is_visible:
            mark = 10 - 5 * (mistakes_left + mistakes_right) / min(len(min_left_angles), len(min_right_angles))
        elif left_arm_is_visible:
            mark = 10 - 5 * mistakes_left / len(min_left_angles)
        elif right_arm_is_visible:
            mark = 10 - 5 * mistakes_right / len(min_right_angles)
        else:
            mark = 0
        response = self.client.chat.completions.create(
            model="openai/gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": 
                    "You are an expert in analyzing exercise form based on angles. The mark given is correct and based on the mark, number of mistakes and angles provided, provide a message that is clear and concise. if an array is empty = visibility of an arm is low, mention that.",
                },
                {
                    "role": "user",
                    "content": f"Analyze the following bicep curl: left arm min angles: {min_left_angles}, left arm max angles: {max_left_angles}, right arm min angles: {min_right_angles}, right arm max angles: {max_right_angles}, mark: {mark}, mistakes left: {mistakes_left}, mistakes right: {mistakes_right}. Provide a message.",
                },
            ],
            temperature=0.4,
            max_tokens=150,
            top_p=1
        )
        print(response.choices[0].message.content)
        print(f"Mark: {mark}")
        message = response.choices[0].message.content
        return mark, message

    def checkTricepExtension(self, left_arm_angles, right_arm_angles, left_arm_is_visible, right_arm_is_visible):
        mistakes_left = 0
        mistakes_right = 0
        max_left = []
        min_left = []
        max_right = []
        min_right = []
        if left_arm_is_visible:
            filtered_left = savgol_filter(left_arm_angles, window_length=20, polyorder=2, mode="nearest")
            max_left = np.round(filtered_left[find_peaks(filtered_left)[0]], 0)
            min_left = np.round(filtered_left[find_peaks(-filtered_left)[0]], 0)
            for angle in max_left:
                if angle < 165:  
                    mistakes_left += 1
            for angle in min_left:
                if angle > 90:
                    mistakes_left += 1

        if right_arm_is_visible:
            filtered_right = savgol_filter(right_arm_angles, window_length=20, polyorder=2, mode="nearest")
            max_right = np.round(filtered_right[find_peaks(filtered_right)[0]], 0)
            min_right = np.round(filtered_right[find_peaks(-filtered_right)[0]], 0)
            for angle in max_right:
                if angle < 165:
                    mistakes_right += 1
            for angle in min_right:
                if angle > 90:
                    mistakes_right += 1


        if left_arm_is_visible and right_arm_is_visible:
            mark = 10 - 5 * (mistakes_left + mistakes_right) / min(len(min_left), len(min_right))
        elif left_arm_is_visible:
            mark = 10 - 5 * mistakes_left / len(min_left)
        elif right_arm_is_visible:
            mark = 10 - 5 * mistakes_right / len(min_right)
        else:
            mark = 0

        response = self.client.chat.completions.create(
            model="openai/gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert analyzing tricep extension exercise based on angles and marks. if an array is empty = visibility of an arm is low, mention that."
                            "Generate a clear, concise feedback message."
                },
                {
                    "role": "user",
                    "content": (
                        f"Tricep extension analysis: left min angles {min_left}, left max angles {max_left}, "
                        f"right min angles {min_right}, right max angles {max_right}, "
                        f"mark: {mark}, mistakes left: {mistakes_left}, mistakes right: {mistakes_right}."
                    )
                }
            ],
            temperature=0.4,
            max_tokens=150,
            top_p=1
        )
        message = response.choices[0].message.content
        print(message)
        print(f"Mark: {mark}")

        return mark, message
    
    def checkLateralRaises(self, left_shoulder_angles, right_shoulder_angles, left_arm_is_visible, right_arm_is_visible):
        mistakes_left = 0
        mistakes_right = 0
        max_left = []
        min_left = []
        max_right = []
        min_right = []

        if left_arm_is_visible:
            filtered_left = savgol_filter(left_shoulder_angles, window_length=20, polyorder=2, mode="nearest")
            max_left = np.round(filtered_left[find_peaks(filtered_left)[0]], 0)
            min_left = np.round(filtered_left[find_peaks(-filtered_left)[0]], 0)
            for angle in max_left:
                if angle < 80: 
                    mistakes_left += 1
            for angle in min_left:
                if angle > 30:
                    mistakes_left += 1


        if right_arm_is_visible:
            filtered_right = savgol_filter(right_shoulder_angles, window_length=20, polyorder=2, mode="nearest")
            max_right = np.round(filtered_right[find_peaks(filtered_right)[0]], 0)
            min_right = np.round(filtered_right[find_peaks(-filtered_right)[0]], 0)
            for angle in max_right:
                if angle < 80:
                    mistakes_right += 1
            for angle in min_right:
                if angle > 30:
                    mistakes_right += 1


        if right_arm_is_visible and left_arm_is_visible:
            mark = 10 - 5 * (mistakes_left + mistakes_right) / min(len(min_left), len(min_right))
        elif left_arm_is_visible:
            mark = 10 - 5 * mistakes_left / len(min_left)
        elif right_arm_is_visible:
            mark = 10 - 5 * mistakes_right / len(min_right)
        else:
            mark = 0

        response = self.client.chat.completions.create(
            model="openai/gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert analyzing lateral raise exercise based on angles and marks. if an array is empty = visibility of an arm is low, mention that."
                            "Generate a clear, concise feedback message."
                },
                {
                    "role": "user",
                    "content": (
                        f"Lateral raise analysis: left min angles {min_left}, left max angles {max_left}, "
                        f"right min angles {min_right}, right max angles {max_right}, "
                        f"mark: {mark}, mistakes left: {mistakes_left}, mistakes right: {mistakes_right}."
                    )
                }
            ],
            temperature=0.4,
            max_tokens=150,
            top_p=1
        )
        message = response.choices[0].message.content
        print(message)
        print(f"Mark: {mark}")

        return mark, message
    
    def checkShoudlerPress(self, left_shoulder_angles, right_shoulder_angles, left_arm_is_visible, right_arm_is_visible):
        mistakes_left = 0
        mistakes_right = 0
        max_left = []
        min_left = []
        max_right = []
        min_right = []

        if left_arm_is_visible:
            filtered_left = savgol_filter(left_shoulder_angles, window_length=20, polyorder=2, mode="nearest")
            max_left = np.round(filtered_left[find_peaks(filtered_left)[0]], 0)
            min_left = np.round(filtered_left[find_peaks(-filtered_left)[0]], 0)
            for angle in max_left:
                if angle < 80: 
                    mistakes_left += 1
            for angle in min_left:
                if angle > 30:
                    mistakes_left += 1


        if right_arm_is_visible:
            filtered_right = savgol_filter(right_shoulder_angles, window_length=20, polyorder=2, mode="nearest")
            max_right = np.round(filtered_right[find_peaks(filtered_right)[0]], 0)
            min_right = np.round(filtered_right[find_peaks(-filtered_right)[0]], 0)
            for angle in max_right:
                if angle < 80:
                    mistakes_right += 1
            for angle in min_right:
                if angle > 30:
                    mistakes_right += 1


        if right_arm_is_visible and left_arm_is_visible:
            mark = 10 - 5 * (mistakes_left + mistakes_right) / min(len(min_left), len(min_right))
        elif left_arm_is_visible:
            mark = 10 - 5 * mistakes_left / len(min_left)
        elif right_arm_is_visible:
            mark = 10 - 5 * mistakes_right / len(min_right)
        else:
            mark = 0

        response = self.client.chat.completions.create(
            model="openai/gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert analyzing shoulder press exercise based on angles and marks. if an array is empty = visibility of an arm is low, mention that."
                            "Generate a clear, concise feedback message."
                },
                {
                    "role": "user",
                    "content": (
                        f"Shoulder press analysis: left min angles {min_left}, left max angles {max_left}, "
                        f"right min angles {min_right}, right max angles {max_right}, "
                        f"mark: {mark}, mistakes left: {mistakes_left}, mistakes right: {mistakes_right}."
                    )
                }
            ],
            temperature=0.4,
            max_tokens=150,
            top_p=1
        )
        message = response.choices[0].message.content
        print(message)
        print(f"Mark: {mark}")  
        return mark, message
    
    def checkLegPress(self, left_leg_angles, right_leg_angles, left_leg_is_visible, right_leg_is_visible):
        mistakes_left = 0
        mistakes_right = 0
        max_left = []
        min_left = []
        max_right = []
        min_right = []

        if left_leg_is_visible:
            filtered_left = savgol_filter(left_leg_angles, window_length=20, polyorder=2, mode="nearest")
            max_left = np.round(filtered_left[find_peaks(filtered_left)[0]], 0)
            min_left = np.round(filtered_left[find_peaks(-filtered_left)[0]], 0)
            for angle in max_left:
                if angle < 160:  
                    mistakes_left += 1
            for angle in min_left:
                if angle > 90:
                    mistakes_left += 1

        if right_leg_is_visible:
            filtered_right = savgol_filter(right_leg_angles, window_length=20, polyorder=2, mode="nearest")
            max_right = np.round(filtered_right[find_peaks(filtered_right)[0]], 0)
            min_right = np.round(filtered_right[find_peaks(-filtered_right)[0]], 0)
            for angle in max_right:
                if angle < 160:
                    mistakes_right += 1
            for angle in min_right:
                if angle > 90:
                    mistakes_right += 1


        if left_leg_is_visible and right_leg_is_visible:
            mark = 10 - 5 * (mistakes_left + mistakes_right) / min(len(min_left), len(min_right))
        elif left_leg_is_visible:
            mark = 10 - 5 * mistakes_left / len(min_left)
        elif right_leg_is_visible:
            mark = 10 - 5 * mistakes_right / len(min_right)
        else:
            mark = 0

        response = self.client.chat.completions.create(
            model="openai/gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert analyzing leg press exercise based on angles and marks. if an array is empty = visibility of a leg is low, mention that."
                            "Generate a clear, concise feedback message."
                },
                {
                    "role": "user",
                    "content": (
                        f"Squat analysis: left min angles {min_left}, left max angles {max_left}, "
                        f"right min angles {min_right}, right max angles {max_right}, "
                        f"mark: {mark}, mistakes left: {mistakes_left}, mistakes right: {mistakes_right}."
                    )   
                }
            ],
            temperature=0.4,
            max_tokens=150,
            top_p=1
        )
        message = response.choices[0].message.content
        return mark, message

    
    def getRightArm(self):

        right_shoulder = self.lmlist[12][1:3]
        right_elbow = self.lmlist[14][1:3]
        right_wrist = self.lmlist[16][1:3]
        right_arm_angle = self.findAngle(right_shoulder, right_elbow, right_wrist)
        return right_arm_angle
    
    def getLeftArm(self):

        left_shoulder = self.lmlist[11][1:3]
        left_elbow = self.lmlist[13][1:3]
        left_wrist = self.lmlist[15][1:3]
        left_arm_angle = self.findAngle(left_shoulder, left_elbow, left_wrist)
        return left_arm_angle

    def getLeftShoulder(self):
        left_shoulder = self.lmlist[11][1:3]
        left_elbow = self.lmlist[13][1:3]
        left_hip = self.lmlist[23][1:3]
        left_shoulder_angle = self.findAngle(left_elbow,left_shoulder,  left_hip)
        return left_shoulder_angle
    
    def getRightShoulder(self):
        right_shoulder = self.lmlist[12][1:3]
        right_elbow = self.lmlist[14][1:3]
        right_hip = self.lmlist[24][1:3]
        right_shoulder_angle = self.findAngle(right_elbow,right_shoulder,  right_hip)
        return right_shoulder_angle

    def getLeftLeg(self):
        left_hip = self.lmlist[23][1:3]
        left_knee = self.lmlist[25][1:3]
        left_ankle = self.lmlist[27][1:3]
        left_leg_angle = self.findAngle(left_hip, left_knee, left_ankle)
        return left_leg_angle
    
    def getRightLeg(self):
        right_hip = self.lmlist[24][1:3]
        right_knee = self.lmlist[26][1:3]
        right_ankle = self.lmlist[28][1:3]
        right_leg_angle = self.findAngle(right_hip, right_knee, right_ankle)
        return right_leg_angle