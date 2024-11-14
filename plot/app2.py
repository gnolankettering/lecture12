from openai import OpenAI
import config
import re

client = OpenAI(api_key=config.OPENAI_API_KEY)

# Quick helper function to convert our output file to a png
def convert_file_to_png(file_id, write_path):
    data = client.files.content(file_id)
    data_bytes = data.read()
    with open(write_path, "wb") as file:
        file.write(data_bytes)

# Add the files to the assistant's file search tool
vector_store = client.beta.vector_stores.create(name="Financial Statements")
file_paths = ["data/NotRealCorp_financial_data.json"]
file_streams = [open(path, "rb") for path in file_paths]
file_batch = client.beta.vector_stores.file_batches.upload_and_poll(
    vector_store_id=vector_store.id, files=file_streams
)

#create assistant
assistant = client.beta.assistants.create(
    name="Data Scientist Assistant",
    instructions="You are a data scientist assistant. When given data and a query, \
        write the proper code and create the proper visualization",
    tools=[{"type": "code_interpreter"},{"type": "file_search"}],
    tool_resources={"file_search": {"vector_store_ids": [vector_store.id]}},
    model="gpt-4-turbo-preview",
)


# create a thread
thread = client.beta.threads.create()

# create a message on the thread
message = client.beta.threads.messages.create(
    thread_id=thread.id,
    role="user",
    content="Calculate profit (revenue minus cost) by quarter and year, \
        and visualize as a line plot across the distribution channels, \
            where the colors of the lines are green, light red, and light blue",
)

# run and poll the assistant
run = client.beta.threads.runs.create_and_poll(
    thread_id=thread.id,
    assistant_id=assistant.id,
)

if run.status == "completed":
    messages = client.beta.threads.messages.list(thread_id=thread.id)
    print(messages)
    match = re.search(r"file_id='(file-[\w\d]+)'", messages.toString())
    plot_file_id = match.group(1) if match else None
    image_path = "images/NotRealCorp_chart.png"
    convert_file_to_png(plot_file_id,image_path)


