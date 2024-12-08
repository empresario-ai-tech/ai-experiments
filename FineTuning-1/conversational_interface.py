import json

def collect_data():
    data = {
        "cooking_style": {},
        "detailed_recipes": [],
        "weekly_schedule_planning": {}
    }

    # Collect Cooking Style
    print("Let's begin with your favorite cuisines and dishes.")
    data["cooking_style"]["favorite_cuisines"] = input("1. What are your favorite cuisines? (e.g., Italian, Thai, Mexican): ").split(', ')
    data["cooking_style"]["signature_dishes"] = input("2. Can you share some signature dishes that you frequently cook or excel at?: ").split(', ')

    print("\nDietary Preferences and Restrictions")
    dietary = input("1. Do you follow any specific diet? (e.g., Vegetarian, Vegan, Keto, Paleo): ")
    data["cooking_style"]["dietary_preferences"] = [diet.strip() for diet in dietary.split(',')]
    allergies = input("2. Do you have any food allergies or intolerances?: ").split(', ')
    data["cooking_style"]["allergies"] = [allergy.strip() for allergy in allergies]

    print("\nPreferred Ingredients")
    data["cooking_style"]["preferred_ingredients"] = input("1. What are your preferred ingredients? (list): ").split(', ')
    data["cooking_style"]["ingredients_to_avoid"] = input("2. Are there any ingredients you dislike or prefer not to use?: ").split(', ')

    print("\nCooking Methods and Equipment")
    data["cooking_style"]["preferred_cooking_methods"] = input("1. What are your preferred cooking methods? (e.g., Grilling, Baking, Sautéing): ").split(', ')
    data["cooking_style"]["kitchen_equipment"] = input("2. Do you use any specific kitchen tools or appliances regularly?: ").split(', ')

    print("\nFlavor Profiles")
    data["cooking_style"]["favorite_spices_and_herbs"] = input("1. Which spices and herbs do you frequently use?: ").split(', ')
    flavors = input("2. What are your flavor preferences? (e.g., Spicy, Sweet, Savory): ").split(', ')
    data["cooking_style"]["flavor_preferences"] = [flavor.strip() for flavor in flavors]

    print("\nMeal Types and Timing")
    data["cooking_style"]["meal_frequency"] = input("1. How many meals do you typically prepare each day? (e.g., 3 meals, 2 meals + 2 snacks): ")
    breakfast = input("2. What time do you have breakfast? ")
    lunch = input("   What time do you have lunch? ")
    dinner = input("   What time do you have dinner? ")
    snacks = input("   What times do you have snacks? (comma-separated): ")
    data["cooking_style"]["typical_meal_times"] = {
        "breakfast": breakfast,
        "lunch": lunch,
        "dinner": dinner,
        "snacks": [snack.strip() for snack in snacks.split(',')]
    }
    data["cooking_style"]["portion_sizes"] = input("3. How would you describe your portion sizes? (e.g., Generous, Moderate, Small): ")
    data["cooking_style"]["serving_style"] = input("4. What is your preferred serving style? (Individual servings, Family-style, Buffet-style): ")

    # Collect Detailed Recipes
    while True:
        print("\nLet's add a recipe.")
        recipe = {}
        recipe["name"] = input("1. What's the name of the recipe?: ")
        ingredients = []
        print("2. Enter the ingredients (type 'done' when finished):")
        while True:
            ingredient = input("   Ingredient: ")
            if ingredient.lower() == 'done':
                break
            quantity = input("   Quantity: ")
            ingredients.append({"ingredient": ingredient, "quantity": quantity})
        recipe["ingredients"] = ingredients
        recipe["instructions"] = input("3. Can you provide the step-by-step instructions for preparing this dish?: ")
        recipe["tips"] = input("4. Any tips or variations you'd like to include? (Optional): ")
        data["detailed_recipes"].append(recipe)
        more = input("5. Would you like to add another recipe? (yes/no): ")
        if more.lower() != 'yes':
            break

    # Collect Weekly Schedule
    print("\nWeekly Schedule Planning")
    data["weekly_schedule_planning"]["daily_cooking_availability"] = {}
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    for day in days:
        availability = input(f"{day} - Available Time: ")
        data["weekly_schedule_planning"]["daily_cooking_availability"][day] = availability

    data["weekly_schedule_planning"]["cooking_duration"] = {
        "weekdays": input("How much time can you allocate to meal preparation on weekdays? (e.g., 1-1.5 hours): "),
        "weekends": input("How much time can you allocate to meal preparation on weekends? (e.g., 3 hours): ")
    }
    data["weekly_schedule_planning"]["work_schedule"] = input("What are your work hours? (e.g., Monday to Friday: 9:00 AM - 5:00 PM): ")
    exercise_hobbies = input("Do you have any exercise or hobbies? Please specify: ")
    data["weekly_schedule_planning"]["exercise_and_hobbies"] = exercise_hobbies.split(', ')
    data["weekly_schedule_planning"]["meal_planning_preferences"] = input("How far in advance do you like to plan your meals? (e.g., Weekly, Bi-weekly): ")
    flexibility = input("How flexible is your meal schedule? (Highly Flexible, Moderately Flexible, Rigid): ")
    data["weekly_schedule_planning"]["schedule_flexibility"] = flexibility
    print("\nGrocery Shopping Habits")
    frequency = input("How often do you go grocery shopping? (Daily, Weekly, Bi-Weekly, Monthly): ")
    preferred_days_times = input("What are your preferred days and times for shopping?: ")
    data["weekly_schedule_planning"]["grocery_shopping_habits"] = {
        "frequency": frequency,
        "preferred_days_times": preferred_days_times
    }
    batch_cooking = input("Do you practice batch cooking or meal prepping? (yes/no): ")
    if batch_cooking.lower() == 'yes':
        practices = input("Please describe your practices: ")
        storage = input("How do you store your prepped meals? (e.g., Glass containers, Freezer bags): ").split(', ')
        data["weekly_schedule_planning"]["batch_cooking_and_meal_prep"] = {
            "engaged": True,
            "practices": practices,
            "storage_preferences": storage
        }
    else:
        data["weekly_schedule_planning"]["batch_cooking_and_meal_prep"] = {
            "engaged": False
        }

    # Save Data to JSON
    with open('user_conversational_preferences.json', 'w') as f:
        json.dump(data, f, indent=4)
    
    print("\nThank you! Your preferences have been saved.")
    
if __name__ == "__main__":
    collect_data() 