import pyrebase

def init_firebase():
    firebaseConfig = {
    "apiKey": "AIzaSyC2dcz3liQ2xKesIVd4tNZ0X7DDH2ZNiKw",
    "authDomain": "cricscore-f1c9f.firebaseapp.com",
    "databaseURL": "https://cricscore-f1c9f-default-rtdb.firebaseio.com",
    "projectId": "cricscore-f1c9f",
    "storageBucket": "cricscore-f1c9f.firebasestorage.app",
    "messagingSenderId": "988380158146",
    "appId": "1:988380158146:web:a07eec6823901b9d8f435b",
    "measurementId": "G-2M1G6NFR4E"
}
    firebase = pyrebase.initialize_app(firebaseConfig)
    return firebase.database()

def register_coach(db, username, team, password):
    users = db.child("users").get().val()
    if users and username in users:
        return False, "Username already exists"
    db.child("users").child(username).set({
        "password": password.strip(),
        "team": team.strip()
    })
    return True, "Registration successful"

def login_coach(db, username, password):
    users = db.child("users").get().val()
    if users and username in users:
        stored_password = users[username].get("password", "").strip()
        if stored_password == password.strip():
            return True, users[username]["team"]
    return False, None
