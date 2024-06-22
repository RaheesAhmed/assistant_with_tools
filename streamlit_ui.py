import streamlit as st  # type: ignore
import os
import time
import json
from generate_images import generate_images
from download_image import download_image
from generate_story import create_story
from generate_docs_file import create_docx_from_json
from openai import OpenAI  # type: ignore
import dotenv  # type: ignore
import requests
from response_format import RESPONSE_FORMAT

# Load environment variables
dotenv.load_dotenv()

# Initialize API client
api_key = os.getenv("OPENAI_API_KEY")
assistant_id = os.getenv("OPENAI_ASSISTANT_ID")
zapier_webhook_url = os.getenv("ZAPIER_WEBHOOK_URL")

client = OpenAI(api_key=api_key)


def chat_with_assistant(story_details):
    try:
        st.write("Generating story content...")
        story = create_story(story_details)
        st.write("Story content generated.")

        st.write("Creating a new thread...")
        thread = client.beta.threads.create()
        st.write(f"Thread created successfully with ID: {thread.id}")

        st.write("Adding user message to the thread...")
        message = client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=f"""Read the provided mystery story, including the title, storyline, event causing the mystery, characters, and clues and images descriptions.
Generate Images:
Main Story Image: an image representing the overall mystery story.
Event Image: an image that captures the event causing the mystery.
Character Images: For each character, generate an image that includes their occupation, personality, physical traits, hobby, and accessory.
Clue Images: For each clue, generate an image that visually represents the clue's text.
Solution Image: generate an image representing the solution to the mystery.
Generate Cryptograms:

For each clue, generate a number cryptogram image based on the provided text.

If there is any error in the image generation, please try again with different prompt.
Download Images:
Download each generated image and save it to the images folder with a given image name.
Combine Story and Images:
combine the {story} and the downloaded image into a structured json format, maintaining a coherent narrative flow.
Always provide the response using the given json format.
Json format should be like this: {json.dumps(RESPONSE_FORMAT, ensure_ascii=False)}
Here are the mystery story details: {json.dumps(story, ensure_ascii=False)} provide a clean json object without any extra formatting or word json""",
        )
        st.write(f"User message added successfully with ID: {message.id}")

        st.write("Starting the run and polling for status updates...")
        run = client.beta.threads.runs.create_and_poll(
            thread_id=thread.id,
            assistant_id=assistant_id,
        )
        st.write(f"Run initiated with status: {run.status}")

        while run.status == "requires_action":
            tool_outputs = []
            st.write("The run requires action. Processing tool calls...")

            if run.required_action and run.required_action.submit_tool_outputs:
                for tool in run.required_action.submit_tool_outputs.tool_calls:
                    st.write(f"Processing tool call for function: {tool.function.name}")

                    # Ensure the arguments are in the correct format
                    arguments = json.loads(tool.function.arguments)

                    try:
                        if tool.function.name == "generate_images":
                            query = arguments.get("description")
                            st.write(f"Generating image for query")
                            image_url = generate_images(query)
                            st.write(f"Image generated successfully: {image_url}")
                            tool_outputs.append(
                                {
                                    "tool_call_id": tool.id,
                                    "output": json.dumps(image_url),
                                }
                            )

                        elif tool.function.name == "download_image":
                            url = arguments.get("url")
                            image_name = arguments.get("image_name")
                            st.write(
                                f"Downloading image from URL: {url} as {image_name}"
                            )
                            result = download_image(url, image_name)
                            st.write(f"Image downloaded successfully: {result}")
                            tool_outputs.append(
                                {"tool_call_id": tool.id, "output": json.dumps(result)}
                            )
                    except Exception as e:
                        st.write(f"An error occurred during tool call processing: {e}")
                        return "An internal error occurred. Please try again later."

                if tool_outputs:
                    st.write("Submitting tool outputs to the thread...")
                    run = client.beta.threads.runs.submit_tool_outputs_and_poll(
                        thread_id=thread.id, run_id=run.id, tool_outputs=tool_outputs
                    )
                    st.write("Tool outputs submitted successfully.")
                else:
                    st.write("No tool outputs to submit.")

            run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
            st.write(f"Current run status: {run.status}")

        while run.status not in ["completed", "failed"]:
            st.write("Run not completed yet. Polling again in a few seconds...")
            time.sleep(2)
            run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
            st.write(f"Current run status: {run.status}")

        if run.status == "completed":
            st.write("Run completed successfully. Fetching final messages...")
            messages = client.beta.threads.messages.list(thread_id=thread.id)
            for message in messages.data:
                st.write(f"Final message content: {message.content[0].text.value}")
                save_response_to_json(message.content[0].text.value)
                return message.content[0].text.value
        else:
            st.write(f"Run ended with status: {run.status}")
            return "An error occurred. Please try again later."
    except Exception as e:
        st.write(f"An error occurred: {e}")
        return "An internal error occurred. Please try again later."


def save_response_to_json(response):
    with open("generated_story.json", "w") as file:
        json.dump(response, file, indent=4)
    st.write("Response saved to: generated_story.json")


def read_json(file_path):
    with open(file_path, "r") as file:
        data = json.load(file)
    return data


def send_to_zapier(file_path):
    with open(file_path, "rb") as f:
        files = {"file": (os.path.basename(file_path), f)}
        response = requests.post(zapier_webhook_url, files=files)
        if response.status_code == 200:
            st.success("File successfully sent to Zapier.")
        else:
            st.error(
                f"Failed to send file to Zapier. Status code: {response.status_code}"
            )


st.set_page_config(page_title="Story Generator", page_icon=":book:", layout="centered")

st.title("📝 Story Generator")
st.write("Fill in the details below to generate a mystery story and visualize it.")

with st.form(key="story_form"):
    title = st.text_input("Story Title", value="Story Title here")
    storyline = st.text_area("Storyline", value="StoryLine here...")
    mystery_event = st.text_area("Mystery Event", value="write about event.")

    st.write("Characters")
    characters = [
        st.text_input(f"Character {i+1}", value=f"Character {i+1} description")
        for i in range(4)
    ]

    st.write("Clues")
    clues = [
        st.text_input(f"Clue {i+1}", value=f"Clue {i+1} description") for i in range(4)
    ]

    submit_button = st.form_submit_button(label="Generate Story")

if submit_button:
    user_message = {
        "title": title,
        "storyline": storyline,
        "mystery_event": mystery_event,
        "characters": characters,
        "clues": clues,
    }

    with st.spinner("Generating story..."):
        story = chat_with_assistant(user_message)
        st.success("Story generated and saved to `generated_story.json`.")

        with st.spinner("Creating DOCX document..."):
            if os.path.exists("generated_story.json"):
                json_file_path = "generated_story.json"
                output_docx_path = "generated_story.docx"
                json_data = read_json(json_file_path)
                result = create_docx_from_json(json_data, output_docx_path)
            else:
                result = "No JSON file found. Please generate a story first."

            st.success(result)
            st.write(f"Document saved: {output_docx_path}")

            with st.spinner("Sending DOCX document to Zapier..."):
                if os.path.exists(output_docx_path):
                    send_to_zapier(output_docx_path)
                else:
                    st.error("No DOCX file found. Please generate a story first.")
