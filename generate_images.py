from openai import OpenAI  # type: ignore
import os
import dotenv  # type: ignore

dotenv.load_dotenv()


api_key = os.getenv("OPENAI_API_KEY")
assistant_id = os.getenv("OPENAI_ASSISTANT_ID")
# Initialize API client
client = OpenAI(api_key=api_key)


def generate_images(prompt):
    try:
        response = client.images.generate(
            model="dall-e-3",
            prompt=f"""{prompt}""",
            size="1024x1024",
            quality="standard",
            n=1,
        )
        image_url = response.data[0].url
        print(image_url)
        return image_url
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        raise ValueError("OpenAI Policy Rejection while generating the image.")


# prompt = "a mysterious forest with a hidden treasure chest"
# generate_images(prompt)
