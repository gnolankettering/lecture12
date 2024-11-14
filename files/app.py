from openai import OpenAI
import config
import re

client = OpenAI(api_key=config.OPENAI_API_KEY)

#create assistant
assistant = client.beta.assistants.create(
    name="LLM Researcher Assistant",
    instructions="You're an LLM researcher who answers questions about research papers on LLM and Generative AI",
    tools=[{"type": "code_interpreter"},{"type": "file_search"}],
    model="gpt-4-turbo-preview",
)

# Add the files to the assistant's file search tool
vector_store = client.beta.vector_stores.create(name="Financial Statements")
file_paths = ["data/language_models_are_unsupervised_multitask_learners.pdf"]
file_streams = [open(path, "rb") for path in file_paths]
file_batch = client.beta.vector_stores.file_batches.upload_and_poll(
    vector_store_id=vector_store.id, files=file_streams
)
assistant = client.beta.assistants.update(
  assistant_id=assistant.id,
  tool_resources={"file_search": {"vector_store_ids": [vector_store.id]}},
) 

# create a thread
thread = client.beta.threads.create()

# create a message on the thread
message = client.beta.threads.messages.create(
    thread_id=thread.id,
    role="user",
    content="What are some cool math concepts behind this ML paper pdf? Explain in two sentences",
)

# run and poll the assistant
run = client.beta.threads.runs.create_and_poll(
    thread_id=thread.id,
    assistant_id=assistant.id,
)

if run.status == "completed":
    messages = client.beta.threads.messages.list(thread_id=thread.id)
    print(messages)


