import os
import requests  # type: ignore
from PIL import Image  # type: ignore


def download_image(url, image_name):
    save_path = "images"

    # Make sure the save directory exists
    os.makedirs(save_path, exist_ok=True)

    # Send a GET request to the image URL
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code == 200:
        # Set the image path
        image_path = os.path.join(save_path, image_name)

        # Write the image data to a file
        with open(image_path, "wb") as file:
            file.write(response.content)

        print(f"Image saved to {image_path}")
        return {"status": "success", "image_path": image_path}
    else:
        print("Failed to retrieve the image")
        return {"status": "failed", "error": "Failed to retrieve the image"}


def read_image(image_path):
    try:
        # Open an image file
        with Image.open(image_path) as img:
            img.show()
            print(f"Image {image_path} opened successfully.")
            return {"status": "success", "image": img}
    except Exception as e:
        print(f"Failed to open image {image_path}: {e}")
        return {"status": "failed", "error": str(e)}


# read_image("images/character_historian.png")
