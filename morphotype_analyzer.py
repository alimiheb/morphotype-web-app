import os
import cv2
import numpy as np
import pandas as pd
from PIL import Image
import mediapipe as mp
import math
import json
import logging
from gemini_integration import GeminiPlanGenerator

logger = logging.getLogger(__name__)

class MorphotypeAnalyzer:
    def __init__(self):
        """Initialize MediaPipe pose detection and Gemini plan generator"""
        self.mp_pose = mp.solutions.pose
        self.pose_detector = self.mp_pose.Pose(
            static_image_mode=True,
            min_detection_confidence=0.5
        )
        self.mp_drawing = mp.solutions.drawing_utils
        self.gemini_generator = GeminiPlanGenerator()
    
    def preprocess_image(self, image_path):
        """Preprocess image to remove EXIF data and convert to OpenCV format"""
        try:
            # Open with PIL and remove EXIF data
            img_pil = Image.open(image_path)
            if img_pil.mode != 'RGB':
                img_pil = img_pil.convert('RGB')
            
            # Create new image without EXIF
            img_no_exif = Image.new(img_pil.mode, img_pil.size)
            img_no_exif.putdata(list(img_pil.getdata()))
            
            # Convert to OpenCV format
            img_cv = cv2.cvtColor(np.array(img_no_exif), cv2.COLOR_RGB2BGR)
            return img_cv
        except Exception as e:
            logger.error(f"Image preprocessing error: {str(e)}")
            return None
    
    def detect_pose_landmarks(self, img_cv):
        """Detect pose landmarks using MediaPipe"""
        try:
            # Convert BGR to RGB for MediaPipe
            img_rgb = cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB)
            results = self.pose_detector.process(img_rgb)
            
            if not results.pose_landmarks:
                return None, "No pose landmarks detected. Please use a clear, full-body image."
            
            return results.pose_landmarks.landmark, None
        except Exception as e:
            logger.error(f"Pose detection error: {str(e)}")
            return None, f"Pose detection failed: {str(e)}"
    
    def calculate_body_measurements(self, landmarks):
        """Calculate body measurements from pose landmarks"""
        try:
            # Get key landmarks
            left_shoulder = landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value]
            right_shoulder = landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER.value]
            left_hip = landmarks[self.mp_pose.PoseLandmark.LEFT_HIP.value]
            right_hip = landmarks[self.mp_pose.PoseLandmark.RIGHT_HIP.value]
            nose = landmarks[self.mp_pose.PoseLandmark.NOSE.value]
            left_ankle = landmarks[self.mp_pose.PoseLandmark.LEFT_ANKLE.value]
            
            # Calculate widths (normalized coordinates)
            shoulder_width = abs(left_shoulder.x - right_shoulder.x)
            hip_width = abs(left_hip.x - right_hip.x)
            
            # Calculate depths (z-coordinate differences)
            shoulder_depth = abs(left_shoulder.z - right_shoulder.z)
            hip_depth = abs(left_hip.z - right_hip.z)
            
            # Calculate ratios
            ratio_width = hip_width / shoulder_width if shoulder_width > 0 else 0
            ratio_depth = hip_depth / shoulder_depth if shoulder_depth > 0 else 0
            ratio_3d = (ratio_width + ratio_depth) / 2
            
            # Estimate height (normalized)
            relative_height = abs(left_ankle.y - nose.y)
            
            return {
                'shoulder_width': round(shoulder_width, 4),
                'hip_width': round(hip_width, 4),
                'shoulder_depth': round(shoulder_depth, 4),
                'hip_depth': round(hip_depth, 4),
                'ratio_width': round(ratio_width, 3),
                'ratio_depth': round(ratio_depth, 3),
                'ratio_3d': round(ratio_3d, 3),
                'relative_height': round(relative_height, 4)
            }, None
            
        except Exception as e:
            logger.error(f"Body measurement calculation error: {str(e)}")
            return None, f"Failed to calculate measurements: {str(e)}"
    
    def classify_morphotype(self, measurements):
        """Classify morphotype based on body measurements"""
        ratio_3d = measurements['ratio_3d']
        
        if ratio_3d < 0.45:
            morphotype = 'Ectomorph'
            description = "Naturally lean build with narrow shoulders and hips. Fast metabolism, difficulty gaining weight."
            characteristics = [
                "Lean muscle mass",
                "Fast metabolism",
                "Narrow frame",
                "Low body fat",
                "Difficulty gaining weight"
            ]
        elif ratio_3d > 0.65:
            morphotype = 'Endomorph'
            description = "Naturally broader build with wider hips. Slower metabolism, tendency to store fat."
            characteristics = [
                "Higher body fat percentage",
                "Slower metabolism",
                "Broader frame",
                "Gains weight easily",
                "Round, soft physique"
            ]
        else:
            morphotype = 'Mesomorph'
            description = "Naturally muscular and athletic build. Balanced metabolism, builds muscle easily."
            characteristics = [
                "Naturally muscular",
                "Athletic build",
                "Balanced metabolism",
                "Builds muscle easily",
                "Well-defined physique"
            ]
        
        return {
            'type': morphotype,
            'description': description,
            'characteristics': characteristics,
            'confidence': self.calculate_confidence(ratio_3d)
        }
    
    def calculate_confidence(self, ratio_3d):
        """Calculate classification confidence"""
        if ratio_3d < 0.35 or ratio_3d > 0.75:
            return "High"
        elif ratio_3d < 0.40 or ratio_3d > 0.70:
            return "Medium"
        else:
            return "Low"
    
    def estimate_body_stats(self, measurements, age=25, gender='unknown'):
        """Estimate height and weight from measurements"""
        # Base height estimation (this is very rough)
        relative_height = measurements['relative_height']
        estimated_height_cm = relative_height * 170  # Scaling factor
        
        # Rough BMI estimation based on morphotype
        ratio_3d = measurements['ratio_3d']
        if ratio_3d < 0.45:  # Ectomorph
            estimated_bmi = 20
        elif ratio_3d > 0.65:  # Endomorph
            estimated_bmi = 26
        else:  # Mesomorph
            estimated_bmi = 23
        
        estimated_weight_kg = estimated_bmi * ((estimated_height_cm / 100) ** 2)
        
        return {
            'height_cm': round(estimated_height_cm, 1),
            'weight_kg': round(estimated_weight_kg, 1),
            'estimated_bmi': round(estimated_bmi, 1)
        }
    
    def calculate_tdee(self, weight_kg, height_cm, age, gender, activity_level):
        """Calculate Total Daily Energy Expenditure"""
        # Mifflin-St Jeor Equation
        if gender.lower() == 'male':
            bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age + 5
        else:
            bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age - 161
        
        # Activity multipliers
        activity_multipliers = {
            'sedentary': 1.2,
            'light': 1.375,
            'moderate': 1.55,
            'active': 1.725,
            'very_active': 1.9
        }
        
        multiplier = activity_multipliers.get(activity_level, 1.55)
        tdee = bmr * multiplier
        
        return {
            'bmr': round(bmr, 0),
            'tdee': round(tdee, 0),
            'activity_multiplier': multiplier
        }
    
    def analyze_image(self, image_path, age=25, gender='unknown', activity_level='moderate', goal='muscle_gain', preferences='', height=0, weight=0):
        """Main analysis function with Gemini integration"""
        try:
            # Preprocess image
            img_cv = self.preprocess_image(image_path)
            if img_cv is None:
                return {'success': False, 'error': 'Failed to process image'}
            
            # Detect pose landmarks
            landmarks, error = self.detect_pose_landmarks(img_cv)
            if landmarks is None:
                return {'success': False, 'error': error}
            
            # Calculate body measurements
            measurements, error = self.calculate_body_measurements(landmarks)
            if measurements is None:
                return {'success': False, 'error': error}
            
            # Classify morphotype
            morphotype_info = self.classify_morphotype(measurements)
            
            # Use provided height/weight or estimate if not provided
            if height > 0 and weight > 0:
                body_stats = {
                    'height_cm': height,
                    'weight_kg': weight,
                    'estimated_bmi': round(weight / ((height / 100) ** 2), 1)
                }
            else:
                body_stats = self.estimate_body_stats(measurements, age, gender)
            
            # Calculate TDEE
            energy_info = self.calculate_tdee(
                body_stats['weight_kg'],
                body_stats['height_cm'],
                age,
                gender,
                activity_level
            )
            
            # Prepare data for Gemini API
            user_data = {
                'morphotype': morphotype_info['type'],
                'height': body_stats['height_cm'],
                'weight': body_stats['weight_kg'],
                'age': age,
                'gender': gender,
                'activity_level': activity_level,
                'goal': goal,
                'preferences': preferences,
                'tdee': energy_info['tdee']
            }
            
            # Generate AI-powered plans
            ai_plans = self.gemini_generator.generate_personalized_plans(user_data)
            
            if not ai_plans['success']:
                return {'success': False, 'error': ai_plans['error']}
            
            # Debug: Print the structure to see what we're getting
            print("DEBUG - AI Plans structure:")
            print("workout_plan keys:", list(ai_plans['workout_plan'].keys()))
            print("meal_plan keys:", list(ai_plans['meal_plan'].keys()))
            
            return {
                'success': True,
                'analysis': {
                    'morphotype': morphotype_info,
                    'measurements': measurements,
                    'body_stats': body_stats,
                    'energy': energy_info,
                    'workout_plan': ai_plans['workout_plan'],  # Make sure this is correct
                    'nutrition_plan': ai_plans['meal_plan'],   # Map meal_plan to nutrition_plan
                    'additional_tips': ai_plans.get('additional_tips', []),
                    'user_info': {
                        'age': age,
                        'gender': gender,
                        'activity_level': activity_level,
                        'goal': goal,
                        'preferences': preferences,
                        'height': body_stats['height_cm'],
                        'weight': body_stats['weight_kg']
                    }
                }
            }
            
        except Exception as e:
            print(f"DEBUG - Exception in analyze_image: {str(e)}")
            import traceback
            traceback.print_exc()
            return {'success': False, 'error': f'Analysis failed: {str(e)}'}
