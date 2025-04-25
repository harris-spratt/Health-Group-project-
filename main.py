import os
import sqlite3
import math
from flask import Flask, render_template, request, redirect, url_for, session, g
from werkzeug.security import check_password_hash
import pdfplumber
import re
import random

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Required for session handling
db_location = 'var/sqlite3.db'

UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"pdf"}
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Ensure upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

# Function to get the database connection
def get_db():
    # Check if the database connection is already available in `g`
    db = getattr(g, '_database', None)
    if db is None:
        # If not, establish a new connection to the SQLite database
        db = sqlite3.connect(db_location)
        db.row_factory = sqlite3.Row  # Enable accessing columns by name
        g._database = db  # Store the connection in `g`
    return db

@app.teardown_appcontext
def close_db_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# Initialize database and run schema
def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

# Function to insert data into the database
def insert_h2fpef_data(data):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        '''INSERT INTO H2FPEF (patient_name, age, bmi, E_e, pasp, af,date_of_echo) 
        VALUES (?, ?, ?, ?, ?, ?,?)''',
        (data["Patient Name"], data["Age"], data["BMI"], data["E/E Prime"], data["PAP"], data["Atrial Fibrillation"], data["Date"])
    )
    db.commit()

def insert_qrisk3_data(data):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        '''
        INSERT INTO qrisk3_data (
            patient_name,
            age,
            sex,
            ethnicity,
            smoker_status,
            bmi,
            systolic_bp,
            bp_variability,
            cholesterol_ratio,
            townsend_index,
            has_af,
            has_atypical_antipsy,
            on_corticosteroids,
            has_impotence,
            has_migraine,
            has_ra,
            has_ckd,
            has_learning_disability,
            has_sle,
            on_hypertension_treatment,
            has_type1_diabetes,
            has_type2_diabetes,
            has_family_history,
            survival_period,
            date_of_echo
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,?)
        ''',
        (
            data["Patient Name"],
            data["Age"],
            data["Sex"].lower(),
            data.get("ethnicity", 0),
            data.get("smoker_status", 0),
            data["BMI"],
            data["SBP"],
            data.get("bp_variability",0),
            data["Chol"],
            data.get("townsend_index", 0),
            data.get("has_af", False),
            data.get("has_atypical_antipsy", False),
            data.get("on_corticosteroids", False),
            data.get("has_impotence", False),
            data.get("has_migraine", False),
            data.get("has_ra", False),
            data.get("has_ckd", False),
            data.get("has_learning_disability", False),
            data.get("has_sle", False),
            data.get("on_hypertension_treatment", False),
            data.get("has_type1_diabetes", False),
            data.get("has_type2_diabetes", False),
            data.get("has_family_history", False),
            data.get("survival_period", 10),
            data.get("Date")
        )
    )
    db.commit()



