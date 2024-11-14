from openai import OpenAI
import config

def create_code_teacher():
    client = OpenAI(api_key=config.OPENAI_API_KEY)
    
    # Create a simple coding assistant
    assistant = client.beta.assistants.create(
        name="Code Teacher",
        instructions="""You are a helpful coding teacher. When given code:
        1. Explain what the code does
        2. Point out any bugs
        3. Suggest improvements
        Always explain concepts in simple terms with examples.""",
        tools=[{"type": "code_interpreter"}],
        model="gpt-4-turbo-preview"
    )
    
    # Create a thread for the conversation
    thread = client.beta.threads.create()
    
    return client, assistant, thread

def ask_code_question(client, assistant, thread, code_question):
    # Add the student's question to the thread
    client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=code_question
    )
    
    # Run the assistant
    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant.id
    )
    
    # Wait for the response
    while True:
        run_status = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id
        )
        if run_status.status == 'completed':
            break
    
    # Get the assistant's response
    messages = client.beta.threads.messages.list(thread_id=thread.id)
    return messages.data[0].content[0].text.value

# Example usage
if __name__ == "__main__":
    # Initialize the teacher
    client, assistant, thread = create_code_teacher()
    
    # Example code to review
    code_to_review = """
    def find_largest(numbers):
        largest = numbers[0]
        for num in numbers:
            if num > largest:
                largest = num
        return largest
    """
    
    # Ask for help with the code
    response = ask_code_question(
        client, 
        assistant, 
        thread,
        f"Can you explain this code and suggest any improvements?\n{code_to_review}"
    )
    print(response)