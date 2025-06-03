import streamlit as st
from auth import init_firebase, register_coach, login_coach

st.set_page_config(page_title="CricScore+", layout="centered")
# Title
st.title("Welcome to CricScore+")

db = init_firebase()

# Tabs for Login and Register
page = st.sidebar.selectbox("Choose Option", ["Login", "Register"])

if page == "Register":
    st.subheader("Create a New Account")

    username = st.text_input("Choose a Username")
    password = st.text_input("Enter Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")

    if st.button("Register"):
    if password != confirm_password:
        st.error("Passwords do not match.")
    else:
        success, message = register_coach(db, username, "TeamNameHere", password)
        if success:
            st.success(message)
        else:
            st.error(message)

elif page == "Login":
    st.subheader("Login to Your Account")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

  if st.button("Login"):
    success, team = login_coach(db, username, password)
    if success:
        st.success(f"Welcome, {username} from team {team}!")
    else:
        st.error("Incorrect username or password.")
