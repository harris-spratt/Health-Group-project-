from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/tests")
def tests():
    return render_template("tests.html")

# Add these new routes:
@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")

# Existing test routes...
@app.route("/h2fpef")
def h2fpef():
    return "H2FPEF Test Page"

@app.route("/qrisk3")
def qrisk3():
    return "QRISK3 Test Page"

@app.route("/who_cv")
def who_cv():
    return "WHO CV Risk Test Page"

if __name__ == "__main__":
    app.run(debug=True)