# Female function
def cvd_female_raw(
    age, b_AF, b_atypicalantipsy, b_corticosteroids, b_migraine, b_ra, b_renal,
    b_semi, b_sle, b_treatedhyp, b_type1, b_type2, bmi, ethrisk, fh_cvd,
    rati, sbp, sbps5, smoke_cat, surv, town
):
    survivor = [
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        0.988876402378082, 0, 0, 0, 0, 0
    ]

    Iethrisk = [0, 0, 0.28040314333, 0.56298994142, 0.29590000851,
                0.07278537988, -0.17072135509, -0.39371043315,
                -0.32632495284, -0.17127056883]

    Ismoke = [0, 0.13386833787, 0.56200858012, 0.66749593378, 0.84948177645]

    dage = age / 10
    age_1 = dage ** -2
    age_2 = dage
    dbmi = bmi / 10
    bmi_1 = dbmi ** -2
    bmi_2 = dbmi ** -2 * math.log(dbmi)

    # Centering
    age_1 -= 0.05327484384
    age_2 -= 4.33250331879
    bmi_1 -= 0.15494617820
    bmi_2 -= 0.14446231723
    rati -= 3.47632646561
    sbp -= 123.13001251221
    sbps5 -= 9.00253772736
    town -= 0.39230883121

    a = 0
    a += Iethrisk[ethrisk]
    a += Ismoke[smoke_cat]

    # Continuous values
    a += age_1 * -8.13881092477
    a += age_2 * 0.79733376690
    a += bmi_1 * 0.29236092275
    a += bmi_2 * -4.15133002138
    a += rati * 0.15338035821
    a += sbp * 0.01313148841
    a += sbps5 * 0.00788945410
    a += town * 0.07722379059

    # Boolean values
    a += b_AF * 1.59233549693
    a += b_atypicalantipsy * 0.25237642070
    a += b_corticosteroids * 0.59520725305
    a += b_migraine * 0.30126726087
    a += b_ra * 0.21364803435
    a += b_renal * 0.65194569494
    a += b_semi * 0.12555308059
    a += b_sle * 0.75880938654
    a += b_treatedhyp * 0.50931593683
    a += b_type1 * 1.72679775105
    a += b_type2 * 1.06887732446
    a += fh_cvd * 0.45445319021

    # Interactions with age_1
    a += age_1 * (smoke_cat == 1) * -4.70571617859
    a += age_1 * (smoke_cat == 2) * -2.74303834036
    a += age_1 * (smoke_cat == 3) * -0.86608088829
    a += age_1 * (smoke_cat == 4) * 0.90241562370
    a += age_1 * b_AF * 19.93803488955
    a += age_1 * b_corticosteroids * -0.98408045236
    a += age_1 * b_migraine * 1.76349795879
    a += age_1 * b_renal * -3.58740477317
    a += age_1 * b_sle * 19.69030373864
    a += age_1 * b_treatedhyp * 11.87280973392
    a += age_1 * b_type1 * -1.24443327143
    a += age_1 * b_type2 * 6.86523420000
    a += age_1 * bmi_1 * 23.80262341214
    a += age_1 * bmi_2 * -71.18494769209
    a += age_1 * fh_cvd * 0.99467807940
    a += age_1 * sbp * 0.03413184234
    a += age_1 * town * -1.03011808020

    # Interactions with age_2
    a += age_2 * (smoke_cat == 1) * -0.07558924464
    a += age_2 * (smoke_cat == 2) * -0.11951192875
    a += age_2 * (smoke_cat == 3) * -0.10366306398
    a += age_2 * (smoke_cat == 4) * -0.13991853592
    a += age_2 * b_AF * -0.07618265101
    a += age_2 * b_corticosteroids * -0.12005364947
    a += age_2 * b_migraine * -0.06558691790
    a += age_2 * b_renal * -0.22688873086
    a += age_2 * b_sle * 0.07734794968
    a += age_2 * b_treatedhyp * 0.00096857824
    a += age_2 * b_type1 * -0.28724064624
    a += age_2 * b_type2 * -0.09711225259
    a += age_2 * bmi_1 * 0.52369958934
    a += age_2 * bmi_2 * 0.04574419012
    a += age_2 * fh_cvd * -0.07688505170
    a += age_2 * sbp * -0.00150825014
    a += age_2 * town * -0.03159341467

    # Final score calculation
    score = 100.0 * (1 - math.pow(survivor[surv], math.exp(a)))
    return score

