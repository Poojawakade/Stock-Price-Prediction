import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go
from sklearn.ensemble import RandomForestRegressor
import joblib
import sqlite3
import bcrypt

# -----------------------------
# CONFIGURATION
# -----------------------------

st.set_page_config(page_title="Stock Prediction System", layout="wide")

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

MODEL_PATH = "model.pkl"
DB_PATH = "users.db"

# -----------------------------
# DATABASE SETUP
# -----------------------------

conn = sqlite3.connect(DB_PATH, check_same_thread=False)
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS users (
    name TEXT,
    username TEXT PRIMARY KEY,
    password BLOB
)
""")
conn.commit()

# -----------------------------
# HELPER FUNCTIONS
# -----------------------------

def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt())

def check_password(password, hashed):
    return bcrypt.checkpw(password.encode(), hashed)

def train_model(df):
    df = df.dropna()

    # Predict next day Close
    df["Prediction"] = df["Close"].shift(-1)
    df = df.dropna()

    X = df[["Close"]]
    y = df["Prediction"]

    model = RandomForestRegressor()
    model.fit(X, y)

    joblib.dump(model, MODEL_PATH)

def predict_next_5_days(stock):
    model = joblib.load(MODEL_PATH)

    data = yf.download(stock, period="1y")

    last_price = data["Close"].values[-1]
    predictions = []

    current_price = last_price

    for _ in range(5):
        pred = model.predict([[current_price]])[0]
        predictions.append(pred)
        current_price = pred

    return predictions, data

# -----------------------------
# SESSION STATE
# -----------------------------

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.role = None
    st.session_state.predictions = None
    st.session_state.stock_data = None

# -----------------------------
# MAIN TITLE
# -----------------------------

st.title("📈 Stock Price Prediction Platform")

menu = st.sidebar.selectbox("Select Login Type", ["Admin Login", "User Login"])

# ======================================================
# ADMIN LOGIN
# ======================================================

if menu == "Admin Login":

    st.subheader("🔐 Admin Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            st.session_state.logged_in = True
            st.session_state.role = "admin"
            st.success("Admin Logged In Successfully")
        else:
            st.error("Invalid Admin Credentials")

    if st.session_state.logged_in and st.session_state.role == "admin":

        st.subheader("📂 Upload Dataset for Training")

        uploaded_file = st.file_uploader("Upload CSV Dataset", type=["csv"])

        if uploaded_file:
            df = pd.read_csv(uploaded_file)
            st.write("Preview:")
            st.dataframe(df.head())

            if st.button("Train Model"):
                train_model(df)
                st.success("Model Trained & Saved Successfully!")

        if st.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.role = None

# ======================================================
# USER LOGIN
# ======================================================

if menu == "User Login":

    option = st.radio("Select Option", ["New User", "Existing User"])

    # --------------------------
    # NEW USER REGISTRATION
    # --------------------------

    if option == "New User":

        st.subheader("📝 Register")

        name = st.text_input("Full Name")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Register"):

            hashed_pw = hash_password(password)

            try:
                c.execute("INSERT INTO users VALUES (?, ?, ?)",
                          (name, username, hashed_pw))
                conn.commit()
                st.success("Registration Successful! Please Login.")
            except:
                st.error("Username already exists.")

    # --------------------------
    # EXISTING USER LOGIN
    # --------------------------

    if option == "Existing User":

        st.subheader("🔑 User Login")

        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login"):

            c.execute("SELECT * FROM users WHERE username=?", (username,))
            result = c.fetchone()

            if result and check_password(password, result[2]):
                st.session_state.logged_in = True
                st.session_state.role = "user"
                st.success("Login Successful")
            else:
                st.error("Invalid Credentials")

    # ======================================================
    # USER DASHBOARD
    # ======================================================

    if st.session_state.logged_in and st.session_state.role == "user":

        st.subheader("📊 Stock Dashboard")

        stock = st.selectbox("Select Stock",
                             ["AAPL", "TSLA", "GOOG", "MSFT", "AMZN"])

        if st.button("Predict"):
            try:
                preds, data = predict_next_5_days(stock)
                st.session_state.predictions = preds
                st.session_state.stock_data = data
            except:
                st.error("Model not trained yet. Please contact admin.")
                st.stop()

        # Show Results
        if st.session_state.predictions is not None:

            data = st.session_state.stock_data
            preds = st.session_state.predictions

            # KPIs
            col1, col2, col3 = st.columns(3)

            col1.metric("Current Price",
                        round(data["Close"].values[-1], 2))

            col2.metric("52W High",
                        round(data["Close"].max(), 2))

            col3.metric("52W Low",
                        round(data["Close"].min(), 2))

            # Chart
            st.subheader("📈 Historical Price")

            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=data.index,
                y=data["Close"],
                name="Close Price"
            ))
            st.plotly_chart(fig, use_container_width=True)

            # Predictions
            st.subheader("🔮 Next 5 Days Prediction")

            for i, p in enumerate(preds):
                st.write(f"Day {i+1}: {round(p, 2)}")

        if st.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.role = None
            st.session_state.predictions = None
            st.session_state.stock_data = None