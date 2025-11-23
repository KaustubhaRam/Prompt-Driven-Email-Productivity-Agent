# Prompt-Driven-Email-Productivity-Agent


This project is a small demo of an email-processing tool built using Streamlit.
The idea is to take a simple email as input and automatically:

    -categorize it

    -extract any action items

    -generate a short reply draft



## Features

    - Simple UI built with Streamlit

    - Paste or type any email text

    - Categorizes emails (Meeting, To-Do, Newsletter, Spam, etc.)

    - Finds action items (deadlines, requests)

    - Creates a reply draft automatically

    - Everything is processed instantly without internet

    - Easy to modify or extend

## How to Run

Install Streamlit (if not installed):

    pip install streamlit


Run the app:

    streamlit run app.py



The app will open at:

http://localhost:8501



## How to Use

    - Paste any email text into the input box

    - Click Process

    - The app will show:

        the detected category

        any action items

        a generated reply