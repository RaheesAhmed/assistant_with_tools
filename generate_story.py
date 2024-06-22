from openai import OpenAI  # type: ignore
import os
import dotenv  # type: ignore
import json


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


# userMessage = {
#     "title": "The Lost Artifact of Galactoria",
#     "storyline": "Aboard the interstellar spaceship 'Galactoria,' the crew is on a mission to explore distant galaxies and uncover ancient alien artifacts. During their voyage, the most prized artifact, the 'Star of Eternity,' has mysteriously disappeared from the secure vault. The artifact was to be presented to the Galactic Council as a symbol of peace. Captain Nova is called in to solve the case. There are nine suspects, each with overlapping traits, and four crucial clues that will lead to the identity of the thief.",
#     "mysteryEvent": "The 'Star of Eternity,' an ancient and powerful alien artifact, was last seen in the secure vault during the ship's evening briefing. When the vault was reopened for the presentation to the Galactic Council, the artifact was missing. Captain Nova must now interview the suspects and uncover the clues to find the culprit.",
#     "characters": [
#         "Occupation: Historian, Personality: Analytical, Physical Trait: Slender, Hobby: Reading ancient texts, Accessory: Wears smart glasses",
#         "Occupation: Journalist, Personality: Inquisitive, Physical Trait: Average build, Hobby: Writing space mystery novels, Accessory: Wears a neural cap",
#         "Occupation: Lawyer, Personality: Persuasive, Physical Trait: Stocky, Hobby: Playing intergalactic chess, Accessory: Wears a tie",
#         "Occupation: Pilot, Personality: Methodical, Physical Trait: Lean, Hobby: Bird watching on alien planets, Accessory: Wears a navigation pocket watch",
#     ],
#     "clues": [
#         "The thief is known for their analytical mind and is often seen reading or playing intergalactic chess.",
#         "Witnesses recall seeing the suspect wearing smart glasses, a tie, or a neural cap at the evening briefing.",
#         "The thief was seen passionately discussing either ancient alien texts or their latest space mystery novel with another crew member during the gala.",
#         "The suspect has a penchant for solving complex puzzles and is meticulous in their approach.",
#     ],
# }
# create_story(userMessage)
