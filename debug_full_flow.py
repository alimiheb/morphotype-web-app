from morphotype_analyzer import MorphotypeAnalyzer
import json
import traceback

def debug_full_analysis():
    try:
        print("🔍 Starting full analysis debug...")
        
        # Test the full flow like the web app does
        analyzer = MorphotypeAnalyzer()
        
        # Use a test image path (you might need to adjust this)
        test_image = "static/uploads/user_image.jpg"  # or any valid image path
        
        result = analyzer.analyze_image(
            test_image,
            age=25,
            gender='male',
            activity_level='moderate',
            goal='muscle_gain',
            preferences='No seafood',
            height=175,
            weight=65
        )
        
        if result['success']:
            print("✅ Analysis successful!")
            analysis = result['analysis']
            
            print("\n=== ANALYSIS STRUCTURE ===")
            print("Top-level keys:", list(analysis.keys()))
            
            if 'workout_plan' in analysis:
                print("\n=== WORKOUT PLAN KEYS ===")
                print(list(analysis['workout_plan'].keys()))
                
            if 'nutrition_plan' in analysis:
                print("\n=== NUTRITION PLAN KEYS ===")
                print(list(analysis['nutrition_plan'].keys()))
                
            # Check for the problematic field
            wp = analysis.get('workout_plan', {})
            if 'weekly_plan' in wp:
                print("❌ FOUND PROBLEM: workout_plan has 'weekly_plan' key")
            if 'weekly_schedule' in wp:
                print("✅ GOOD: workout_plan has 'weekly_schedule' key")
                
        else:
            print("❌ Analysis failed:", result['error'])
            
    except Exception as e:
        print(f"❌ Debug failed: {str(e)}")
        print("\n=== FULL TRACEBACK ===")
        traceback.print_exc()

if __name__ == "__main__":
    debug_full_analysis()