# Male function
def cvd_male_raw(
    age, b_AF, b_atypicalantipsy, b_corticosteroids, b_impotence2, b_migraine, b_ra,
    b_renal, b_semi, b_sle, b_treatedhyp, b_type1, b_type2, bmi, ethrisk, fh_cvd,
    rati, sbp, sbps5, smoke_cat, surv, town
):
    survivor = [0] * 16
    survivor[10] = 0.977268040180206

    Iethrisk = [
        0,
        0,
        0.2771924876030828,
        0.4744636071493127,
        0.5296172991968937,
        0.03510015918629902,
        -0.3580789966932792,
        -0.4005648523216514,
        -0.41522792889830173,
        -0.26321348134749967
    ]
    Ismoke = [
        0,
        0.19128222863388983,
        0.5524158819264555,
        0.6383505302750607,
        0.7898381988185802
    ]

    dage = age / 10.0
    age_1 = math.pow(dage, -1)
    age_2 = math.pow(dage, 3)
    dbmi = bmi / 10.0
    bmi_1 = math.pow(dbmi, -2)
    bmi_2 = bmi_1 * math.log(dbmi)

    age_1 -= 0.234766781330109
    age_2 -= 77.284080505371094
    bmi_1 -= 0.149176135659218
    bmi_2 -= 0.141913309693336
    rati -= 4.300998687744141
    sbp -= 128.5715789794922
    sbps5 -= 8.756621360778809
    town -= 0.52630490064621

    a = 0

    a += Iethrisk[ethrisk]
    a += Ismoke[smoke_cat]

    a += age_1 * -17.839781666005575
    a += age_2 * 0.0022964880605765492
    a += bmi_1 * 2.4562776660536358
    a += bmi_2 * -8.301112231471135
    a += rati * 0.1734019685632711
    a += sbp * 0.012910126542553305
    a += sbps5 * 0.010251914291290456
    a += town * 0.033268201277287295

    a += b_AF * 1.468982533025846
    a += b_atypicalantipsy * 0.24561578714948888
    a += b_corticosteroids * 0.5637982613932328
    a += b_impotence2 * 0.3352614795097372
    a += b_migraine * 0.34779839342189144
    a += b_ra * 0.2114006932730158
    a += b_renal * 0.5562969939606479
    a += b_semi * 0.12177169581511542
    a += b_sle * 0.5150835761074043
    a += b_treatedhyp * 0.4931263171675913
    a += b_type1 * 1.4715694782080564
    a += b_type2 * 1.1512740242281486
    a += fh_cvd * 0.460102515331084

    score = 100.0 * (1 - math.pow(survivor[surv], math.exp(a)))
    return score

# Main function to choose the correct function
def calculate_qrisk3_result(data):
    print("Input data received:", data)  # Debug: print input dictionary
    sex = data.get("Sex", "").lower()  # Should be "female" or "male"
    age = float(data.get("Age", 0))
    b_AF = int(data.get("has_af", 0))
    b_atypicalantipsy = int(data.get("has_atypical_antipsy", 0))
    b_corticosteroids = int(data.get("on_corticosteroids", 0))
    b_impotence2 = int(data.get("has_impotence", 0))
    b_migraine = int(data.get("has_migraine", 0))
    b_ra = int(data.get("has_ra", 0))
    b_renal = int(data.get("has_ckd", 0))
    b_semi = int(data.get("has_learning_disability", 0))  # Assuming this maps correctly
    b_sle = int(data.get("has_sle", 0))
    b_treatedhyp = int(data.get("on_hypertension_treatment", 0))
    b_type1 = int(data.get("has_type1_diabetes", 0))
    b_type2 = int(data.get("has_type2_diabetes", 0))
    bmi = float(data.get("BMI", 0))
    ethrisk = int(data.get("ethnicity", 0))
    fh_cvd = int(data.get("has_family_history", 0))
    rati = float(data.get("Chol", 0))  # assuming this is 'chol' or 'cholesterol_ratio'
    sbp = float(data.get("SBP", 0))
    sbps5 = float(data.get("bp_variability", 0))
    smoke_cat = int(data.get("smoker_status", 0))
    surv = int(data.get("survival_period", 10))
    town = 0

    # Choose the function based on sex
    if sex == "female":
        print("Calling cvd_female_raw with:", age, b_AF, b_atypicalantipsy, b_corticosteroids, b_migraine,
              b_ra, b_renal, b_semi, b_sle, b_treatedhyp, b_type1, b_type2, bmi, ethrisk, fh_cvd,
              rati, sbp, sbps5, smoke_cat, surv, town)  # Debug

        return cvd_female_raw(
            age, b_AF, b_atypicalantipsy, b_corticosteroids, b_migraine, b_ra, b_renal,
            b_semi, b_sle, b_treatedhyp, b_type1, b_type2, bmi, ethrisk, fh_cvd,
            rati, sbp, sbps5, smoke_cat, surv, town
        )
    elif sex == "male":
        return cvd_male_raw(
            age, b_AF, b_atypicalantipsy, b_corticosteroids, b_impotence2, b_migraine, b_ra,
            b_renal, b_semi, b_sle, b_treatedhyp, b_type1, b_type2, bmi, ethrisk, fh_cvd,
            rati, sbp, sbps5, smoke_cat, surv, town
        )
    else:
        return None  # Return None if sex is neither "female" nor "male"

