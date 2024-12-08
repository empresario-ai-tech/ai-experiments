from transformers import GPT2Tokenizer, GPT2LMHeadModel, Trainer, TrainingArguments
import pandas as pd

def fine_tune_model(recipe_df, model_name='gpt2', output_dir='./personalized_model'):
    tokenizer = GPT2Tokenizer.from_pretrained(model_name)
    model = GPT2LMHeadModel.from_pretrained(model_name)

    # Prepare the dataset
    texts = recipe_df['instructions'].tolist()
    encodings = tokenizer('\n\n'.join(texts), return_tensors='pt', max_length=512, truncation=True)

    # Define training arguments
    training_args = TrainingArguments(
        output_dir=output_dir,
        num_train_epochs=3,
        per_device_train_batch_size=2,
        warmup_steps=500,
        weight_decay=0.01,
        logging_dir='./logs',
    )

    # Initialize Trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=encodings['input_ids'],
    )

    # Train the model
    trainer.train()
    trainer.save_pretrained(output_dir) 