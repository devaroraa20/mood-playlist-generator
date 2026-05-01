from flask import Flask, render_template, request, redirect, session
from cloudant.client import Cloudant
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = "moodmelody_secret_key"

cloudant_username = os.environ.get("CLOUDANT_USERNAME")
cloudant_password = os.environ.get("CLOUDANT_PASSWORD")
cloudant_url = os.environ.get("CLOUDANT_URL")

client = Cloudant(cloudant_username, cloudant_password, url=cloudant_url, connect=True)

user_db = client["users"] if "users" in client.all_dbs() else client.create_database("users")
playlist_db = client["mood_playlist"] if "mood_playlist" in client.all_dbs() else client.create_database("mood_playlist")

playlists = {
    "happy": [
        {"name": "Lucid Dreams", "artist": "Juice WRLD", "yt": "mzB1VGEGcSU"},
        {"name": "Sunflower", "artist": "Post Malone", "yt": "ApXoWvfEYVU"},
        {"name": "Blinding Lights", "artist": "The Weeknd", "yt": "4NRXx6U8ABQ"},
        {"name": "Stay", "artist": "The Kid LAROI", "yt": "kTJczUoc26U"},
        {"name": "Heat Waves", "artist": "Glass Animals", "yt": "mRD0-GxqHVo"}
    ],
    "chill": [
        {"name": "Peaches", "artist": "Justin Bieber", "yt": "tQ0yjYUFKAE"},
        {"name": "Perfect", "artist": "Ed Sheeran", "yt": "2Vv-BfVoq4g"},
        {"name": "Sweater Weather", "artist": "The Neighbourhood", "yt": "GCdwKhTtNNw"},
        {"name": "Let Me Down Slowly", "artist": "Alec Benjamin", "yt": "50VNCymT-Cs"},
        {"name": "Night Changes", "artist": "One Direction", "yt": "syFZfO_wfMQ"}
    ],
    "sad": [
        {"name": "All Girls Are The Same", "artist": "Juice WRLD", "yt": "h3EJICKwITw"},
        {"name": "Someone Like You", "artist": "Adele", "yt": "hLQl3WQQoQ0"},
        {"name": "Let Her Go", "artist": "Passenger", "yt": "RBumgq5yVrA"},
        {"name": "Lovely", "artist": "Billie Eilish", "yt": "V1Pl8CzNzCw"},
        {"name": "Fix You", "artist": "Coldplay", "yt": "k4V3Mo61fJM"}
    ],
    "energetic": [
        {"name": "Believer", "artist": "Imagine Dragons", "yt": "7wtfhZwyrcc"},
        {"name": "Enemy", "artist": "Imagine Dragons", "yt": "F5tSoaJ93ac"},
        {"name": "Stronger", "artist": "Kanye West", "yt": "PsO6ZnUZI0g"},
        {"name": "Thunder", "artist": "Imagine Dragons", "yt": "fKopy74weus"},
        {"name": "Industry Baby", "artist": "Lil Nas X", "yt": "UTHLKHL_whs"}
    ],
    "focus": [
        {"name": "Lofi Study Beats", "artist": "Lofi Girl", "yt": "jfKfPfyJRdk"},
        {"name": "Deep Focus", "artist": "Study Music", "yt": "5qap5aO4i9A"},
        {"name": "Calm Piano", "artist": "Relaxing Music", "yt": "1ZYbU82GVz4"},
        {"name": "Coding Music", "artist": "Focus Beats", "yt": "WPni755-Krg"},
        {"name": "Ambient Focus", "artist": "Study Session", "yt": "lTRiuFIWV54"}
    ],
    "romantic": [
        {"name": "Perfect", "artist": "Ed Sheeran", "yt": "2Vv-BfVoq4g"},
        {"name": "Until I Found You", "artist": "Stephen Sanchez", "yt": "GxldQ9eX2wo"},
        {"name": "Love Me Like You Do", "artist": "Ellie Goulding", "yt": "AJtDXIazrMo"},
        {"name": "Senorita", "artist": "Shawn Mendes", "yt": "Pkh8UtuejGw"},
        {"name": "Die For You", "artist": "The Weeknd", "yt": "uPD0QOGTmMI"}
    ]
}

@app.route("/", methods=["GET", "POST"])
def login():
    error = ""

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        for user in user_db:
            if user.get("username") == username and user.get("password") == password:
                session["user"] = username
                return redirect("/dashboard")

        error = "Invalid username or password"

    return render_template("login.html", error=error)

@app.route("/register", methods=["GET", "POST"])
def register():
    error = ""

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        for user in user_db:
            if user.get("username") == username:
                error = "Username already exists"
                return render_template("register.html", error=error)

        user_db.create_document({
            "username": username,
            "password": password,
            "created_at": datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        })

        return redirect("/")

    return render_template("register.html", error=error)

@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    if "user" not in session:
        return redirect("/")

    mood = "happy"
    songs = playlists[mood]

    if request.method == "POST":
        mood = request.form["mood"]
        songs = playlists[mood]

        playlist_db.create_document({
            "user": session["user"],
            "mood": mood,
            "songs": [s["name"] for s in songs],
            "created_at": datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        })

    now_playing = songs[0]

    return render_template(
        "index.html",
        mood=mood,
        songs=songs,
        now_playing=now_playing,
        user=session["user"]
    )

@app.route("/history")
def history():
    if "user" not in session:
        return redirect("/")

    docs = [doc for doc in playlist_db if doc.get("user") == session["user"]]
    return render_template("history.html", docs=docs, user=session["user"])

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)