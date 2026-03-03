from flask import Flask, request, jsonify, send_from_directory, send_file
from flask_cors import CORS
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer
from my import SalaryPredictor
import uuid
import io
import os
import json

from pymongo import MongoClient
from dotenv import load_dotenv

# ---------------- ENV ----------------
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
APP_URL    = os.getenv("APP_URL", "http://localhost:5000")   # your Render URL after deploy

# ---------------- MONGO ----------------
client     = MongoClient(MONGO_URI)
db         = client["AI_Salar_Predictor"]
users_col  = db["users"]

# ---------------- APP SETUP ----------------
app = Flask(__name__, static_folder="../front-end", static_url_path="")
CORS(app, origins="*")

app.config["SECRET_KEY"]        = os.getenv("SECRET_KEY", "CHANGE_ME")
app.config["MAIL_SERVER"]       = "smtp.gmail.com"
app.config["MAIL_PORT"]         = 587
app.config["MAIL_USE_TLS"]      = True
app.config["MAIL_USERNAME"]     = os.getenv("MAIL_USERNAME")
app.config["MAIL_PASSWORD"]     = os.getenv("MAIL_PASSWORD")
app.config["MAIL_DEFAULT_SENDER"] = os.getenv("MAIL_USERNAME")

mail       = Mail(app)
serializer = URLSafeTimedSerializer(app.config["SECRET_KEY"])

# ---------------- FRONTEND ROUTES ----------------
@app.route("/")
def serve_index():
    return send_from_directory(app.static_folder, "index.html")

@app.route("/login-page")
def serve_login():
    return send_from_directory(app.static_folder, "login.html")

@app.route("/signup-page")
def serve_signup():
    return send_from_directory(app.static_folder, "signup.html")

# ---------------- AUTH ----------------
@app.route("/signup", methods=["POST"])
def signup():
    data     = request.json or {}
    email    = data.get("email", "").strip().lower()
    password = data.get("password", "").strip()

    if not email or not password:
        return jsonify({"message": "Email and password required"}), 400

    if users_col.find_one({"email": email}):
        return jsonify({"message": "User already exists"}), 400

    users_col.insert_one({"email": email, "password": password, "verified": False})

    token       = serializer.dumps(email, salt="email-verify")
    verify_link = f"{APP_URL}/verify/{token}"

    try:
        msg      = Message("Verify your Know Your Worth account", recipients=[email])
        msg.body = (
            f"Hello!\n\n"
            f"Click the link below to verify your account:\n\n"
            f"{verify_link}\n\n"
            f"This link expires in 1 hour.\n\n"
            f"— Know Your Worth Team"
        )
        mail.send(msg)
    except Exception as e:
        print("EMAIL ERROR:", e)
        # Still save user; let them know email failed
        return jsonify({"message": "Account created but email delivery failed. "
                                   "Contact support."}), 500

    return jsonify({"message": "Verification email sent! Check your inbox 📩"}), 200


@app.route("/verify/<token>")
def verify_email(token):
    try:
        email  = serializer.loads(token, salt="email-verify", max_age=3600)
        result = users_col.update_one({"email": email}, {"$set": {"verified": True}})
        if result.matched_count == 0:
            return "<h2>User not found</h2>"
        return """
        <html><body style="font-family:sans-serif;text-align:center;padding:60px">
        <h1>✅ Email Verified!</h1>
        <p>Your account is ready.</p>
        <a href="/login-page" style="display:inline-block;margin-top:20px;padding:12px 24px;
           background:linear-gradient(to right,#2563eb,#06b6d4);color:#fff;border-radius:8px;
           text-decoration:none;font-weight:bold">Go to Login →</a>
        </body></html>
        """
    except Exception:
        return "<h2>⚠️ Invalid or expired link</h2>"


@app.route("/login", methods=["POST"])
def login():
    data     = request.json or {}
    email    = data.get("email", "").strip().lower()
    password = data.get("password", "").strip()

    user = users_col.find_one({"email": email})
    if not user:
        return jsonify({"message": "User not found"}), 404
    if user["password"] != password:
        return jsonify({"message": "Wrong password"}), 401
    if not user.get("verified"):
        return jsonify({"message": "Please verify your email first"}), 403

    return jsonify({"token": str(uuid.uuid4()), "email": email}), 200

# ---------------- SALARY MODEL ----------------
import os
BASE_DIR  = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "salary_predictor_model.pkl")
DATA_PATH  = os.path.join(BASE_DIR, "global_job_salaries_200k_usd.csv")

