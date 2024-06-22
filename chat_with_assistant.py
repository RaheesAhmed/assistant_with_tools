import os
import time
import json
import dotenv  # type: ignore
from openai import OpenAI  # type: ignore
from generate_images import generate_images
from download_image import download_image
from generate_story import create_story
from response_format import RESPONSE_FORMAT

# from generate_story import create_story, read_story
from generate_docs_file import create_docx_from_json

dotenv.load_dotenv()

# Initialize API client
api_key = os.getenv("OPENAI_API_KEY")
assistant_id = os.getenv("OPENAI_ASSISTANT_ID")
client = OpenAI(api_key=api_key)


def save_response_to_json(response):
    with open("generated_story.json", "w") as file:
        json.dump(response, file, indent=4)
        print("Response saved to: {file}")


def read_json(file_path):
    with open(file_path, "r") as file:
        data = json.load(file)
    return data


def chat_with_assistant(story_details):
    try:
        story = create_story(story_details)
        # Create a thread and add a user message
        print("Creating thread...")
        thread = client.beta.threads.create()
        print(f"Thread created with ID: {thread.id}")

        print("Adding user message to thread...")
        message = client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=f"""Read the provided mystery story, including the title, storyline, event causing the mystery, characters, and clues and images descrptions.
Generate Images:
Main Story Image: an image representing the overall mystery story.
Event Image:  an image that captures the event causing the mystery.
Character Images: For each character, generate an image that includes their occupation, personality, physical traits, hobby, and accessory.
Clue Images: For each clue, generate an image that visually represents the clue's text.
Solution Image: generate an image representing the solution to the mystery.
Generate Cryptograms:

For each clue, generate a number cryptogram image based on the provided text.
Download Images:
Download the each generated image and save it to the images folder with a given image name.
Combine Story and Images:
combine the {story}  and the downloaded image into a structured json fromat, maintaining a coherent narrative flow.
Always provide the response using the given json format.
Json format should be like this: {json.dumps(RESPONSE_FORMAT, ensure_ascii=False)}
Here are the mystery story details: {json.dumps(story, ensure_ascii=False)} prvide a clean json object with any extra formatting or word json""",
        )
        print(f"User message added with ID: {message.id}")

        # Create and poll the run
        print("Creating and polling the run...")
        run = client.beta.threads.runs.create_and_poll(
            thread_id=thread.id,
            assistant_id=assistant_id,
        )
        print(f"Run created with status: {run.status}")

        while run.status == "requires_action":
            tool_outputs = []
            print("Run requires action. Processing tool calls...")

            if run.required_action and run.required_action.submit_tool_outputs:
                for tool in run.required_action.submit_tool_outputs.tool_calls:
                    print(f"Processing tool call for function: {tool.function.name}")

                    # Ensure the arguments are in the correct format
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

                # Submit the tool outputs if there are any
                if tool_outputs:
                    print("Submitting tool outputs...")
                    run = client.beta.threads.runs.submit_tool_outputs_and_poll(
                        thread_id=thread.id, run_id=run.id, tool_outputs=tool_outputs
                    )
                    print("Tool outputs submitted successfully.")
                else:
                    print("No tool outputs to submit.")
            else:
                print("No required action found or no tool calls.")

            # Retrieve the run status again
            run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
            print(f"Current run status: {run.status}")

        # Poll for the final status of the run until completion
        while run.status not in ["completed", "failed"]:
            print("Run not completed. Polling again...")
            time.sleep(2)
            run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
            print(f"Current run status: {run.status}")

        # Check the final status of the run
        if run.status == "completed":
            print("Run completed. Fetching messages...")
            messages = client.beta.threads.messages.list(thread_id=thread.id)
            for message in messages.data:
                print(message.content[0].text.value)
                save_response_to_json(message.content[0].text.value)
                return message.content[0].text.value
        else:
            print(f"Run ended with status: {run.status}")
            return "An error occurred. Please try again later."
    except Exception as e:
        print(f"An error occurred: {e}")
        return "An internal error occurred. Please try again later."


#  Example usage
user_message = {
    "title": "The Enchanted Forest Mystery",
    "storyline": "In the heart of the Enchanted Forest, the magical Crystal of Light has gone missing. The Crystal was the source of all magic in the forest, and its disappearance has caused chaos among the magical creatures. The forest guardian, Elara, must solve the mystery to restore peace. There are five suspects, each with a unique trait, and three important clues to uncover the thief.",
    "mystery_event": "The Crystal of Light was last seen in the Forest Shrine during the nightly ceremony. When the shrine was opened the next morning, the Crystal was gone. Elara must talk to the suspects and follow the clues to find the culprit.",
    "characters": [
        "Mage: Wise, tall, always carrying a spellbook, wears a blue robe.",
        "Elf: Agile, slender, expert archer, wears a green cloak.",
        "Dwarf: Strong, stout, skilled blacksmith, carries a hammer.",
        "Fairy: Cheerful, small, loves singing, has sparkling wings.",
        "Goblin: Sneaky, short, clever with traps, wears a hood.",
    ],
    "clues": [
        "The thief was seen near the shrine late at night.",
        "A piece of blue fabric was found near the shrine.",
        "Witnesses heard someone humming a familiar tune near the scene.",
    ],
}


# story = chat_with_assistant(story_details)
# file_path = "generated_story.json"
# output_path = "generated_story.docx"
# data = read_json(file_path)
# create_docx_from_json(data, output_path)
