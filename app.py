from flask import Flask, render_template, jsonify, request, send_file
import requests
import sqlite3
import os
import json
from datetime import datetime, timedelta
import io
import urllib.request

app = Flask(__name__)
NASA_API_KEY = "DEMO_KEY"  # Replace with your NASA API key from https://api.nasa.gov/

# ─── Database Setup ───────────────────────────────────────────────────────────
def init_db():
    conn = sqlite3.connect("cosmoview.db")
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS favorites (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        date TEXT,
        url TEXT,
        media_type TEXT,
        explanation TEXT,
        saved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS search_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        query TEXT,
        searched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )""")
    conn.commit()
    conn.close()

init_db()

# ─── Routes ───────────────────────────────────────────────────────────────────
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/apod")
def apod_page():
    return render_template("apod.html")

@app.route("/iss")
def iss_page():
    return render_template("iss.html")

@app.route("/planets")
def planets_page():
    return render_template("planets.html")

@app.route("/news")
def news_page():
    return render_template("news.html")

@app.route("/explorer")
def explorer_page():
    return render_template("explorer.html")

# ─── API Endpoints ────────────────────────────────────────────────────────────
@app.route("/api/apod")
def get_apod():
    date = request.args.get("date", "")
    count = request.args.get("count", "")
    params = {"api_key": NASA_API_KEY}
    if date:
        params["date"] = date
    if count:
        params["count"] = count
    try:
        r = requests.get("https://api.nasa.gov/planetary/apod", params=params, timeout=10)
        return jsonify(r.json())
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/apod/random")
def get_random_apod():
    try:
        r = requests.get("https://api.nasa.gov/planetary/apod",
                         params={"api_key": NASA_API_KEY, "count": 1}, timeout=10)
        data = r.json()
        return jsonify(data[0] if isinstance(data, list) else data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/iss/location")
def get_iss_location():
    try:
        r = requests.get("http://api.open-notify.org/iss-now.json", timeout=10)
        return jsonify(r.json())
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/iss/astronauts")
def get_astronauts():
    try:
        r = requests.get("http://api.open-notify.org/astros.json", timeout=10)
        return jsonify(r.json())
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/news")
def get_news():
    news_type = request.args.get("type", "article")
    limit = request.args.get("limit", "12")
    try:
        url = f"https://api.spaceflightnewsapi.net/v4/{news_type}s/?limit={limit}&ordering=-published_at"
        r = requests.get(url, timeout=10)
        return jsonify(r.json())
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/launches")
def get_launches():
    try:
        r = requests.get("https://api.spaceflightnewsapi.net/v4/launches/?limit=10&ordering=-published_at", timeout=10)
        return jsonify(r.json())
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/planets")
def get_planets():
    planets = {
        "mercury": {
            "name": "Mercury", "emoji": "☿",
            "color": "#b5b5b5",
            "distance_from_sun": "57.9 million km",
            "diameter": "4,879 km",
            "mass": "3.30 × 10²³ kg",
            "gravity": "3.7 m/s²",
            "day_length": "58.6 Earth days",
            "year_length": "88 Earth days",
            "avg_temperature": "-173°C to 427°C",
            "atmosphere": "Minimal – thin exosphere of oxygen, sodium, hydrogen",
            "moons": 0,
            "rings": False,
            "fun_facts": [
                "Closest planet to the Sun",
                "Has the most extreme temperature swings in the solar system",
                "Despite being closest to the Sun, it's NOT the hottest planet",
                "A year on Mercury is shorter than its day",
                "Covered in craters like Earth's Moon"
            ],
            "description": "The smallest planet in our solar system and nearest to the Sun, Mercury has a thin atmosphere that can't regulate temperature — making it swing wildly from -173°C at night to 427°C during the day.",
            "image_hint": "gray rocky barren"
        },
        "venus": {
            "name": "Venus", "emoji": "♀",
            "color": "#e8c46a",
            "distance_from_sun": "108.2 million km",
            "diameter": "12,104 km",
            "mass": "4.87 × 10²⁴ kg",
            "gravity": "8.87 m/s²",
            "day_length": "243 Earth days",
            "year_length": "225 Earth days",
            "avg_temperature": "465°C (average)",
            "atmosphere": "96% CO₂, 3.5% Nitrogen – extreme greenhouse effect",
            "moons": 0,
            "rings": False,
            "fun_facts": [
                "Hottest planet despite not being closest to Sun",
                "Rotates backwards compared to most planets",
                "A day on Venus is longer than its year",
                "Surface pressure is 90x that of Earth's",
                "Called Earth's twin due to similar size"
            ],
            "description": "Venus is Earth's twisted twin — similar in size but with a crushing atmosphere and temperatures hot enough to melt lead. Its thick clouds of sulfuric acid make it the brightest object in the night sky after the Moon.",
            "image_hint": "yellow cloudy thick atmosphere"
        },
        "earth": {
            "name": "Earth", "emoji": "🌍",
            "color": "#4a9eff",
            "distance_from_sun": "149.6 million km",
            "diameter": "12,742 km",
            "mass": "5.97 × 10²⁴ kg",
            "gravity": "9.8 m/s²",
            "day_length": "24 hours",
            "year_length": "365.25 days",
            "avg_temperature": "15°C (average)",
            "atmosphere": "78% Nitrogen, 21% Oxygen, 1% Argon",
            "moons": 1,
            "rings": False,
            "fun_facts": [
                "Only known planet with life",
                "71% of surface covered by water",
                "Has a powerful magnetic field protecting life",
                "Home to over 8.7 million species",
                "The Moon stabilizes Earth's axial tilt"
            ],
            "description": "Our pale blue dot — the only world known to harbor life. Earth's perfect distance from the Sun, liquid water, and protective atmosphere create the Goldilocks conditions for an incredible diversity of life.",
            "image_hint": "blue ocean green continents clouds"
        },
        "mars": {
            "name": "Mars", "emoji": "♂",
            "color": "#c1440e",
            "distance_from_sun": "227.9 million km",
            "diameter": "6,779 km",
            "mass": "6.39 × 10²³ kg",
            "gravity": "3.72 m/s²",
            "day_length": "24h 37min",
            "year_length": "687 Earth days",
            "avg_temperature": "-63°C (average)",
            "atmosphere": "95% CO₂, 3% Nitrogen – very thin",
            "moons": 2,
            "rings": False,
            "fun_facts": [
                "Has the tallest volcano in the solar system – Olympus Mons",
                "Has the longest canyon – Valles Marineris (4,000 km)",
                "Dust storms can cover the entire planet",
                "Red color comes from iron oxide (rust)",
                "Has evidence of ancient liquid water"
            ],
            "description": "The Red Planet is humanity's next great frontier. With its rust-colored deserts, massive volcanoes, and ancient riverbeds, Mars may once have harbored life — and might do so again with human settlers.",
            "image_hint": "red rocky desert rust"
        },
        "jupiter": {
            "name": "Jupiter", "emoji": "♃",
            "color": "#c88b3a",
            "distance_from_sun": "778.5 million km",
            "diameter": "139,820 km",
            "mass": "1.90 × 10²⁷ kg",
            "gravity": "24.8 m/s²",
            "day_length": "9h 56min",
            "year_length": "11.9 Earth years",
            "avg_temperature": "-110°C (cloud tops)",
            "atmosphere": "90% Hydrogen, 10% Helium",
            "moons": 95,
            "rings": True,
            "fun_facts": [
                "Largest planet – 1,300 Earths could fit inside",
                "Great Red Spot is a storm lasting 350+ years",
                "Acts as the solar system's vacuum cleaner",
                "Fastest rotating planet despite its size",
                "Has faint rings made of dust"
            ],
            "description": "King of the planets, Jupiter is so massive it could swallow all other planets combined. Its Great Red Spot is a storm that has raged for centuries, and its 95 moons form a miniature solar system of their own.",
            "image_hint": "giant gas swirling bands brown orange"
        },
        "saturn": {
            "name": "Saturn", "emoji": "♄",
            "color": "#e8d5a3",
            "distance_from_sun": "1.43 billion km",
            "diameter": "116,460 km",
            "mass": "5.68 × 10²⁶ kg",
            "gravity": "10.4 m/s²",
            "day_length": "10h 42min",
            "year_length": "29.5 Earth years",
            "avg_temperature": "-140°C (cloud tops)",
            "atmosphere": "96% Hydrogen, 3% Helium",
            "moons": 146,
            "rings": True,
            "fun_facts": [
                "Least dense planet – would float on water",
                "Rings are made of ice and rock",
                "Rings stretch 282,000 km but are only 1km thick",
                "Has 146 known moons — the most of any planet",
                "Titan (its moon) has a thick atmosphere and lakes"
            ],
            "description": "Saturn's stunning ring system makes it the jewel of the solar system. Its rings are incredibly thin relative to their width, and its moon Titan is more planet-like than any other moon — with rivers and lakes of liquid methane.",
            "image_hint": "pale gold rings ice rock bands"
        },
        "uranus": {
            "name": "Uranus", "emoji": "⛢",
            "color": "#7de8e8",
            "distance_from_sun": "2.87 billion km",
            "diameter": "50,724 km",
            "mass": "8.68 × 10²⁵ kg",
            "gravity": "8.69 m/s²",
            "day_length": "17h 14min",
            "year_length": "84 Earth years",
            "avg_temperature": "-195°C (average)",
            "atmosphere": "83% Hydrogen, 15% Helium, 2% Methane",
            "moons": 27,
            "rings": True,
            "fun_facts": [
                "Rotates on its side – axial tilt of 98°",
                "Has the coldest planetary atmosphere in the solar system",
                "Its moons are named after Shakespeare characters",
                "Blue-green color from methane in atmosphere",
                "Only planet to orbit the Sun on its side"
            ],
            "description": "The tilted ice giant rolls around the Sun on its side, likely due to a massive collision billions of years ago. Its methane-rich atmosphere gives it a distinctive cyan hue, and its seasons last over 20 years each.",
            "image_hint": "cyan blue green ice giant tilted"
        },
        "neptune": {
            "name": "Neptune", "emoji": "♆",
            "color": "#4b70dd",
            "distance_from_sun": "4.50 billion km",
            "diameter": "49,244 km",
            "mass": "1.02 × 10²⁶ kg",
            "gravity": "11.15 m/s²",
            "day_length": "16h 6min",
            "year_length": "165 Earth years",
            "avg_temperature": "-200°C (average)",
            "atmosphere": "80% Hydrogen, 19% Helium, 1% Methane",
            "moons": 16,
            "rings": True,
            "fun_facts": [
                "Has the fastest winds in the solar system – up to 2,100 km/h",
                "Was discovered by math, not telescope first",
                "Triton (moon) orbits backwards and may be a captured Kuiper Belt object",
                "Its Great Dark Spot is similar to Jupiter's storm",
                "Takes 165 Earth years to complete one orbit"
            ],
            "description": "The furthest planet from the Sun, Neptune is a dynamic world of supersonic winds and violent storms. Its largest moon Triton is slowly spiraling inward and will eventually be torn apart to form a ring system in about 3.6 billion years.",
            "image_hint": "deep blue ice giant distant dark"
        }
    }
    planet_name = request.args.get("name", "").lower()
    if planet_name and planet_name in planets:
        return jsonify(planets[planet_name])
    return jsonify(planets)

@app.route("/api/favorites", methods=["GET", "POST", "DELETE"])
def manage_favorites():
    conn = sqlite3.connect("cosmoview.db")
    c = conn.cursor()
    if request.method == "GET":
        c.execute("SELECT * FROM favorites ORDER BY saved_at DESC")
        rows = c.fetchall()
        cols = ["id", "title", "date", "url", "media_type", "explanation", "saved_at"]
        result = [dict(zip(cols, r)) for r in rows]
        conn.close()
        return jsonify(result)
    elif request.method == "POST":
        data = request.json
        c.execute("INSERT INTO favorites (title, date, url, media_type, explanation) VALUES (?,?,?,?,?)",
                  (data.get("title"), data.get("date"), data.get("url"),
                   data.get("media_type"), data.get("explanation")))
        conn.commit()
        conn.close()
        return jsonify({"success": True})
    elif request.method == "DELETE":
        fav_id = request.args.get("id")
        c.execute("DELETE FROM favorites WHERE id=?", (fav_id,))
        conn.commit()
        conn.close()
        return jsonify({"success": True})

if __name__ == "__main__":
    app.run(debug=True, port=5000)
