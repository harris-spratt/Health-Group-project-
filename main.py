from flask import Flask, render_template, request, session, redirect, url_for

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Required for session management

# Hardcoded password for demo purposes
CORRECT_PASSWORD = "health123"


@app.route('/')
def home():
    return render_template("home.html")


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        password = request.form.get('password')

        if password == CORRECT_PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('tests'))
        else:
            return render_template('login.html', error="Incorrect password")

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('home'))


# Existing test routes
@app.route("/tests")
def tests():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template("tests.html")


@app.route("/h2fpef")
def h2fpef():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return "H2FPEF Test Page"


@app.route("/qrisk3")
def qrisk3():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return "QRISK3 Test Page"


@app.route("/who_cv")
def who_cv():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return "WHO CV Risk Test Page"


if __name__ == '__main__':
    app.run(debug=True)