from openai import OpenAI  # type: ignore
import os
import dotenv  # type: ignore

dotenv.load_dotenv()


api_key = os.getenv("OPEN_API_KEY")
assistant_id = os.getenv("OPENAI_ASSISTANT_ID")
# Initialize API client
client = OpenAI(api_key=api_key)


def generate_images(prompt):
    response = client.images.generate(
        model="dall-e-3",
        prompt=f"""generate the perfect and fully matching image on provided prompt: {prompt}""",
        size="1024x1024",
        quality="standard",
        n=1,
    )
    image_url = response.data[0].url
    print(image_url)
    return image_url
