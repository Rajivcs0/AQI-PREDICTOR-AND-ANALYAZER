import streamlit as st
import pandas as pd
import joblib
import numpy as np
import plotly.express as px
import sqlite3
import hashlib
import base64
import requests
from fpdf import FPDF
from io import BytesIO

# --------------- Background Image Setup ---------------
def set_background(image_file):
    with open(image_file, "rb") as img:
        encoded = base64.b64encode(img.read()).decode()
    st.markdown(f"""
        <style>
        .stApp {{
            background-image: url("data:image/png;base64,{encoded}");
            background-size: cover;
            background-attachment: fixed;
            background-repeat: no-repeat;
            background-position: center;
            color: black !important;
            font-weight: bold !important;
        }}
        .block-container {{
            background: rgba(255, 255, 255, 0.85);
            padding: 2rem;
            border-radius: 12px;
            box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
        }}
        /* Bold and black for all text */
        h1, h2, h3, h4, h5, h6, p, span, label, div, input, button, .css-1cpxqw2 {{
            color: black !important;
            font-weight: bold !important;
        }}
        </style>
        """, unsafe_allow_html=True)


set_background("Pollution.png")

# --------------- Auth: Database & Functions ---------------
def create_connection():
    return sqlite3.connect("users.db", check_same_thread=False)