def calculate_h2fpef_result(data):
    # Extracting data from the input dictionary and converting to float if necessary
    age = float(data.get("Age", 0))
    bmi = float(data.get("BMI", 0))
    ee_prime = float(data.get("E/E Prime", 0))
    pasp = float(data.get("PAP", 0))
    af = 1 if data.get("Atrial Fibrillation") else 0  # Convert boolean to 1/0

    # Check if all necessary values are present (age, bmi, ee_prime, pasp)
    if age and bmi and ee_prime and pasp is not None:
        # Calculating y using the given formula
        y = (-9.1917 + 0.0451 * age + 0.1307 * bmi + 0.0859 * ee_prime + 0.0520 * pasp + 1.6997 * af)

        # Calculate Z (e^y)
        Z = math.exp(y)

        # Calculate the probability using the formula (Z / (1 + Z)) * 100
        probability = (Z / (1 + Z)) * 100

        # Round the result to two decimal places
        return round(probability, 2)
    return None  # Return None if any required value is missing

# Function to insert QRisk3 score result
# Function to insert both QRisk3 and H2FPEF results
def insert_results(data, qrisk3_score, h2fpef_score):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        '''
        INSERT INTO results 
        (patient_name, age, sex, bmi, systolic_bp, cholesterol_ratio, E_e, pasp, af, qrisk3_score, H2FPEF_score, date_of_echo) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''',
        (
            data["Patient Name"],
            int(data["Age"]),
            data["Sex"].lower(),
            float(data.get("BMI", 0)),
            float(data.get("SBP", 0)),
            float(data.get("Chol", 0)),
            float(data.get("E/E Prime", 0)),
            float(data.get("PAP", 0)),
            int(data.get("Atrial Fibrillation", 0)),
            round(float(qrisk3_score), 1),  # Store QRisk3 score with one decimal place
            float(h2fpef_score),
            data["Date"]  # Date of Echo
        )
    )
    db.commit()



# Function to extract data from the Echo test PDF
def readechotest(pdf_path, pasp=None, sbp=None, chol=None):
    extracted_text_plumber = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            extracted_text_plumber.append(page.extract_text())

    extracted_text_plumber = "\n\n".join(filter(None, extracted_text_plumber))
    text = extracted_text_plumber
    # Example extraction using regex
    #name = extract_values_from_text(text, r"Patient Name\s([A-Za-z'-]+\s+[A-Za-z'-]+)")
    name= "sample_patient"
    age = extract_values_from_text(text, r"Age\s(\d+)")
    sex = extract_values_from_text(text, r"Gender\s*([A-Za-z]+)")
    # Normalize the sex value
    if sex:
        sex = sex.strip().upper()
        if sex == "M":
            sex = "Male"
        elif sex == "F":
            sex = "Female"

    patient_id = random.randint(100000, 999999)

    # Function to safely convert values to float
    def safe_float(value):
        try:
            return float(value)
        except (ValueError, TypeError):
            return 0  # Return 0 if the conversion fails

    height_str = extract_values_from_text(extracted_text_plumber, r"Height\s([\d.]+)")
    weight_str = extract_values_from_text(extracted_text_plumber, r"Weight\s([\d.]+)")

    height = float(height_str) if height_str else None
    weight = float(weight_str) if weight_str else None

    def calculate_bmi(height, weight):
        if height and weight:
            height = height / 100
            return round(weight / (height * height), 2)
        return None

    # Ensure BMI calculation is done only if both height and weight are valid
    bmi = calculate_bmi(height, weight)

    # Dummy extraction results (you should adjust this for your own extraction logic)
    ee_prime = extract_values_from_text(extracted_text_plumber, r"E/E' sep\s([\d.]+)")
    # Use PASP passed in from the frontend
    pasp = float(pasp) if pasp else 20  # fallback to 20 if not provided
    sbp = float(sbp) if sbp else 110
    chol= float(chol) if chol else 3.5
    date = extract_values_from_text(extracted_text_plumber, r"Date\s*([\d.]+)")


    # Check for atrial fibrillation in the Indications section
    indications_match = re.search(r"Indicat(?:ion)?s?[:;]\s(.?)\sReported by", extracted_text_plumber,
                                  re.DOTALL | re.IGNORECASE)
    indications_text = indications_match.group(1) if indications_match else ""
    has_atrial_fibrillation = "atrial fibrillation" in indications_text.lower()

    # Return extracted data as a dictionary
    return {
        "Patient Name": name,
        "Age": age,
        "Sex": sex,
        "BMI": bmi,
        "E/E Prime": ee_prime,
        "PAP": pasp,
        "Atrial Fibrillation": 1 if has_atrial_fibrillation else 0,  # Return 1 for True, 0 for False
        "SBP": sbp,
        "Chol": chol,
        "Date": date
    }


