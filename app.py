import math
from flask import Flask, request, jsonify

app = Flask(__name__)

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

def suggest_meal(meal_type):
    meals = {
        'breakfast': 'Oatmeal with fruits and nuts',
        'lunch': 'Grilled chicken salad',
        'dinner': 'Salmon with veggies',
        'snack': 'Greek yogurt with berries'
    }
    return meals.get(meal_type.lower(), 'Balanced meal option')

@app.route('/plan', methods=['POST'])
def get_plan():
    data = request.json
    age = data.get('age')
    weight_kg = data.get('weight_kg')
    height_cm = data.get('height_cm')
    gender = data.get('gender')
    activity_level = data.get('activity_level')
    goal = data.get('goal')
    meal_type = data.get('meal_type', 'dinner')
    
    if not all([age, weight_kg, height_cm, gender, activity_level, goal]):
        return jsonify({'error': 'Missing required parameters'}), 400
    
    bmi = calculate_bmi(weight_kg, height_cm)
    calories = estimate_calories(age, weight_kg, height_cm, gender, activity_level, goal)
    protein, carbs, fats = allocate_macros(calories, goal)
    meal = suggest_meal(meal_type)
    
    return jsonify({
        'bmi': round(bmi, 2),
        'daily_calories': calories,
        'macros': {'protein': protein, 'carbs': carbs, 'fats': fats},
        'sample_meal': f'{meal_type.capitalize()}: {meal}'
    })

if __name__ == '__main__':
    app.run(debug=True)
