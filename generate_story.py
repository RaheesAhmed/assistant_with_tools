from openai import OpenAI  # type: ignore
import os
import dotenv  # type: ignore
import json
import streamlit as st  # type: ignore

dotenv.load_dotenv()


api_key = os.getenv("OPENAI_API_KEY")
assistant_id = os.getenv("OPENAI_ASSISTANT_ID")
# Initialize API client
client = OpenAI(api_key=api_key)


def create_story(story_details):

    content = f"You are an assistant that helps create visual stories and images based on given mystery narratives. Your tasks include:Understand the Story Context:Read and comprehend the provided mystery story, including the title, storyline, event causing the mystery, characters, and clues.Generate Image Descriptions:Main Story Image: Describe an image representing the overall mystery story.Event Image: Describe an image that captures the event causing the mystery.Character Images: For each character, describe an image that includes their occupation, personality, physical traits, hobby, and accessory.Clue Images: For each clue, describe an image that visually represents the clue's text.Solution Image: Describe an image representing the solution to the mystery.Generate Cryptograms:For each clue, generate a number cryptogram image based on the provided text.Please ensure each image accurately reflects the description provided in the story and clues. Maintain consistency in style and quality throughout the images"

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": content},
            {
                "role": "user",
                "content": f"""write the mystery story, including the title, storyline, event causing the mystery, characters, clues etc.
      Generate Image Descriptions:
      Generate images Descrptions based on the provided text,
      Generate Cryptograms:
      For each clue, generate a number cryptogram  based on the provided text.
      Response Format:Response should be always in clean json format dont use word json or any extra.,
      here are the details: {story_details}""",
            },
        ],
    )
    print(response.choices[0].message.content)
    st.write(response.choices[0].message.content)
    save_response_to_json(response.choices[0].message.content)
    return response.choices[0].message.content


# # save response to json file
def save_response_to_json(response):
    with open("generated_story.json", "w") as file:
        json.dump(response, file, indent=4)
        print("Response saved to generated_story.json")


# read the json file
def read_story():
    with open("generated_story.json", "r") as file:
        data = json.load(file)
        print("File loaded...")
        return data


userMessage = {
    "title": "A Love to Remember",
    "storyline": "In a small picturesque town, nestled between rolling hills and serene lakes, lived a young woman named Emily. She was known for her kind heart and beautiful smile, which could light up even the gloomiest day. One day, a charming artist named James moved into the town. With his arrival, he brought a burst of color and life, capturing the beauty of the town on his canvas. Emily and James' paths crossed one sunny afternoon at the local market.",
    "mysteryEvent": "Their love story began when James left a small painting at Emily's flower shop, depicting a beautiful bouquet of her favorite flowers. This act of kindness was the first clue in their blossoming relationship. Emily found a handwritten note from James, inviting her to an art exhibition, where she discovered a painting of herself, titled 'The Heart of the Town'.",
    "characters": [
        "Occupation: Florist, Personality: Kind-hearted, Physical Trait: Bright smile, Hobby: Arranging beautiful bouquets, Accessory: Wears a floral apron",
        "Occupation: Artist, Personality: Charming, Physical Trait: Tall and slender, Hobby: Painting vibrant scenes, Accessory: Carries a sketchbook",
        "Occupation: Cafe Owner, Personality: Warm and welcoming, Physical Trait: Curvy, Hobby: Baking delicious pastries, Accessory: Wears a chef's hat",
        "Occupation: Shopkeeper, Personality: Friendly, Physical Trait: Stocky, Hobby: Sharing stories about the town's history, Accessory: Wears glasses",
    ],
    "clues": [
        "James left a small painting at Emily's flower shop, depicting a beautiful bouquet of her favorite flowers.",
        "Emily found a handwritten note from James, inviting her to an art exhibition.",
        "At the art exhibition, Emily discovered a painting of herself, titled 'The Heart of the Town'.",
        "James surprised Emily with a picnic by the lake, where they first met.",
    ],
}

# create_story(userMessage)