# Helper function to extract values from text using regex
def extract_values_from_text(text, pattern):
    match = re.search(pattern, text, re.IGNORECASE)
    return match.group(1) if match else None

@app.route("/", methods=["GET", "POST"])
def login():
    hashed_password = "scrypt:32768:8:1$v8oSW7nWajiMxrrd$b5f09615ce676ec6352bc9de910febea5487157dfbc28cf02dbdd0be46f91ee84725319a9137c584595ffee79c972cb41efd07ec6206344bb0d1c48c9898ab78"  # full string here

    if request.method == "POST":
        entered_password = request.form.get("password")

        if check_password_hash(hashed_password, entered_password):
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
    if not session.get("authenticated"):
        return redirect(url_for("login"))
    data = None
    h2fpef_result = None  # To hold the result of the H2FPEF calculation
    qrisk_result = None

    if "uploaded_pdfs" not in session:
        session["uploaded_pdfs"] = {"h2fpef": False, "qrisk3": False, "who_cv": False}

    if request.method == "POST":
        file = request.files.get("file")
        if file and allowed_file(file.filename):
            # Instead of saving the file, process it directly from memory
            # Pass file.stream to readechotest, assuming it can handle a file-like object
            pasp_value = request.form.get("pasp")
            chol_value = request.form.get("chol")
            sbp_value = request.form.get("sbp")

            # Extract patient data from the PDF directly using the file's stream
            data = readechotest(file.stream, pasp=pasp_value, sbp=sbp_value, chol=chol_value)

            # Insert extracted data into the database
            insert_h2fpef_data(data)
            insert_qrisk3_data(data)

            # Calculate H2FPEF result using the extracted data
            h2fpef_result = calculate_h2fpef_result(data)
            # Calculate and format QRisk3 result
            qrisk_raw = calculate_qrisk3_result(data)
            if qrisk_raw is not None and h2fpef_result is not None:
                qrisk_result = f"{qrisk_raw:.1f}%"
                # Insert both results into the database
                insert_results(data, qrisk_raw, h2fpef_result)
            else:
                qrisk_result = None

            # Mark the PDF as uploaded in the session
            session["uploaded_pdfs"]["h2fpef"] = True

    # If there is any extracted data or calculation, pass it to the template
    return render_template("h2fpef.html", uploaded=session["uploaded_pdfs"]["h2fpef"], data=data, h2fpef_result=h2fpef_result, qrisk_result=qrisk_result)


@app.route('/results')
def results():
    if not session.get("authenticated"):
        return redirect(url_for("login"))
    # Get data from the database
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM results')
    results = cursor.fetchall()  # Get all rows from the query

    return render_template('results.html', results=results)
@app.route("/logout")
def logout():
    session.pop("authenticated", None)  # Clear the session
    return redirect(url_for("login"))  # Redirect to the login page

if __name__ == "__main__":
    init_db()  # Initialize database before running the app
    app.run(debug=True)



