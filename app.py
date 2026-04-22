from neo4j_helper import get_word_details
from flask import Flask, render_template, request, redirect, session
import random
import json
import os

app = Flask(__name__)
app.secret_key = "secret123"

DATA_FOLDER = "data"
PROGRESS_FILE = "progress.json"


# ------------------ DATA LOADING ------------------

def get_sets():
    files = os.listdir(DATA_FOLDER)
    result = {}

    for file in files:
        if file.endswith(".json"):
            level, set_name = file.replace(".json", "").split("_")

            if level not in result:
                result[level] = []

            result[level].append(set_name)

    return result


def load_set(level, set_name):
    path = f"{DATA_FOLDER}/{level}_{set_name}.json"
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


# ------------------ PROGRESS ------------------

def load_progress():
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, "r") as f:
            return json.load(f)
    return {"words": {}, "completed_sets": []}


def save_progress(progress):
    with open(PROGRESS_FILE, "w") as f:
        json.dump(progress, f)


# ------------------ ROUTES ------------------

@app.route("/", methods=["GET", "POST"])
def index():
    sets = get_sets()

    if request.method == "POST":
        level = request.form["level"]
        set_name = request.form["set"]

        session["level"] = level
        session["set"] = set_name

        words = load_set(level, set_name)
        random.shuffle(words)

        session["queue"] = words
        session.pop("current", None)

        return redirect("/card")

    return render_template("index.html", sets=sets)


# ------------------ CARD ------------------

@app.route("/card", methods=["GET", "POST"])
def card():
    progress = load_progress()

    if "set" not in session or "level" not in session or "queue" not in session:
        return redirect("/")

    # HANDLE POST
    if request.method == "POST":
        action = request.form.get("action")

        if action == "show_meaning":
            session["show_meaning"] = True

        else:
            result = request.form["result"]
            card = session["current"]
            word = card["word"]

            if word not in progress["words"]:
                progress["words"][word] = {"correct": 0, "wrong": 0}

            if result == "know":
                progress["words"][word]["correct"] += 1

                if progress["words"][word]["correct"] < 2:
                    pos = random.randint(3, min(7, len(session["queue"])))
                    session["queue"].insert(pos, card)

            else:
                progress["words"][word]["wrong"] += 1

                pos = random.randint(3, min(7, len(session["queue"])))
                session["queue"].insert(pos, card)

            save_progress(progress)

            session.pop("current", None)
            session["show_meaning"] = False

    # COMPLETION
    if len(session["queue"]) == 0:
        set_id = f"{session['level']}_{session['set']}"

        if set_id not in progress["completed_sets"]:
            progress["completed_sets"].append(set_id)
            save_progress(progress)

        return f"<h2>✅ Set {session['set']} Completed!</h2><a href='/'>Back</a>"

    # CURRENT CARD
    if "current" not in session:
        card = session["queue"].pop(0)
        session["current"] = card
        session["show_meaning"] = False
    else:
        card = session["current"]

    word = card["word"]

    # STATUS
    status = "new"
    if word in progress["words"]:
        c = progress["words"][word]["correct"]
        w = progress["words"][word]["wrong"]

        if c >= 2:
            status = "mastered"
        elif w > c:
            status = "difficult"
        else:
            status = "learning"

    return render_template(
        "card.html",
        card=card,
        remaining=len(session["queue"]),
        level=session["level"],
        set_name=session["set"],
        status=status,
        show_meaning=session.get("show_meaning", False)
    )


# ------------------ LEARN ------------------

@app.route("/learn/<word>")
def learn(word):
    details = get_word_details(word)

    if not details:
        return f"<h2>No data found for {word}</h2><a href='/card'>Back</a>"

    return render_template(
        "learn.html",
        word=details["word"],
        meaning=details["meaning"],
        example=details["example"],
        perfect=details["perfect"],
        reflexive=details["reflexive"]
    )


# ------------------ DASHBOARD ------------------

@app.route("/dashboard")
def dashboard():
    progress = load_progress()

    words = progress.get("words", {})
    completed_sets = progress.get("completed_sets", [])

    total_words = len(words)

    mastered = 0
    learning = 0
    difficult = 0

    for w in words.values():
        c = w["correct"]
        wr = w["wrong"]

        if c >= 2:
            mastered += 1
        elif wr > c:
            difficult += 1
        else:
            learning += 1

    return render_template(
        "dashboard.html",
        total=total_words,
        mastered=mastered,
        learning=learning,
        difficult=difficult,
        completed_sets=completed_sets
    )


if __name__ == "__main__":
    app.run(debug=True)