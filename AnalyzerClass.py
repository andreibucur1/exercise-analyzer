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
        left_arm_is_visible = True
        right_arm_is_visible = True
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
                if(self.lmlist[13][3] < VISIBILITY):
                    left_arm_is_visible = False
                if(self.lmlist[14][3] < VISIBILITY):    
                    right_arm_is_visible = False
                

            cv2.imshow("Image", img)
            cv2.waitKey(1)
        
        
        match exercise:
            case "bicepCurl":
                mark, message = self.checkBicepCurl(l_arm_angles, r_arm_angles, left_arm_is_visible, right_arm_is_visible)
            case "tricepExtension":
                mark, message = self.checkTricepExtension(l_arm_angles, r_arm_angles)
            case "lateralRaise":
                mark, message = self.checkLateralRaises(l_shoulder_angles, r_shoulder_angles)
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
            max_tokens=4096,
            top_p=1
        )
        print(response.choices[0].message.content)
        print(f"Mark: {mark}")
        message = response.choices[0].message.content
        return mark, message

    def checkTricepExtension(self, left_arm_angles, right_arm_angles):
        
    
        
        filtered_left_angles = savgol_filter(left_arm_angles, window_length=20, polyorder=2, mode= "nearest")
        filtered_right_angles = savgol_filter(right_arm_angles, window_length=20, polyorder=2,  mode= "nearest")

        max_left_id = find_peaks(filtered_left_angles)[0]
        max_right_id = find_peaks(filtered_right_angles)[0]

        min_left_id = find_peaks(-filtered_left_angles)[0]
        min_right_id = find_peaks(-filtered_right_angles)[0]


        # plt.figure(figsize=(12, 6))
        # plt.plot(left_arm_angles, label='Unghi Dreapta Brut', alpha=0.7, color = 'blue')
        # plt.plot(filtered_left_angles, label='Unghi Dreapta Prelucrat', alpha=0.7, color = 'red')
        # # plt.plot(right_arm_angles, label='Unghi Dreapta Brut', alpha=0.7, color = 'blue')
        # # plt.plot(filtered_right_angles, label='Unghi Dreapta Prelucrat', alpha=0.7, color = 'red')
        # plt.show()


        not_low_enough_l = 0
        not_high_enough_l = 0

        not_low_enough_r = 0
        not_high_enough_r = 0

        mark_l = 0
        mark_r = 0



        if len(min_left_id) < len(max_left_id):
            rep_capture_error = 1
            index_number_l = len(min_left_id)
        else:
            rep_capture_error = 0
            index_number_l = len(max_left_id)

        for i in range(index_number_l):
            if filtered_left_angles[max_left_id[i + rep_capture_error]] < 165:
                not_low_enough_l += 1
            if filtered_left_angles[min_left_id[i]] > 90:
                not_high_enough_l += 1

        number_of_mistakes_l = not_high_enough_l + not_low_enough_l
        mark_l = 10 - 5 * number_of_mistakes_l / index_number_l





        if len(min_right_id) < len(max_right_id):
            rep_capture_error = 1
            index_number_r = len(min_right_id)
        else:
            rep_capture_error = 0
            index_number_r = len(max_right_id)

        for i in range(index_number_r):
            if filtered_right_angles[max_right_id[i + rep_capture_error]] < 165:
                not_low_enough_r += 1
            if filtered_right_angles[min_right_id[i ]] > 70:
                not_high_enough_r += 1
        number_of_mistakes_r = not_high_enough_r + not_low_enough_r
        mark_r = 10 - 5 * number_of_mistakes_r / index_number_r


        mark = (mark_r+mark_l)/2
        
        if not_low_enough_l == 0 and not_high_enough_l == 0 and not_low_enough_r == 0 and not_high_enough_r == 0:
            message = "Perfect form!"
        elif (not_low_enough_l != 0 or not_low_enough_r != 0) and (not_high_enough_l != 0 and not_high_enough_r != 0):
            message = "You need to work on your form, try to lower your arms more and raise them higher."
        elif not_low_enough_l != 0 or not_low_enough_r != 0:
            message = "You need to work on your form, try to lower your arms more." 
        else:
            message = "You need tro work on your form, try to raise your arms higher."   
        
        return mark, message
    
    def checkLateralRaises(self, left_shoulder_angles, right_shoulder_angles):
        filtered_left_angles = savgol_filter(left_shoulder_angles, window_length=20, polyorder=2, mode= "nearest")
        filtered_right_angles = savgol_filter(right_shoulder_angles, window_length=20, polyorder=2,  mode= "nearest")

        max_left_id = find_peaks(filtered_left_angles)[0]
        max_right_id = find_peaks(filtered_right_angles)[0]

        min_left_id = find_peaks(-filtered_left_angles)[0]
        min_right_id = find_peaks(-filtered_right_angles)[0]


        # plt.figure(figsize=(12, 6))
        # plt.plot(left_shoulder_angles, label='Unghi Dreapta Brut', alpha=0.7, color = 'blue')
        # plt.plot(filtered_left_angles, label='Unghi Dreapta Prelucrat', alpha=0.7, color = 'red')
        # # plt.plot(right_arm_angles, label='Unghi Dreapta Brut', alpha=0.7, color = 'blue')
        # # plt.plot(filtered_right_angles, label='Unghi Dreapta Prelucrat', alpha=0.7, color = 'red')
        # plt.show()


        not_low_enough_l = 0
        not_high_enough_l = 0

        not_low_enough_r = 0
        not_high_enough_r = 0

        mark_l = 0
        mark_r = 0



        if len(min_left_id) < len(max_left_id):
            rep_capture_error = 1
            index_number_l = len(min_left_id)
        else:
            rep_capture_error = 0
            index_number_l = len(max_left_id)

        for i in range(index_number_l):
            if filtered_left_angles[max_left_id[i+ rep_capture_error]] < 80:
                not_low_enough_l += 1
            if filtered_left_angles[min_left_id[i ]] > 30:
                not_high_enough_l += 1

        number_of_mistakes_l = not_high_enough_l + not_low_enough_l
        mark_l = 10 - 5 * number_of_mistakes_l / index_number_l





        if len(min_right_id) <= len(max_right_id):
            rep_capture_error = 0
            index_number_r = len(min_right_id)
        else:
            rep_capture_error = 1
            index_number_r = len(max_right_id)

        for i in range(index_number_r):
            if filtered_right_angles[max_right_id[i]] < 80:
                not_low_enough_r += 1
            if filtered_right_angles[min_right_id[i + rep_capture_error]] > 30:
                not_high_enough_r += 1
        number_of_mistakes_r = not_high_enough_r + not_low_enough_r
        mark_r = 10 - 5 * number_of_mistakes_r / index_number_r


        mark = (mark_r+mark_l)/2
        
        if not_low_enough_l == 0 and not_high_enough_l == 0 and not_low_enough_r == 0 and not_high_enough_r == 0:
            message = "Perfect form!"
        elif (not_low_enough_l != 0 or not_low_enough_r != 0) and (not_high_enough_l != 0 and not_high_enough_r != 0):
            message = "You need to work on your form, try to lower your arms more and raise them higher."
        elif not_low_enough_l != 0 or not_low_enough_r != 0:
            message = "You need to work on your form, try to lower your arms more." 
        else:
            message = "You need tro work on your form, try to raise your arms higher."
        print(not_high_enough_l, not_high_enough_r, not_low_enough_l, not_low_enough_r)   
        
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