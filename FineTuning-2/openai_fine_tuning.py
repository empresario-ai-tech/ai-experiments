import openai
import json

openai.api_key = 'your-api-key'

def prepare_training_data(file_path='path/to/user_data_commercial.json'):
    with open(file_path, 'r') as f:
        data = json.load(f)
    training_data = []
    for doc in data['documents']:
        prompt = f"Recipe Name: {doc['title']}\nIngredients: {doc['content']}\n"
        completion = doc['content']
        training_data.append({"prompt": prompt, "completion": completion})
    return training_data

def upload_files(training_data, training_file='training_data.jsonl'):
    with open(training_file, 'w') as f:
        for item in training_data:
            f.write(json.dumps(item) + '\n')
    response = openai.File.create(
        file=open(training_file),
        purpose='fine-tune'
    )
    return response['id']

def fine_tune_model(file_id, model='davinci'):
    response = openai.FineTune.create(
        training_file=file_id,
        model=model,
        n_epochs=4,
        batch_size=2
    )
    return response

if __name__ == "__main__":
    training_data = prepare_training_data()
    file_id = upload_files(training_data)
    fine_tune_response = fine_tune_model(file_id)
    print(f"Fine-tuning started: {fine_tune_response}")