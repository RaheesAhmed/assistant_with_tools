import streamlit as st  # type: ignore
import os
import time
import json
from generate_images import generate_images
from download_image import download_image
from generate_story import create_story
from generate_docs_file import create_docx_from_json
from openai import OpenAI  # type: ignore
import dotenv
import requests

# Load environment variables
dotenv.load_dotenv()

# Initialize API client
api_key = os.getenv("OPENAI_API_KEY")
assistant_id = os.getenv("OPENAI_ASSISTANT_ID")

zapier_webhook_url = os.getenv("ZAPIER_WEBHOOK_URL")

client = OpenAI(api_key=api_key)


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


def chat_with_assistant(story_details):
    try:
        story = create_story(story_details)
        thread = client.beta.threads.create()
        message = client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=f"""You are an assistant that helps create visual stories and images based on given mystery narratives. Your tasks include:
    - Understand the Story Context: Read and comprehend the provided mystery story, including the title, storyline, event causing the mystery, characters, and clues.
    - Generate Images:
        - Main Story Image: image representing the overall mystery story.
        - Event Image:  an image that captures the event causing the mystery.
        - Character Images: For each character, generate an image that includes their occupation, personality, physical traits, hobby, and accessory.
        - Clue Images: For each clue, generate an image that visually represents the clue's text.
        - Solution Image: generate an image representing the solution to the mystery.
    - Generate Cryptograms: For each clue, generate a number cryptogram image based on the provided text.
    Please ensure each image accurately reflects the description provided in the story and clues. Maintain consistency in style and quality throughout the images 
Download Images:
-download the images generated from the descriptions and save them to a given folder.
Here are the mystery story details: {json.dumps(story, ensure_ascii=False)}  prvide a clean json object with any extra formatting or word json""",
        )

        run = client.beta.threads.runs.create_and_poll(
            thread_id=thread.id,
            assistant_id=assistant_id,
        )

        while run.status == "requires_action":
            tool_outputs = []

            if run.required_action and run.required_action.submit_tool_outputs:
                for tool in run.required_action.submit_tool_outputs.tool_calls:
                    arguments = json.loads(tool.function.arguments)

                    if tool.function.name == "generate_images":
                        query = arguments.get("description")
                        image_url = generate_images(query)
                        tool_outputs.append(
                            {"tool_call_id": tool.id, "output": json.dumps(image_url)}
                        )

                    elif tool.function.name == "download_image":
                        url = arguments.get("url")
                        image_name = arguments.get("image_name")
                        result = download_image(url, image_name)
                        tool_outputs.append(
                            {"tool_call_id": tool.id, "output": json.dumps(result)}
                        )

                if tool_outputs:
                    run = client.beta.threads.runs.submit_tool_outputs_and_poll(
                        thread_id=thread.id, run_id=run.id, tool_outputs=tool_outputs
                    )
            run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)

        while run.status not in ["completed", "failed"]:
            time.sleep(2)
            run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)

        if run.status == "completed":
            messages = client.beta.threads.messages.list(thread_id=thread.id)
            for message in messages.data:
                save_response_to_json(message.content[0].text.value)
                return message.content[0].text.value
        else:
            return "An error occurred. Please try again later."
    except Exception as e:
        return f"An internal error occurred: {e}"


st.set_page_config(page_title="Story Generator", page_icon=":book:", layout="centered")

st.title("📝 Story Generator")
st.write("Fill in the details below to generate a mystery story and visualize it.")

with st.form(key="story_form"):
    title = st.text_input("Story Title", value="The Enchanted Forest Mystery")
    storyline = st.text_area(
        "Storyline",
        value="In the heart of the Enchanted Forest, the magical Crystal of Light has gone missing. The Crystal was the source of all magic in the forest, and its disappearance has caused chaos among the magical creatures. The forest guardian, Elara, must solve the mystery to restore peace. There are five suspects, each with a unique trait, and three important clues to uncover the thief.",
    )
    mystery_event = st.text_area(
        "Mystery Event",
        value="The Crystal of Light was last seen in the Forest Shrine during the nightly ceremony. When the shrine was opened the next morning, the Crystal was gone. Elara must talk to the suspects and follow the clues to find the culprit.",
    )

    st.write("Characters")
    characters = []
    for i in range(4):
        character = st.text_input(
            f"Character {i+1}", value=f"Character {i+1} description"
        )
        characters.append(character)

    st.write("Clues")
    clues = []
    for i in range(4):
        clue = st.text_input(f"Clue {i+1}", value=f"Clue {i+1} description")
        clues.append(clue)

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
            json_file_path = "generated_story.json"
            output_docx_path = "generated_story.docx"
            json_data = read_json(json_file_path)
            result = create_docx_from_json(json_data, output_docx_path)

            st.success(result)
            st.write(f"Document saved...")

            with st.spinner("Sending DOCX document to Zapier..."):
                send_to_zapier(output_docx_path)
