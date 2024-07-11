import streamlit as st
from dotenv import load_dotenv
import os
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled

# Load environment variables from .env file
load_dotenv()

# Configure Google Generative AI with API key from environment variables
genai.configure(api_key=os.getenv("Google_API_Key"))

# Prompt template for summarizing YouTube transcripts
prompt = """You are a video summarizer. You will be taking the transcript text
and summarizing the entire video and providing the important summary in points
within 250 words. Please provide the summary of the text given here: """

# Function to extract transcript from YouTube video
def extract_transcript_details(youtube_video_url):
    try:
        # Split by both "=" and "/" to handle various YouTube URL formats
        if "watch?v=" in youtube_video_url:
            video_id = youtube_video_url.split("watch?v=")[1]
        elif "youtu.be/" in youtube_video_url:
            video_id = youtube_video_url.split("youtu.be/")[1]
        else:
            video_id = youtube_video_url.split("/")[-1]

        transcript_text = YouTubeTranscriptApi.get_transcript(video_id, languages=['en'])

        transcript = ""
        for i in transcript_text:
            transcript += " " + i["text"]
        print("The entire transcription of the video:")
        print(transcript)
        return transcript
        
    except TranscriptsDisabled:
        return None  # No transcript available for this video
    except Exception as e:
        raise e

# Function to generate summary using Google Generative AI
def generative_gemini_content(transcript_text, prompt):
    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(prompt + transcript_text)
    return response.text

# Streamlit app setup
st.title("QuickTube:Instant Summaries 📺📜")
st.write("If you give me an URL, I will summarize it:")
youtube_link = st.text_input("Enter YouTube Video Link Below:")

# Initialize a session state variable to store the transcript
if 'transcript' not in st.session_state:
    st.session_state.transcript = ''

if youtube_link:
    try:
        if "watch?v=" in youtube_link:
            video_id = youtube_link.split("watch?v=")[1]
        elif "youtu.be/" in youtube_link:
            video_id = youtube_link.split("youtu.be/")[1]
        else:
            video_id = youtube_link.split("/")[-1]
        
        # Debugging: Print the video ID to ensure it's correct
        st.write(f"Video ID: {video_id}")
        
        # Display the thumbnail image
        thumbnail_url = f"http://img.youtube.com/vi/{video_id}/0.jpg"
        st.write(f"Thumbnail URL: {thumbnail_url}")  # Print the URL for debugging
        # st.image(thumbnail_url, use_column_width=True)  # Uncomment this line to display the image
    except IndexError:
        st.error("Invalid YouTube URL. Please check the format.")

if st.button("Get Detailed Notes"):
    try:
        transcript_text = extract_transcript_details(youtube_link)
        if transcript_text:
            st.session_state.transcript = transcript_text  # Store the transcript in session state
            summary = generative_gemini_content(transcript_text, prompt)
            st.markdown("## Detailed Notes:")
            st.write(summary)
        else:
            st.error("Transcripts are disabled for this video. Please try another video.")
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")

if st.button("Get Full Transcript of the Video"):
    if st.session_state.transcript:
        st.markdown("Entire Video Transcript:")
        st.write(st.session_state.transcript)
    else:
        st.error("Please click 'Get Detailed Notes' to extract the transcript first.")
