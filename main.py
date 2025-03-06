from flask import Flask, render_template, request, session, redirect, url_for

app = Flask(__name__)
app.secret_key = 'dev'  # Change for production

# Simple user database (replace with real DB later)
USERS = {
    'admin': 'health123'
}


@app.route('/')
def home():
    return render_template('home.html', logged_in=session.get('logged_in'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if USERS.get(username) == password:
            session['logged_in'] = True
            session['username'] = username
            return redirect(url_for('tests'))
        return render_template('login.html', error="Invalid credentials")

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

@app.route("/tests")
def tests():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template("tests.html")


@app.route("/h2fpef.html")
def h2fpef():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return "H2FPEF Test Page"


@app.route("/qrisk3.html")
def qrisk3():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return "QRISK3 Test Page"


@app.route("/who_cv.html")
def who_cv():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return "WHO CV Risk Test Page"



if __name__ == '__main__':
    app.run(debug=True)