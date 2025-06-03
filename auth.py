import pyrebase

def init_firebase():
    firebaseConfig = {
        "apiKey": "AIzaSyCq9HpJNkW3N60pwjTymKEKwV5a5nPZOo",
        "authDomain": "cricket-wala-project.firebaseapp.com",
        "databaseURL": "https://cricket-wala-project-default-rtdb.firebaseio.com",
        "projectId": "cricket-wala-project",
        "storageBucket": "cricket-wala-project.appspot.com",
        "messagingSenderId": "959184856893",
        "appId": "1:959184856893:web:bbc5346f69170cddf80754",
        "measurementId": "G-469DLPQV0V"
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
