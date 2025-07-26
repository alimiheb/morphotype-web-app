import os
import json
import logging
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class GeminiPlanGenerator:
    def __init__(self):
        """Initialize Gemini AI client"""
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        genai.configure(api_key=api_key)
        # Updated model name - use the correct model identifier
        self.model = genai.GenerativeModel('gemini-1.5-flash')  # or 'gemini-1.5-pro'
    
    def generate_personalized_plans(self, user_data):
        """Generate workout and meal plans using Gemini API"""
        try:
            prompt = self._create_detailed_prompt(user_data)
            
            # Add generation config for better JSON output
            generation_config = genai.types.GenerationConfig(
                temperature=0.7,
                max_output_tokens=4000,
                candidate_count=1
            )
            
            response = self.model.generate_content(
                prompt, 
                generation_config=generation_config
            )
            
            if not response.text:
                return {'success': False, 'error': 'Empty response from AI'}
            
            # Clean the response text (remove markdown code blocks if present)
            response_text = response.text.strip()
            if response_text.startswith('```json'):
                response_text = response_text[7:]  # Remove ```json
            if response_text.endswith('```'):
                response_text = response_text[:-3]  # Remove ```
            response_text = response_text.strip()
            
            # Parse the JSON response
            plan_data = json.loads(response_text)
            
            # Ensure the structure matches what the template expects
            workout_plan = plan_data.get('workout_plan', {})
            meal_plan = plan_data.get('meal_plan', {})
            
            # Add fallback structure if needed
            if 'weekly_schedule' not in workout_plan:
                workout_plan['weekly_schedule'] = {}
            if 'weekly_meals' not in meal_plan:
                meal_plan['weekly_meals'] = {}
            
            return {
                'success': True,
                'workout_plan': workout_plan,
                'meal_plan': meal_plan,  # This should be 'meal_plan', not 'nutrition_plan'
                'additional_tips': plan_data.get('additional_tips', [])
            }
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Gemini response as JSON: {str(e)}")
            logger.error(f"Raw response: {response.text[:500] if hasattr(response, 'text') else 'No response text'}...")
            return {'success': False, 'error': 'AI returned invalid JSON format'}
        except Exception as e:
            logger.error(f"Gemini API error: {str(e)}")
            return {'success': False, 'error': f'AI plan generation failed: {str(e)}'}
    
    def _create_detailed_prompt(self, user_data):
        """Create a comprehensive prompt for Gemini"""
        morphotype = user_data.get('morphotype', 'Unknown')
        height = user_data.get('height', 0)
        weight = user_data.get('weight', 0)
        age = user_data.get('age', 25)
        gender = user_data.get('gender', 'unknown')
        activity_level = user_data.get('activity_level', 'moderate')
        goal = user_data.get('goal', 'muscle_gain')
        preferences = user_data.get('preferences', '')
        
        prompt = f"""You are a world-class fitness and nutrition coach with expertise in body type analysis and personalized training.

USER PROFILE:
- Height: {height} cm
- Weight: {weight} kg
- Age: {age} years
- Gender: {gender}
- Body Type (Morphotype): {morphotype}
- Activity Level: {activity_level}
- Primary Goal: {goal}
- Additional Preferences: {preferences}

Create highly personalized workout and meal plans based on this user's specific profile.

Return your response as a valid JSON object with this exact structure:

{{
  "workout_plan": {{
    "overview": {{
      "focus": "Main training focus for this {morphotype}",
      "frequency": "X times per week",
      "duration": "X minutes per session",
      "intensity": "Beginner/Intermediate/Advanced"
    }},
    "weekly_schedule": {{
      "Monday": {{
        "type": "Upper Body Strength",
        "exercises": ["Push-ups 3x10", "Dumbbell Rows 3x12", "Shoulder Press 3x10"],
        "duration": "45 minutes",
        "notes": "Focus on form over weight"
      }},
      "Tuesday": {{
        "type": "Cardio",
        "exercises": ["Running 20 min", "Jump rope 10 min", "Cool down walk 5 min"],
        "duration": "35 minutes",
        "notes": "Moderate intensity"
      }},
      "Wednesday": {{
        "type": "Lower Body Strength",
        "exercises": ["Squats 3x12", "Lunges 3x10 each leg", "Calf raises 3x15"],
        "duration": "40 minutes",
        "notes": "Focus on proper squat depth"
      }},
      "Thursday": {{
        "type": "Active Recovery",
        "exercises": ["Yoga 30 min", "Light stretching", "Walk 15 min"],
        "duration": "45 minutes",
        "notes": "Low intensity recovery"
      }},
      "Friday": {{
        "type": "Full Body Circuit",
        "exercises": ["Burpees 3x8", "Mountain climbers 3x20", "Plank 3x30sec"],
        "duration": "35 minutes",
        "notes": "High intensity, short rest"
      }},
      "Saturday": {{
        "type": "Cardio + Core",
        "exercises": ["Cycling 25 min", "Crunches 3x15", "Russian twists 3x20"],
        "duration": "40 minutes",
        "notes": "Maintain steady pace"
      }},
      "Sunday": {{
        "type": "Rest Day",
        "exercises": ["Light walk", "Gentle stretching"],
        "duration": "Optional 20 minutes",
        "notes": "Complete rest or very light activity"
      }}
    }},
    "key_principles": ["Progressive overload", "Proper form", "Adequate rest"]
  }},
  "meal_plan": {{
    "daily_targets": {{
      "calories": 2200,
      "protein_g": 120,
      "carbs_g": 250,
      "fats_g": 80
    }},
    "weekly_meals": {{
      "Monday": {{
        "breakfast": {{
          "meal": "Oatmeal with berries and protein powder",
          "calories": 350,
          "prep_time": "5 minutes"
        }},
        "lunch": {{
          "meal": "Grilled chicken salad with quinoa",
          "calories": 450,
          "prep_time": "15 minutes"
        }},
        "dinner": {{
          "meal": "Salmon with roasted vegetables",
          "calories": 500,
          "prep_time": "20 minutes"
        }},
        "snacks": {{
          "meal": "Greek yogurt with nuts",
          "calories": 200,
          "prep_time": "2 minutes"
        }}
      }},
      "Tuesday": {{
        "breakfast": {{"meal": "Scrambled eggs with spinach", "calories": 300, "prep_time": "8 minutes"}},
        "lunch": {{"meal": "Turkey wrap with vegetables", "calories": 400, "prep_time": "10 minutes"}},
        "dinner": {{"meal": "Lean beef stir-fry with rice", "calories": 550, "prep_time": "25 minutes"}},
        "snacks": {{"meal": "Apple with almond butter", "calories": 180, "prep_time": "2 minutes"}}
      }},
      "Wednesday": {{
        "breakfast": {{"meal": "Protein smoothie with banana", "calories": 320, "prep_time": "5 minutes"}},
        "lunch": {{"meal": "Tuna salad with whole grain bread", "calories": 420, "prep_time": "10 minutes"}},
        "dinner": {{"meal": "Chicken breast with sweet potato", "calories": 480, "prep_time": "30 minutes"}},
        "snacks": {{"meal": "Mixed nuts and dried fruit", "calories": 220, "prep_time": "1 minute"}}
      }},
      "Thursday": {{
        "breakfast": {{"meal": "Avocado toast with egg", "calories": 340, "prep_time": "8 minutes"}},
        "lunch": {{"meal": "Lentil soup with bread", "calories": 380, "prep_time": "5 minutes"}},
        "dinner": {{"meal": "Grilled fish with quinoa salad", "calories": 520, "prep_time": "25 minutes"}},
        "snacks": {{"meal": "Cottage cheese with berries", "calories": 160, "prep_time": "3 minutes"}}
      }},
      "Friday": {{
        "breakfast": {{"meal": "Greek yogurt parfait", "calories": 310, "prep_time": "5 minutes"}},
        "lunch": {{"meal": "Chicken Caesar salad", "calories": 440, "prep_time": "10 minutes"}},
        "dinner": {{"meal": "Pork tenderloin with vegetables", "calories": 490, "prep_time": "35 minutes"}},
        "snacks": {{"meal": "Protein bar", "calories": 200, "prep_time": "0 minutes"}}
      }},
      "Saturday": {{
        "breakfast": {{"meal": "Pancakes with protein powder", "calories": 360, "prep_time": "15 minutes"}},
        "lunch": {{"meal": "Beef and vegetable soup", "calories": 410, "prep_time": "5 minutes"}},
        "dinner": {{"meal": "Grilled chicken with pasta", "calories": 540, "prep_time": "20 minutes"}},
        "snacks": {{"meal": "Trail mix", "calories": 190, "prep_time": "1 minute"}}
      }},
      "Sunday": {{
        "breakfast": {{"meal": "Omelet with vegetables", "calories": 330, "prep_time": "12 minutes"}},
        "lunch": {{"meal": "Quinoa bowl with beans", "calories": 430, "prep_time": "15 minutes"}},
        "dinner": {{"meal": "Baked cod with rice", "calories": 460, "prep_time": "25 minutes"}},
        "snacks": {{"meal": "Dark chocolate and almonds", "calories": 180, "prep_time": "1 minute"}}
      }}
    }},
    "nutrition_guidelines": ["Eat protein with every meal", "Stay hydrated with 8+ glasses water", "Include vegetables in lunch and dinner"]
  }},
  "additional_tips": ["Get 7-9 hours of sleep", "Track your progress weekly", "Listen to your body and rest when needed"]
}}

CRITICAL REQUIREMENTS:
- Return ONLY the JSON object, no other text
- Ensure all JSON syntax is perfect
- Customize everything for the {morphotype} body type
- Make calorie targets appropriate for {goal}
- Consider {activity_level} activity level
- All exercises should be practical and achievable"""

        return prompt

    def list_available_models(self):
        """Helper method to list available models"""
        try:
            models = genai.list_models()
            available_models = []
            for model in models:
                if 'generateContent' in model.supported_generation_methods:
                    available_models.append(model.name)
            return available_models
        except Exception as e:
            logger.error(f"Error listing models: {str(e)}")
            return []