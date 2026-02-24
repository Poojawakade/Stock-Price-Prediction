import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import bcrypt
import random
import smtplib
import os
from email.mime.text import MIMEText

# ==============================
# CONFIG
# ==============================

st.set_page_config(page_title="Stock Dashboard", layout="wide")

DATA_PATH = "synthetic_stock_dataset_1000.csv"

# Gmail credentials (REPLACE THESE)
SENDER_EMAIL = "yourgmail@gmail.com"
APP_PASSWORD = "your_16_digit_app_password"

# ==============================
# SESSION STATE INIT
# ==============================

if "users" not in st.session_state:
    st.session_state.users = {}  # {email: hashed_password}

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "reset_mode" not in st.session_state:
    st.session_state.reset_mode = False

if "otp_sent" not in st.session_state:
    st.session_state.otp_sent = False

if "generated_otp" not in st.session_state:
    st.session_state.generated_otp = None

# ==============================
# EMAIL FUNCTION
# ==============================

def send_otp_email(receiver_email, otp):
    message = MIMEText(f"Your OTP for password reset is: {otp}")
    message["Subject"] = "Password Reset OTP"
    message["From"] = SENDER_EMAIL
    message["To"] = receiver_email

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(SENDER_EMAIL, APP_PASSWORD)
        server.send_message(message)
        server.quit()
        return True
    except Exception as e:
        st.error(f"Email failed: {e}")
        return False

# ==============================
# LOGIN PAGE
# ==============================

if not st.session_state.logged_in:

    st.title("🔐 Stock Prediction Login")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("Forgot Password?"):
            st.session_state.reset_mode = True

    if st.button("Login"):
        if email in st.session_state.users:
            hashed = st.session_state.users[email]
            if bcrypt.checkpw(password.encode(), hashed):
                st.session_state.logged_in = True
                st.success("Login Successful!")
                st.rerun()
            else:
                st.error("Incorrect Password")
        else:
            st.error("User not found")

    st.divider()

    st.subheader("📝 Register")

    new_email = st.text_input("Register Email")
    new_password = st.text_input("Register Password", type="password")

    if st.button("Register"):
        if new_email not in st.session_state.users:
            hashed_pw = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt())
            st.session_state.users[new_email] = hashed_pw
            st.success("User Registered Successfully!")
        else:
            st.error("User already exists")

# ==============================
# FORGOT PASSWORD PAGE
# ==============================

if st.session_state.reset_mode:

    st.title("🔑 Reset Password")

    reset_email = st.text_input("Enter Registered Email")

    if st.button("Send OTP"):
        if reset_email in st.session_state.users:
            otp = random.randint(100000, 999999)
            success = send_otp_email(reset_email, otp)
            if success:
                st.session_state.generated_otp = str(otp)
                st.session_state.otp_sent = True
                st.success("OTP sent successfully!")
        else:
            st.error("Email not registered")

    if st.session_state.otp_sent:
        entered_otp = st.text_input("Enter OTP")
        new_password = st.text_input("New Password", type="password")

        if st.button("Reset Password"):
            if entered_otp == st.session_state.generated_otp:
                hashed_pw = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt())
                st.session_state.users[reset_email] = hashed_pw
                st.success("Password Reset Successful!")
                st.session_state.reset_mode = False
                st.session_state.otp_sent = False
                st.rerun()
            else:
                st.error("Invalid OTP")

# ==============================
# MAIN DASHBOARD
# ==============================

if st.session_state.logged_in:

    st.title("📊 Stock Dashboard")

    df = pd.read_csv(DATA_PATH)
    df['Date'] = pd.to_datetime(df['Date'])

    # ==========================
    # KPIs
    # ==========================

    col1, col2, col3 = st.columns(3)

    col1.metric("Total Records", len(df))
    col2.metric("Average Close Price", round(df["Close"].mean(), 2))
    col3.metric("Max Volume", int(df["Volume"].max()))

    st.divider()

    # ==========================
    # Chart
    # ==========================

    st.subheader("📈 Historical Price Trend")

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df['Date'],
        y=df['Close'],
        mode='lines',
        name="Close Price"
    ))
    st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # ==========================
    # STOCK DROPDOWN
    # ==========================

    stock = st.selectbox(
        "Select Stock",
        df["Stock"].unique()
    )

    # ==========================
    # PREDICTION FUNCTION
    # ==========================

    def predict_next_5_days():
        last_price = df[df["Stock"] == stock]["Close"].iloc[-1]
        predictions = []
        for i in range(5):
            change = random.uniform(-5, 5)
            last_price += change
            predictions.append(round(last_price, 2))
        return predictions

    if st.button("Predict Next 5 Days"):

        preds = predict_next_5_days()

        st.subheader("🔮 Next 5 Days Prediction")

        for i, p in enumerate(preds):
            st.write(f"Day {i+1}: {p}")

    st.divider()

    if st.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()