predictor = SalaryPredictor()
if os.path.exists(MODEL_PATH):
    print("Loading existing model...")
    predictor.load_saved_model(MODEL_PATH)
else:
    print("Training model from scratch...")
    import gc
    predictor.load_data(DATA_PATH)
    predictor.train_model()
    predictor.save_model(MODEL_PATH)
    gc.collect()
    print("Model trained and saved!")
```

Also update `requirements.txt` — add this line at the top of the Build Command in Render:

Go to **Render → your service → Settings → Build Command** and change to:
```
pip install -r requirements.txt
```

And go to **Environment Variables** → add:
```
WEB_CONCURRENCY = 1
MALLOC_TRIM_THRESHOLD_ = 100000

# ---------------- PPP + FX TABLES ----------------
PPP_FACTOR = {
    "United States": 1.0,   "India": 0.32,   "Germany": 1.05,
    "United Kingdom": 1.02, "Canada": 1.03,  "Australia": 1.01,
    "Japan": 0.95,          "France": 1.01,  "China": 0.45,
    "Brazil": 0.55,         "South Africa": 0.41, "Singapore": 1.12,
}
DEFAULT_PPP = 0.75

EXCHANGE_RATE = {
    "United States": 1.0,   "India": 83.0,   "Germany": 0.92,
    "United Kingdom": 0.78, "Canada": 1.35,  "Australia": 1.52,
    "Japan": 150.0,         "France": 0.92,  "China": 7.2,
    "Brazil": 5.0,          "South Africa": 18.5, "Singapore": 1.35,
}

CURRENCY_MAP = {
    "United States":  {"symbol": "$",   "code": "USD"},
    "India":          {"symbol": "₹",   "code": "INR"},
    "Germany":        {"symbol": "€",   "code": "EUR"},
    "United Kingdom": {"symbol": "£",   "code": "GBP"},
    "Canada":         {"symbol": "C$",  "code": "CAD"},
    "Australia":      {"symbol": "A$",  "code": "AUD"},
    "Japan":          {"symbol": "¥",   "code": "JPY"},
    "France":         {"symbol": "€",   "code": "EUR"},
    "China":          {"symbol": "¥",   "code": "CNY"},
    "Brazil":         {"symbol": "R$",  "code": "BRL"},
    "South Africa":   {"symbol": "R",   "code": "ZAR"},
    "Singapore":      {"symbol": "S$",  "code": "SGD"},
}
DEFAULT_CURRENCY = {"symbol": "$", "code": "USD"}

ROLE_MULTIPLIER = {
    "frontend developer":    0.35,
    "backend developer":     0.60,
    "full stack developer":  0.70,
    "software engineer":     0.75,
    "data scientist":        1.00,
    "machine learning engineer": 1.10,
    "ai engineer":           1.15,
    "devops engineer":       0.90,
    "qa engineer":           0.40,
    "automation engineer":   0.45,
    "tester":                0.35,
    "intern":                0.20,
    "web developer":         0.40,
    "mobile developer":      0.65,
    "cloud engineer":        0.85,
}

def apply_ppp_and_fx(usd_salary, country):
    fx  = EXCHANGE_RATE.get(country, 1.0)
    ppp = PPP_FACTOR.get(country, DEFAULT_PPP)
    return round(usd_salary, 2), round(usd_salary * fx * ppp, 2)

def growth_projection(current_salary):
    g1 = current_salary * 1.08
    g2 = g1 * 1.08
    g3 = g2 * 1.08
    return {
        "year1": round(g1, 2), "year2": round(g2, 2), "year3": round(g3, 2),
        "year1_ppp_local": None, "year2_ppp_local": None, "year3_ppp_local": None,
    }