def create_user_table():
    conn = create_connection()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS userstable (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL,
                    password TEXT NOT NULL
                )''')
    conn.commit()
    conn.close()

def add_user(username, password):
    conn = create_connection()
    c = conn.cursor()
    c.execute('INSERT INTO userstable (username, password) VALUES (?, ?)', (username, password))
    conn.commit()
    conn.close()

def login_user(username, password):
    conn = create_connection()
    c = conn.cursor()
    try:
        c.execute('SELECT * FROM userstable WHERE username = ? AND password = ?', (username, password))
        data = c.fetchone()
    except sqlite3.OperationalError as e:
        st.error(f"Database error: {e}")
        data = None
    conn.close()
    return data

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Ensure table is created
create_user_table()

# --------------- Login / Signup UI ---------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

menu = ["Login", "Signup"]
choice = st.sidebar.selectbox("Choose Action", menu)

if not st.session_state.logged_in:
    if choice == "Signup":
        st.subheader("🔐 Create New Account / புதிதாக கணக்கு துவங்க")
        new_user = st.text_input("Username")
        new_pass = st.text_input("Password", type="password")
        if st.button("Signup"):
            add_user(new_user, hash_password(new_pass))
            st.success("✅ Account created successfully. You can now log in.")
    else:
        st.subheader("🔑 Login to Your Account / கணக்கினை திறக்க")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            if login_user(username, hash_password(password)):
                st.session_state.logged_in = True
                st.session_state.username = username
                st.success(f"✅ Welcome, {username}!")
            else:
                st.error("❌ Invalid Username or Password")

# --------------- AQI Dashboard ---------------
if st.session_state.logged_in:
    model = joblib.load("aqi_model.pkl")
    scaler = joblib.load("aqi_scaler.pkl")

    @st.cache_data
    def load_data():
        df = pd.read_csv("aqi_india.csv")
        df["Date"] = pd.to_datetime(df["Date"])
        df["Year"] = df["Date"].dt.year
        return df

    df = load_data()

    st.title("🌍 AQI Prediction & Analysis")
    st.subheader("Analyze the Air Quality level and download the Live fetch Data")

    col1, col2, col3 = st.columns(3)
    with col1:
        selected_year = st.selectbox("Year", sorted(df["Year"].unique()))
    with col2:
        selected_date = st.date_input("Date")
    with col3:
        selected_city = st.selectbox("City", sorted(df["City"].unique()))

    selected_row = df[(df["Year"] == selected_year) & (df["Date"] == pd.to_datetime(selected_date)) & (df["City"] == selected_city)]

    if not selected_row.empty:
        row = selected_row.iloc[0]
        st.subheader("📌 Selected Data Output")
        output_cols = ["PM2.5", "PM10", "NO2", "CO", "O3"]
        st.write(row[output_cols])

        features = ['PM2.5', 'PM10', 'NO', 'NO2', 'NOx', 'NH3', 'CO', 'SO2', 'O3', 'Benzene', 'Toluene', 'Xylene']
        input_data = np.array([row[features]])
        scaled_input = scaler.transform(input_data)
        predicted_aqi = model.predict(scaled_input)[0]

        st.subheader("🥧 Pie Chart – Pollutant Distribution")
        pie_features = ["PM2.5", "PM10", "NO2", "CO", "O3", "SO2", "Benzene", "Toluene", "Xylene"]
        fig = px.pie(names=row[pie_features].index, values=row[pie_features].values, title="Pollutant Composition")
        st.plotly_chart(fig)

        st.subheader("🔢 Predicted AQI")
        st.success(f"AQI Prediction: {predicted_aqi:.2f}")

        st.subheader("📣 Air Quality Notification")
        if predicted_aqi <= 50:
            st.success("✅ Good – No worries.")
        elif predicted_aqi <= 100:
            st.info("😷 Satisfactory – Minor pollution, use mask if needed.")
        elif predicted_aqi <= 200:
            st.warning("⚠️ Moderate – Harmful for sensitive groups.")
        elif predicted_aqi <= 300:
            st.error("❌ Poor – Harmful for sensitive and elderly.")
        elif predicted_aqi <= 400:
            st.error("🚨 Very Poor – Dangerous for health.")
        else:
            st.error("🛑 Severe – Seek medical help.")
    else:
        st.warning("⚠️ No data found for selected input.")

    st.subheader("இந்தப் பிரிவானது கடந்த 2023 january இல் இருந்து 2025 may வரை இருக்கும் தகவல்கள் ஆகும். இது முற்றிலும் பயன்பாட்டாளர்களின் தகவல் பெறுவதற்கான பிரிவாகும். ஜூன் 2025 முதல் live data வை பெறும் படி இணையதளம் வடிவமைக்கப்பட்டுள்ளது. (குறிப்பு: ஜூன் 2025 மற்றும் அதற்கு படியான  தகவல்களை தினமும் பெற இயலாது. அன்றைய நாள் மட்டுமே பெறமுடியும்.) ")
    st.subheader("This section contains information from January 2023 to May 2025. This is a section entirely for users to access information. The website is designed to provide live data from June 2025 onwards. (Note: Information from June 2025 and onwards cannot be accessed daily. It can only be accessed on that day.)")
    st.markdown("---")
    st.subheader("📬 Get AQI Health Advisory by Manual Input / கையேடு உள்ளீடு மூலம் AQI சுகாதார ஆலோசனையைப் பெறுங்கள்.")
    user_aqi = st.number_input("Enter an AQI value manually / AQI மதிப்பைக் கொடுக்கவும்", min_value=0, max_value=999, step=1)
    if st.button("Get Advisory"):
        if user_aqi <= 50:
            st.success("✅ Good – Air quality is considered satisfactory. / நல்ல காற்று மற்றும் மாசற்ற சூழல் உள்ளது.")
        elif user_aqi <= 100:
            st.info("😷 Satisfactory – Acceptable air quality. / ஏற்றுக்கொள்ளக் கூடிய சுற்றுச்சூழல்.")
        elif user_aqi <= 200:
            st.warning("⚠️ Moderate – May cause health issues. / சற்று அளவான சுற்றுச்சூழல் அமைப்பு - உடல்நலம் கெடுவதற்கு வாய்ப்புள்ளது.")
        elif user_aqi <= 300:
            st.error("❌ Poor – Health effects possible./ சற்று மோசமான சுற்றுச்சூழல் - உடல்நலம் கெடுவதற்கு வாய்ப்புள்ளது.")
        elif user_aqi <= 400:
            st.error("🚨 Very Poor – Avoid going outside./ மோசமான சுற்றுச்சூழல் - வெளியில் செல்வதைத் தவிர்க்கவும்.")
        else:
            st.error("🛑 Severe – Serious health effects. / மிகவும் மோசமான சுற்றுச்சூழல் - மிகவும் உடல்நலம் பாதிக்கப்பட்டு சோர்வடையச் செய்யும்.")

    # --------------- LIVE AQI SECTION ----------------
    st.markdown("---")
    st.subheader("🌐 Real-Time AQI Data via AQICN")
    live_city = st.selectbox("Select a city", ["chennai", "mumbai", "delhi", "kolkata", "ahmedabad", "hyderabad", "jaipur", "bangalore"])

    def fetch_live_aqi(city):
        url = f"https://api.waqi.info/feed/{city}/?token=78e9eadba5ec45b20b0963b3391f1dc58f7c7330"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if data["status"] == "ok":
                return data["data"]
        return None

    if st.button("Fetch Live AQI"):
        live_data = fetch_live_aqi(live_city)
        if live_data:
            iaqi = live_data.get("iaqi", {})
            live_aqi = live_data.get("aqi", "N/A")
            live_time = live_data.get("time", {}).get("s", "Unknown")
            pollutants = {k: v['v'] for k, v in iaqi.items() if isinstance(v, dict)}

            st.success(f"✅ Live AQI for {live_city.title()} at {live_time}: {live_aqi}")

            if pollutants:
                fig2 = px.pie(names=list(pollutants.keys()), values=list(pollutants.values()),
                             title=f"Live Pollutant Composition for {live_city.title()}")
                st.plotly_chart(fig2)

            live_aqi_val = int(live_aqi) if str(live_aqi).isdigit() else -1
            if 0 <= live_aqi_val <= 50:
                st.success("✅ Good – No worries. / நல்ல காற்று மற்றும் மாசற்ற சூழல் உள்ளது.")
            elif live_aqi_val <= 100:
                st.info("😷 Satisfactory – Minor pollution. / ஏற்றுக்கொள்ளக் கூடிய சுற்றுச்சூழல்.")
            elif live_aqi_val <= 200:
                st.warning("⚠️ Moderate – Sensitive groups take care. / சற்று அளவான சுற்றுச்சூழல் அமைப்பு - உடல்நலம் கெடுவதற்கு வாய்ப்புள்ளது.")
            elif live_aqi_val <= 300:
                st.error("❌ Poor – Harmful for sensitive and elderly. / சற்று மோசமான சுற்றுச்சூழல் - உடல்நலம் கெடுவதற்கு வாய்ப்புள்ளது.")
            elif live_aqi_val <= 400:
                st.error("🚨 Very Poor – Dangerous air quality. / மோசமான சுற்றுச்சூழல் - வெளியில் செல்வதைத் தவிர்க்கவும்.")
            elif live_aqi_val > 400:
                st.error("🛑 Severe – Avoid going outside.  / மிகவும் மோசமான சுற்றுச்சூழல் - மிகவும் உடல்நலம் பாதிக்கப்பட்டு சோர்வடையச் செய்யும்.")

            st.subheader("📄 Download Live AQI Report / பதிவிறக்கி AQI படிவம்")
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            pdf.cell(200, 10, txt="Live AQI Report", ln=True, align="C")
            pdf.cell(200, 10, txt=f"City: {live_city.title()}", ln=True)
            pdf.cell(200, 10, txt=f"Time: {live_time}", ln=True)
            pdf.cell(200, 10, txt=f"AQI: {live_aqi}", ln=True)

            pdf.ln(5)
            pdf.cell(200, 10, txt="Pollutants:", ln=True)
            for pol, val in pollutants.items():
                pdf.cell(200, 10, txt=f"{pol.upper()}: {val}", ln=True)

            # ✅ Output PDF to memory and encode
            pdf_bytes = pdf.output(dest="S").encode("latin-1")

            st.download_button(
                label="📥 Download AQI Report as PDF",
                data=pdf_bytes,
                file_name=f"{live_city}_aqi_report.pdf",
                mime="application/pdf"
            )
        else:
            st.error("❌ Failed to fetch live AQI data.")

