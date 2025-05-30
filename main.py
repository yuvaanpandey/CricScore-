import streamlit as st

st.set_page_config(page_title="CricScore+", layout="centered")

# Title
st.title("Welcome to CricScore+")

# Tabs for Login and Register
page = st.sidebar.selectbox("Choose Option", ["Login", "Register"])

# Store user data in session_state (temporary)
if "users" not in st.session_state:
    st.session_state.users = {"coach1": "password123", "player1": "pass456"}

if page == "Register":
    st.subheader("Create a New Account")

    username = st.text_input("Choose a Username")
    password = st.text_input("Enter Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")

    if st.button("Register"):
        if username in st.session_state.users:
            st.error("Username already exists. Try another.")
        elif password != confirm_password:
            st.error("Passwords do not match.")
        else:
            st.session_state.users[username] = password
            st.success("Registration successful! You can now log in.")

elif page == "Login":
    st.subheader("Login to Your Account")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username in st.session_state.users and st.session_state.users[username] == password:
            st.success(f"Welcome, {username}!")
        else:
            st.error("Incorrect username or password.")
