import streamlit as st
import pandas as pd
import joblib
import numpy as np
import plotly.express as px
import sqlite3
import hashlib
import base64

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
            color: #222222;
        }}
        div[data-baseweb="select"] > div {{
            transition: box-shadow 0.3s ease-in-out;
        }}
        div[data-baseweb="select"]:hover > div {{
            box-shadow: 0 0 15px 4px rgba(255, 255, 255, 0.6);
            border-radius: 10px;
        }}
        input[type="text"]:hover,
        input[type="number"]:hover,
        input[type="date"]:hover {{
            box-shadow: 0 0 15px 4px rgba(255, 255, 255, 0.6);
            border-radius: 10px;
        }}
        .block-container {{
            background: rgba(255, 255, 255, 0.85);
            padding: 2rem;
            border-radius: 12px;
            box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
        }}
        </style>
        """, unsafe_allow_html=True
    )

set_background("Pollution.png")

# --------------- Auth: Database & Functions ---------------
def create_connection():
    return sqlite3.connect("users.db")

def create_user_table():
    conn = create_connection()
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS userstable(username TEXT, password TEXT)')
    conn.commit()
    conn.close()

def add_user(username, password):
    conn = create_connection()
    c = conn.cursor()
    c.execute('INSERT INTO userstable(username, password) VALUES (?,?)', (username, password))
    conn.commit()
    conn.close()

def login_user(username, password):
    conn = create_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM userstable WHERE username = ? AND password = ?', (username, password))
    data = c.fetchall()
    conn.close()
    return data

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

create_user_table()

# --------------- Login / Signup UI ---------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

menu = ["Login", "Signup"]
choice = st.sidebar.selectbox("Choose Action", menu)

if not st.session_state.logged_in:
    if choice == "Signup":
        st.subheader("🔐 Create New Account")
        new_user = st.text_input("Username")
        new_pass = st.text_input("Password", type="password")
        if st.button("Signup"):
            add_user(new_user, hash_password(new_pass))
            st.success("✅ Account created successfully. You can now log in.")
    else:
        st.subheader("🔑 Login to Your Account")
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

    st.title("🌍 AQI Prediction & Analysis - Jan 2023 to May 2025")
    st.markdown("Select a date, year, and city to predict and visualize AQI levels.")

    col1, col2, col3 = st.columns(3)
    with col1:
        selected_year = st.selectbox("Year", sorted(df["Year"].unique()))
    with col2:
        selected_date = st.date_input("Date")
    with col3:
        selected_city = st.selectbox("City", sorted(df["City"].unique()))

    selected_row = df[
        (df["Year"] == selected_year) &
        (df["Date"] == pd.to_datetime(selected_date)) &
        (df["City"] == selected_city)
    ]

    if not selected_row.empty:
        row = selected_row.iloc[0]

        st.subheader("📌 Selected Data Output")
        output_cols = ["PM2.5", "PM10", "NO2", "CO", "O3"]
        st.write(row[output_cols])

        features = ['PM2.5', 'PM10', 'NO', 'NO2', 'NOx', 'NH3', 'CO', 'SO2',
                    'O3', 'Benzene', 'Toluene', 'Xylene']
        input_data = np.array([row[features]])
        scaled_input = scaler.transform(input_data)
        predicted_aqi = model.predict(scaled_input)[0]

        st.subheader("🥧 Pie Chart – Pollutant Distribution")
        pie_features = ["PM2.5", "PM10", "NO2", "CO", "O3", "SO2", "Benzene", "Toluene", "Xylene"]
        pie_data = row[pie_features]
        fig = px.pie(
            names=pie_data.index,
            values=pie_data.values,
            title="Pollutant Composition"
        )
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

        st.markdown(f"**AQI Level:** {predicted_aqi:.2f}")
    else:
        st.warning("⚠️ No data found for selected input.")

    # --------------- Manual AQI Input Notification ---------------
    st.markdown("---")
    st.subheader("📬 Get AQI Health Advisory by Manual Input")

    user_aqi = st.number_input("Enter an AQI value manually to get air quality notification", min_value=0, max_value=999, step=1)

    if st.button("Get Advisory"):
        if user_aqi <= 50:
            msg = "✅ Good – Air quality is considered satisfactory, and air pollution poses little or no risk."
            st.success(msg)
        elif user_aqi <= 100:
            msg = "😷 Satisfactory – Acceptable air quality; however, there may be a concern for sensitive individuals."
            st.info(msg)
        elif user_aqi <= 200:
            msg = "⚠️ Moderate – May cause health issues for some people with sensitivities."
            st.warning(msg)
        elif user_aqi <= 300:
            msg = "❌ Poor – Health effects may be experienced by sensitive groups. Limit outdoor activities."
            st.error(msg)
        elif user_aqi <= 400:
            msg = "🚨 Very Poor – May cause respiratory issues to most people. Avoid going outside."
            st.error(msg)
        else:
            msg = "🛑 Severe – Emergency condition. Everyone may experience more serious health effects."
            st.error(msg)
