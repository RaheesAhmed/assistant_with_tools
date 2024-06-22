import os
import time
import json
import dotenv  # type: ignore
from openai import OpenAI  # type: ignore
from generate_images import generate_images
from download_image import download_image
from generate_story import create_story
from generate_docs_file import generate_document

dotenv.load_dotenv()

# Initialize API client
api_key = os.getenv("OPENAI_API_KEY")
assistant_id = os.getenv("OPENAI_ASSISTANT_ID")
client = OpenAI(api_key=api_key)




def chat_with_assistant(user_query):
    try:
        story = create_story(user_query)
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

Response Format:Response should be always in clean json format dont use word json or any extra formatting.
      here are the details: {story}""",
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
                        query = arguments.get("prompt")
                        image_url = generate_images(query)
                        tool_outputs.append(
                            {"tool_call_id": tool.id, "output": json.dumps(image_url)}
                        )
                    elif tool.function.name == "create_story":
                        query = arguments
                        story = create_story(query)
                        tool_outputs.append(
                            {"tool_call_id": tool.id, "output": json.dumps(story)}
                        )
                    elif tool.function.name == "download_image":
                        url = arguments.get("url")
                        image_name = arguments.get("image_name")
                        result = download_image(url, image_name)
                        tool_outputs.append(
                            {"tool_call_id": tool.id, "output": json.dumps(result)}
                        )
                    
                    elif tool.function.name == "generate_document":
                        file_path = 'response.json'
                        result = generate_document(file_path)
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
                
                return message.content[0].text.value
        else:
            print(f"Run ended with status: {run.status}")
            return "An error occurred. Please try again later."
    except Exception as e:
        print(f"An error occurred: {e}")
        return "An internal error occurred. Please try again later."


# # Example usage
userMessage = {
    "title": "The Lost Artifact of Galactoria",
    "storyline": "Aboard the interstellar spaceship 'Galactoria,' the crew is on a mission to explore distant galaxies and uncover ancient alien artifacts. During their voyage, the most prized artifact, the 'Star of Eternity,' has mysteriously disappeared from the secure vault. The artifact was to be presented to the Galactic Council as a symbol of peace. Captain Nova is called in to solve the case. There are nine suspects, each with overlapping traits, and four crucial clues that will lead to the identity of the thief.",
    "mysteryEvent": "The 'Star of Eternity,' an ancient and powerful alien artifact, was last seen in the secure vault during the ship's evening briefing. When the vault was reopened for the presentation to the Galactic Council, the artifact was missing. Captain Nova must now interview the suspects and uncover the clues to find the culprit.",
    "characters": [
        "Occupation: Historian, Personality: Analytical, Physical Trait: Slender, Hobby: Reading ancient texts, Accessory: Wears smart glasses",
        "Occupation: Journalist, Personality: Inquisitive, Physical Trait: Average build, Hobby: Writing space mystery novels, Accessory: Wears a neural cap",
        "Occupation: Lawyer, Personality: Persuasive, Physical Trait: Stocky, Hobby: Playing intergalactic chess, Accessory: Wears a tie",
        "Occupation: Pilot, Personality: Methodical, Physical Trait: Lean, Hobby: Bird watching on alien planets, Accessory: Wears a navigation pocket watch",
    ],
    "clues": [
        "The thief is known for their analytical mind and is often seen reading or playing intergalactic chess.",
        "Witnesses recall seeing the suspect wearing smart glasses, a tie, or a neural cap at the evening briefing.",
        "The thief was seen passionately discussing either ancient alien texts or their latest space mystery novel with another crew member during the gala.",
        "The suspect has a penchant for solving complex puzzles and is meticulous in their approach.",
    ],
}


story=chat_with_assistant(userMessage)




