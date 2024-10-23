from transformers import pipeline

def generate_widget_from_text(user_input):
    generator = pipeline('text-generation', model='EleutherAI/gpt-neo-1.3B')

    # General-purpose prompt based on the user input
    prompt = (
        f"Write a Python function to accomplish the following task: {user_input}. "
        "The function should accept a pandas DataFrame 'df' as input if necessary and "
        "must modify it in place. Avoid unnecessary imports or unrelated code."
    )

    # Generate code using GPT-Neo
    response = generator(prompt, max_length=200, num_return_sequences=1)
    
    # Post-process: Remove extra imports, restrict to function definitions
    code = response[0]['generated_text']
    
    # Additional logic to ensure valid code can be added here
    return code