# ---------------- PREDICT ----------------
@app.route("/predict-salary", methods=["POST"])
def predict_salary():
    data   = request.json or {}
    jobRole = data.get("jobRole", "").strip()
    skills  = data.get("skills", "").strip()
    region  = data.get("region", "").strip()
    years   = int(data.get("yearsOfExperience", 0))

    role_key = jobRole.lower()
    if role_key not in ROLE_MULTIPLIER:
        return jsonify({"error": f"Unsupported job role: '{jobRole}'. "
                                  "Try: Software Engineer, Data Scientist, etc."}), 400

    base_salary = predictor.predict_salary(
        job_title=jobRole, skills=skills,
        country=region,    years_of_experience=years
    )
    salary = base_salary * ROLE_MULTIPLIER[role_key]

    nominal_usd, ppp_local = apply_ppp_and_fx(salary, region)
    currency = CURRENCY_MAP.get(region, DEFAULT_CURRENCY)

    # growth in PPP local
    g = growth_projection(ppp_local)
    g["year1_ppp_local"] = round(ppp_local * 1.08, 2)
    g["year2_ppp_local"] = round(ppp_local * 1.08**2, 2)
    g["year3_ppp_local"] = round(ppp_local * 1.08**3, 2)

    return jsonify({
        "nominalSalaryUSD": nominal_usd,
        "pppSalaryLocal":   ppp_local,
        "currency":         currency,
        "growth":           g,
    }), 200

# ---------------- PDF DOWNLOAD ----------------
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

@app.route("/download-report", methods=["POST"])
def download_report():
    data    = request.json or {}
    jobRole = data.get("jobRole", "")
    skills  = data.get("skills", "")
    region  = data.get("region", "")
    years   = int(data.get("yearsOfExperience", 0))

    role_key    = jobRole.lower().strip()
    multiplier  = ROLE_MULTIPLIER.get(role_key, 0.6)
    base_salary = predictor.predict_salary(
        job_title=jobRole, skills=skills,
        country=region,    years_of_experience=years
    )
    salary = base_salary * multiplier
    nominal_usd, ppp_local = apply_ppp_and_fx(salary, region)
    currency = CURRENCY_MAP.get(region, DEFAULT_CURRENCY)
    sym      = currency["symbol"]

    buffer = io.BytesIO()
    doc    = SimpleDocTemplate(buffer, pagesize=A4,
                               leftMargin=50, rightMargin=50,
                               topMargin=60, bottomMargin=60)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("Title2", parent=styles["Title"],
                                 fontSize=22, spaceAfter=6,
                                 textColor=colors.HexColor("#1e3a8a"))
    body  = ParagraphStyle("Body2", parent=styles["Normal"],
                           fontSize=11, leading=18)

    story = [
        Paragraph("💼 Know Your Worth", title_style),
        Paragraph("AI-Powered Salary Prediction Report", styles["Heading2"]),
        Spacer(1, 16),
        Paragraph(f"<b>Role:</b> {jobRole}", body),
        Paragraph(f"<b>Region:</b> {region}", body),
        Paragraph(f"<b>Skills:</b> {skills}", body),
        Paragraph(f"<b>Experience:</b> {years} year(s)", body),
        Spacer(1, 20),
    ]

    table_data = [
        ["Metric", "Value"],
        ["Nominal Salary (USD)", f"${nominal_usd:,.2f}"],
        [f"PPP-Adjusted ({currency['code']})", f"{sym}{ppp_local:,.0f}"],
        [f"After 1 Year ({currency['code']})", f"{sym}{ppp_local*1.08:,.0f}"],
        [f"After 2 Years ({currency['code']})", f"{sym}{ppp_local*1.08**2:,.0f}"],
        [f"After 3 Years ({currency['code']})", f"{sym}{ppp_local*1.08**3:,.0f}"],
    ]
    t = Table(table_data, colWidths=[250, 220])
    t.setStyle(TableStyle([
        ("BACKGROUND",  (0, 0), (-1, 0), colors.HexColor("#2563eb")),
        ("TEXTCOLOR",   (0, 0), (-1, 0), colors.white),
        ("FONTNAME",    (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",    (0, 0), (-1, 0), 12),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1),
         [colors.HexColor("#f0f4ff"), colors.white]),
        ("FONTSIZE",    (0, 1), (-1, -1), 11),
        ("GRID",        (0, 0), (-1, -1), 0.5, colors.HexColor("#c7d2fe")),
        ("ROWPADDING",  (0, 0), (-1, -1), 8),
    ]))
    story.append(t)
    story.append(Spacer(1, 20))
    story.append(Paragraph(
        "PPP (Purchasing Power Parity) adjusts salary to reflect the true value "
        "of income based on local cost of living.",
        ParagraphStyle("Note", parent=styles["Normal"],
                       fontSize=9, textColor=colors.grey)
    ))

    doc.build(story)
    buffer.seek(0)

    return send_file(buffer, as_attachment=True,
                     download_name="salary_report.pdf",
                     mimetype="application/pdf")

# ---------------- RUN ----------------
if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
