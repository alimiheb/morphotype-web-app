from gemini_integration import GeminiPlanGenerator
import json

def debug_gemini_response():
    try:
        generator = GeminiPlanGenerator()
        
        test_data = {
            'morphotype': 'Ectomorph',
            'height': 175,
            'weight': 65,
            'age': 25,
            'gender': 'male',
            'activity_level': 'moderate',
            'goal': 'muscle_gain',
            'preferences': 'No seafood'
        }
        
        result = generator.generate_personalized_plans(test_data)
        
        if result['success']:
            print("✅ Success! Here's the structure:")
            print("\n=== WORKOUT PLAN STRUCTURE ===")
            print(json.dumps(result['workout_plan'], indent=2))
            print("\n=== MEAL PLAN STRUCTURE ===")
            print(json.dumps(result['meal_plan'], indent=2))
            
            # Check for expected fields
            wp = result['workout_plan']
            mp = result['meal_plan']
            
            print("\n=== FIELD CHECKS ===")
            print(f"workout_plan has 'weekly_schedule': {'weekly_schedule' in wp}")
            print(f"meal_plan has 'weekly_meals': {'weekly_meals' in mp}")
            print(f"workout_plan keys: {list(wp.keys())}")
            print(f"meal_plan keys: {list(mp.keys())}")
            
        else:
            print("❌ Error:", result['error'])
            
    except Exception as e:
        print(f"❌ Debug failed: {str(e)}")

if __name__ == "__main__":
    debug_gemini_response()