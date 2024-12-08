from flask import Flask, request, jsonify
import openai

app = Flask(__name__)
openai.api_key = 'your-api-key'

@app.route('/generate_recipe', methods=['POST'])
def generate_recipe():
    data = request.get_json()
    meal_type = data.get('meal_type')
    schedule_details = "Available time: Monday 6-7:30 PM, Tuesday 6-7:30 PM, ..."
    prompt = f"Based on my schedule: {schedule_details}, generate a {meal_type} recipe that fits my dietary preferences."
    
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
    
    recipe = response.choices[0].text.strip()
    return jsonify({'recipe': recipe})

if __name__ == '__main__':
    app.run(debug=True) 