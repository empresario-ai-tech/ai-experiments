import openai

openai.api_key = 'your-api-key'

def generate_custom_recipe(meal_type, schedule_details):
    prompt = (
        f"Based on my schedule: {schedule_details}, generate a {meal_type} recipe that fits my dietary preferences."
    )
    response = openai.Completion.create(
        model='your-fine-tuned-model',
        prompt=prompt,
        max_tokens=250,
        temperature=0.7,
        top_p=0.9,
        frequency_penalty=0,
        presence_penalty=0.6,
        stop=["\n\n"]
    )
    return response.choices[0].text.strip()

if __name__ == "__main__":
    meal_type = input("Enter meal type (e.g., dinner, lunch): ")
    schedule_details = "Available time: Monday 6-7:30 PM, Tuesday 6-7:30 PM, ..."
    recipe = generate_custom_recipe(meal_type, schedule_details)
    print(recipe)