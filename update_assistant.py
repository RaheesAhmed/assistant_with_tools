from openai import OpenAI  # type: ignore
import os
import dotenv  # type: ignore


dotenv.load_dotenv()


api_key = os.getenv("OPENAI_API_KEY")
assistant_id = os.getenv("OPENAI_ASSISTANT_ID")

client = OpenAI(api_key=api_key)

my_updated_assistant = client.beta.assistants.update(
    assistant_id,
    instructions=f"""You are an assistant that helps create visual stories and images based on given mystery narratives. Your tasks include:

1. **Understand the Story Context**:
    - Read the provided mystery story, including the title, storyline, event causing the mystery, characters, and clues.
2. **Generate Visual Content**:
    - Create images representing key elements of the story such as the main story image, event image, character images, clue images, and solution image.
3. **Create Cryptograms**:
    - Generate cryptogram images for each clue based on the provided text.
4. **Download and Organize Content**:
    - Download the generated images and save them with specified names.
5. **Combine Story and Visuals**:
    - Integrate the story and the downloaded images into a structured JSON format, maintaining a coherent narrative flow.
6. **Generate Document**:
    - Create a DOCX file that contains the story and the images, maintaining a coherent narrative flow.
7. **Provide Clean Output**:
    - Ensure the final response is in a clean JSON format without using the word 'JSON' or any extra formatting.
""",
    model="gpt-4o",
    name="Mystery Story Generator",
    tools=[
        {"type": "code_interpreter"},
        {
            "type": "function",
            "function": {
                "name": "generate_images",
                "description": "Generate story images based on provided prompts using OpenAI's DALL-E 3 model",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "prompt": {
                            "type": "string",
                            "description": "A prompt to generate images.",
                        }
                    },
                    "required": ["prompt"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "download_image",
                "description": "Download an image from a URL and save it to an images folder with a given image name.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "url": {
                            "type": "string",
                            "description": "The URL of the image to download.",
                        },
                        "image_name": {
                            "type": "string",
                            "description": "The name to use for the saved image file.",
                        },
                    },
                    "required": ["url", "image_name"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "test_create_docx_from_json",
                "description": "Generates a Word document based on a JSON file containing story details, images, and descriptions. The document will be saved on local storage.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "json_file_path": {
                            "type": "string",
                            "description": "The path to the JSON file containing the story data.",
                        },
                        "output_docx_path": {
                            "type": "string",
                            "description": "The path where the generated Word document will be saved.",
                        },
                    },
                    "required": ["json_file_path", "output_docx_path"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "read_json",
                "description": "Reads a genereted story JSON file and returns the data.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "json_file_path": {
                            "type": "string",
                            "description": "The path to the JSON file containing the story data.",
                        },
                    },
                    "required": ["json_file_path"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "create_docx_from_json",
                "description": "Generates a Word document based on a JSON file containing story details, images, and descriptions. The document will be saved on local storage.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "json_file_path": {
                            "type": "string",
                            "description": "The path to the JSON file containing the story data.",
                        },
                        "output_docx_path": {
                            "type": "string",
                            "description": "The path where the generated Word document will be saved.",
                        },
                    },
                    "required": ["json_file_path", "output_docx_path"],
                },
            },
        },
    ],
)

print(my_updated_assistant)
print("Assistant updated successfully!")
