# Story Generator Using OpenAI Assistant API with Tools Calling 

This Streamlit application allows users to generate a mystery story based on provided details, create a DOCX document from the generated story, and send the document to a Zapier webhook.

## Table of Contents

- [Story Generator Using OpenAI Assistant API with Tools Calling](#story-generator-using-openai-assistant-api-with-tools-calling)
  - [Table of Contents](#table-of-contents)
  - [Installation](#installation)
  - [Environment Setup](#environment-setup)
  - [Running the Application](#running-the-application)
  - [Using the Application](#using-the-application)
  - [Environment Variables](#environment-variables)
  - [File Descriptions](#file-descriptions)
  - [Example Usage](#example-usage)
  - [License](#license)

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/RaheesAhmed/assistant_with_tools.git
    cd assistant_with_tools
    ```

2. Install the required packages:
    ```bash
    pip install -r requirements.txt
    ```

3. Install Streamlit if not already installed:
    ```bash
    pip install streamlit
    ```

## Environment Setup

Create a `.env` file in the root directory of your project and add your OpenAI API key, Assistant ID, and Zapier Webhook URL:
```
OPENAI_API_KEY=your_openai_api_key
OPENAI_ASSISTANT_ID=your_assistant_id
ZAPIER_WEBHOOK_URL=your_zapier_webhook_url
```


## Running the Application

1. Start the Streamlit application:
    ```bash
    streamlit run app.py
    ```

2. This command will open the Streamlit app in your default web browser.

## Using the Application

1. Fill in the details for the story, including:
    - **Story Title**
    - **Storyline**
    - **Mystery Event**
    - **Characters**
    - **Clues**

2. Click the "Generate Story" button to generate the story. The application will:
    - Send the story details to an OpenAI assistant.
    - Save the generated story to `generated_story.json`.
    - Create a DOCX document from the JSON file.
    - Send the DOCX file to the configured Zapier webhook URL.

## Environment Variables

- `OPENAI_API_KEY`: Your OpenAI API key.
- `OPENAI_ASSISTANT_ID`: Your OpenAI Assistant ID.
- `ZAPIER_WEBHOOK_URL`: The URL for your Zapier webhook to receive the DOCX file.

## File Descriptions

- `app.py`: The main Streamlit application script.
- `generate_story.py`: Contains the function to generate the story.
- `generate_images.py`: Contains the function to generate images.
- `download_image.py`: Contains the function to download images.
- `generate_docs_file.py`: Contains the function to create a DOCX file from JSON data.
- `requirements.txt`: A list of required Python packages.


## Example Usage

1. Clone the repository and navigate to the project directory.
2. Install the required packages.
3. Create a `.env` file with your OpenAI API key, Assistant ID, and Zapier Webhook URL.
4. Run the Streamlit application using `streamlit run app.py`.
5. Fill in the story details and generate the story.
6. The generated DOCX file will be sent to the configured Zapier webhook URL.

## License

This project is licensed under the MIT License. See the LICENSE file for details.


