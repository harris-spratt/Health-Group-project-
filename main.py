import os
from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Required for session handling

UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"pdf"}
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Ensure upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

# Set your desired password
PASSWORD = "pass"

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        entered_password = request.form.get("password")
        if entered_password == PASSWORD:
            session["authenticated"] = True
            return redirect(url_for("home"))
        else:
            return render_template("login.html", error="Incorrect password. Try again.")

    return render_template("login.html")

@app.route("/home")
def home():
    if not session.get("authenticated"):
        return redirect(url_for("login"))
    return render_template("home.html", active_page="home")

@app.route("/about")
def about():
    if not session.get("authenticated"):
        return redirect(url_for("login"))
    return render_template("about.html", active_page="about")

@app.route("/contact")
def contact():
    if not session.get("authenticated"):
        return redirect(url_for("login"))
    return render_template("contact.html", active_page="contact")

@app.route("/tests")
def tests():
    if not session.get("authenticated"):
        return redirect(url_for("login"))
    return render_template("tests.html", active_page="tests")

@app.route("/tests/h2fpef", methods=["GET", "POST"])
def h2fpef():
    if "uploaded_pdfs" not in session:
        session["uploaded_pdfs"] = {"h2fpef": False, "qrisk3": False, "who_cv": False}

    if request.method == "POST":
        file = request.files.get("file")
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
            session["uploaded_pdfs"]["h2fpef"] = True  # Mark as uploaded
            return render_template("h2fpef.html", uploaded=True)

    return render_template("h2fpef.html", uploaded=False)



@app.route("/tests/qrisk3", methods=["GET", "POST"])
def qrisk3():
    if "uploaded_pdfs" not in session:
        session["uploaded_pdfs"] = {"h2fpef": False, "qrisk3": False, "who_cv": False}

    if request.method == "POST":
        file = request.files.get("file")
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
            session["uploaded_pdfs"]["qrisk3"] = True  # Mark as uploaded
            return render_template("qrisk3.html", uploaded=True)

    return render_template("qrisk3.html", uploaded=False)


@app.route("/tests/who_cv", methods=["GET", "POST"])
def who_cv():
    if "uploaded_pdfs" not in session:
        session["uploaded_pdfs"] = {"h2fpef": False, "qrisk3": False, "who_cv": False}

    if request.method == "POST":
        file = request.files.get("file")
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
            session["uploaded_pdfs"]["who_cv"] = True  # Mark as uploaded
            return render_template("who_cv.html", uploaded=True)

    return render_template("who_cv.html", uploaded=False)


@app.route("/logout")
def logout():
    session.pop("authenticated", None)  # Clear the session
    return redirect(url_for("login"))  # Redirect to the login page

if __name__ == "__main__":
    app.run(debug=True)
import os
from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Required for session handling

UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"pdf"}
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Ensure upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

# Set your desired password
PASSWORD = "pass"

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        entered_password = request.form.get("password")
        if entered_password == PASSWORD:
            session["authenticated"] = True
            return redirect(url_for("home"))
        else:
            return render_template("login.html", error="Incorrect password. Try again.")

    return render_template("login.html")

@app.route("/home")
def home():
    if not session.get("authenticated"):
        return redirect(url_for("login"))
    return render_template("home.html", active_page="home")

@app.route("/about")
def about():
    if not session.get("authenticated"):
        return redirect(url_for("login"))
    return render_template("about.html", active_page="about")

@app.route("/contact")
def contact():
    if not session.get("authenticated"):
        return redirect(url_for("login"))
    return render_template("contact.html", active_page="contact")

@app.route("/tests")
def tests():
    if not session.get("authenticated"):
        return redirect(url_for("login"))
    return render_template("tests.html", active_page="tests")

@app.route("/tests/h2fpef", methods=["GET", "POST"])
def h2fpef():
    if "uploaded_pdfs" not in session:
        session["uploaded_pdfs"] = {"h2fpef": False, "qrisk3": False, "who_cv": False}

    if request.method == "POST":
        file = request.files.get("file")
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
            session["uploaded_pdfs"]["h2fpef"] = True  # Mark as uploaded
            return render_template("h2fpef.html", uploaded=True)

    return render_template("h2fpef.html", uploaded=False)



@app.route("/tests/qrisk3", methods=["GET", "POST"])
def qrisk3():
    if "uploaded_pdfs" not in session:
        session["uploaded_pdfs"] = {"h2fpef": False, "qrisk3": False, "who_cv": False}

    if request.method == "POST":
        file = request.files.get("file")
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
            session["uploaded_pdfs"]["qrisk3"] = True  # Mark as uploaded
            return render_template("qrisk3.html", uploaded=True)

    return render_template("qrisk3.html", uploaded=False)


@app.route("/tests/who_cv", methods=["GET", "POST"])
def who_cv():
    if "uploaded_pdfs" not in session:
        session["uploaded_pdfs"] = {"h2fpef": False, "qrisk3": False, "who_cv": False}

    if request.method == "POST":
        file = request.files.get("file")
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
            session["uploaded_pdfs"]["who_cv"] = True  # Mark as uploaded
            return render_template("who_cv.html", uploaded=True)

    return render_template("who_cv.html", uploaded=False)


@app.route("/logout")
def logout():
    session.pop("authenticated", None)  # Clear the session
    return redirect(url_for("login"))  # Redirect to the login page

if __name__ == "__main__":
    app.run(debug=True)
