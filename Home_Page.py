import streamlit as st

# Title of App
st.set_page_config(page_title="Country Explorer App", page_icon="🌍")
st.title("Welcome to the Country Explorer")

# Assignment Data 
# TODO: Fill out your team number, section, and team members

st.header("CS 1301")
st.subheader("Team 44, Web Development - Section A")
st.subheader("Steven William Hermann, Joanna George")


# Introduction
# TODO: Write a quick description for all of your pages in this lab below, in the form:
#       1. **Page Name**: Description
#       2. **Page Name**: Description
#       3. **Page Name**: Description
#       4. **Page Name**: Description

st.write("""
Welcome to our Streamlit Web Development Lab03 app! You can navigate between the pages using the sidebar to the left. The following pages are:

1. **Country Explorer Page**: Browse countries by region and view detailed statistics, flags, and comparisons

2. **AI Chatbot Page**: Chat with an AI assistant about geography and other topics

3. **Country Culture Comparator**: Select two countries and a topic to get an AI-generated cultural comparison.
""")

