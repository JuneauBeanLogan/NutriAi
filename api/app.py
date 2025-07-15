import math
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

def calculate_bmi(weight_kg, height_cm):
    height_m = height_cm / 100
    return weight_kg / (height_m ** 2)

def estimate_calories(age, weight_kg, height_cm, gender, activity_level, goal):
    if gender.lower() == 'male':
        bmr = 88.362 + (13.397 * weight_kg) + (4.799 * height_cm) - (5.677 * age)
    else:
        bmr = 447.593 + (9.247 * weight_kg) + (3.098 * height_cm) - (4.330 * age)
    
    activity_multipliers = {
        'sedentary': 1.2,
        'lightly active': 1.375,
        'moderately active': 1.55,
        'very active': 1.725,
        'super active': 1.9
    }
    multiplier = activity_multipliers.get(activity_level.lower(), 1.2)
    
    calories = bmr * multiplier
    
    goal_adjustments = {
        'loss': -500,
        'maintenance': 0,
        'gain': 500
    }
    adjustment = goal_adjustments.get(goal.lower(), 0)
    return math.ceil(calories + adjustment)

def allocate_macros(calories, goal):
    if goal.lower() == 'loss':
        protein_ratio, carb_ratio, fat_ratio = 0.3, 0.4, 0.3
    elif goal.lower() == 'gain':
        protein_ratio, carb_ratio, fat_ratio = 0.25, 0.55, 0.2
    else:
        protein_ratio, carb_ratio, fat_ratio = 0.3, 0.45, 0.25
    
    protein_g = (protein_ratio * calories) / 4
    carb_g = (carb_ratio * calories) / 4
    fat_g = (fat_ratio * calories) / 9
    
    return round(protein_g), round(carb_g), round(fat_g)

def get_location_suggestions(location="US"):
    """Get location-based food suggestions"""
    location_foods = {
        'US': ['Quinoa salad', 'Grilled chicken', 'Sweet potato', 'Avocado toast'],
        'Mediterranean': ['Greek yogurt', 'Olive oil', 'Feta cheese', 'Tomatoes'],
        'Asian': ['Brown rice', 'Tofu', 'Seaweed', 'Green tea'],
        'Indian': ['Lentils', 'Curry vegetables', 'Basmati rice', 'Yogurt'],
        'Mexican': ['Black beans', 'Quinoa', 'Avocado', 'Salsa verde']
    }
    return location_foods.get(location, location_foods['US'])

def suggest_meal(meal_type, location="US"):
    location_foods = get_location_suggestions(location)
    
    meals = {
        'breakfast': f'Oatmeal with fruits and nuts, {location_foods[0]}',
        'lunch': f'Grilled chicken salad with {location_foods[1]}',
        'dinner': f'Salmon with veggies and {location_foods[2]}',
        'snack': f'Greek yogurt with berries and {location_foods[3]}'
    }
    return meals.get(meal_type.lower(), f'Balanced meal with {location_foods[0]}')

def convert_units(weight, height, unit_system):
    """Convert between metric and imperial units"""
    if unit_system == 'imperial':
        # Convert lbs to kg, inches to cm
        weight_kg = weight * 0.453592
        height_cm = height * 2.54
    else:
        # Already in metric
        weight_kg = weight
        height_cm = height
    
    return weight_kg, height_cm

@app.route('/plan', methods=['POST'])
def get_plan():
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        age = data.get('age')
        weight = data.get('weight')
        height = data.get('height')
        gender = data.get('gender')
        activity_level = data.get('activity_level')
        goal = data.get('goal')
        meal_type = data.get('meal_type', 'dinner')
        unit_system = data.get('unit_system', 'metric')
        location = data.get('location', 'US')
        
        if not all([age, weight, height, gender, activity_level, goal]):
            return jsonify({'error': 'Missing required parameters'}), 400
        
        # Convert units if needed
        weight_kg, height_cm = convert_units(weight, height, unit_system)
        
        bmi = calculate_bmi(weight_kg, height_cm)
        calories = estimate_calories(age, weight_kg, height_cm, gender, activity_level, goal)
        protein, carbs, fats = allocate_macros(calories, goal)
        meal = suggest_meal(meal_type, location)
        location_suggestions = get_location_suggestions(location)
        
        return jsonify({
            'bmi': round(bmi, 2),
            'daily_calories': calories,
            'macros': {'protein': protein, 'carbs': carbs, 'fats': fats},
            'sample_meal': f'{meal_type.capitalize()}: {meal}',
            'location_suggestions': location_suggestions,
            'unit_system': unit_system,
            'location': location
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'message': 'NutriAI API is running'})

@app.route('/', methods=['GET'])
def root():
    return jsonify({'message': 'NutriAI API', 'version': '1.0.0'})

# This is required for Vercel serverless functions
# The app object must be available at module level

if __name__ == '__main__':
    app.run(debug=True)
