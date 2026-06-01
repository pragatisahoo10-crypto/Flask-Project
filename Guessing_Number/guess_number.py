# Build a game where:
# The app generates a random number (1–10)
# User submits a guess
# Show message: Too high / Too low / Correct

# 👉 Practice: logic + condition handling


from flask import Flask, request, render_template
import random

app = Flask(__name__)
app.secret_key = "secret123"

number = random.randint(1, 10)

@app.route('/', methods=["GET", "POST"])
def home():
    result = None
    if request.method == "POST":
        guess = int(request.form["guess"])

        if guess == number:
            result = "Correct!"
        elif guess > number:
            result = "Too high!"
        else:
            result = "Too low!"

    return render_template("result.html", result=result)

if __name__ == "__main__":
    app.run(debug=True)