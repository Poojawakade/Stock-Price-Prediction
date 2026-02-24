import streamlit as st
import pandas as pd
import numpy as np
import os
import joblib
import plotly.graph_objects as go
import hashlib
import smtplib
import random
from email.mime.text import MIMEText
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split

# Optional for local development
try:
    from dotenv import load_dotenv
    load_dotenv()
except:
    pass

# =============================
# CONFIGURATION
# =============================
st.set_page_config(page_title="Stock Prediction System", layout="wide")

DATA_PATH = "uploaded_stock_data.csv"
MODEL_PATH = "model.pkl"
USER_DB = "users.csv"

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

# =============================
# PASSWORD HASHING
# =============================
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(stored_password, provided_password):
    return stored_password == hash_password(provided_password)

# =============================
# HYBRID EMAIL CONFIG
# =============================
def get_email_credentials():
    # 1️⃣ Try Streamlit Cloud secrets
    try:
        if "EMAIL" in st.secrets and "EMAIL_PASSWORD" in st.secrets:
            return st.secrets["EMAIL"], st.secrets["EMAIL_PASSWORD"]
    except:
        pass

    # 2️⃣ Try local .env
    email = os.getenv("EMAIL")
    password = os.getenv("EMAIL_PASSWORD")

    if email and password:
        return email, password

    return None, None


def send_otp_email(receiver_email, otp):
    sender_email, sender_password = get_email_credentials()

    if not sender_email or not sender_password:
        st.error("❌ Email credentials not configured.")
        return False

    try:
        msg = MIMEText(f"Your OTP for password reset is: {otp}")
        msg["Subject"] = "Password Reset OTP"
        msg["From"] = sender_email
        msg["To"] = receiver_email

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, receiver_email, msg.as_string())
        server.quit()

        return True

    except Exception as e:
        st.error(f"Email Error: {e}")
        return False

# =============================
# TRAIN MODEL
# =============================
def train_model(df):
    X = df[["Close"]]
    y = df["Target_Next_Close"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    model = LinearRegression()
    model.fit(X_train, y_train)

    joblib.dump(model, MODEL_PATH)

    return model.score(X_test, y_test)

# =============================
# PREDICT 5 DAYS
# =============================
def predict_next_5_days(model, last_price):
    predictions = []
    current_price = last_price

    for _ in range(5):
        pred = model.predict([[current_price]])[0]
        predictions.append(pred)
        current_price = pred

    return predictions

# =============================
# SESSION INIT
# =============================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.role = None

# =============================
# MAIN MENU
# =============================
st.title("📈 Stock Price Prediction System")
menu = st.sidebar.selectbox("Select Role", ["Home", "Admin Login", "User Login"])

# =================================================
# HOME
# =================================================
if menu == "Home":
    st.write("Welcome to the AI Stock Prediction Platform 🚀")

# =================================================
# ADMIN LOGIN
# =================================================
elif menu == "Admin Login":

    st.subheader("🔐 Admin Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            st.session_state.logged_in = True
            st.session_state.role = "admin"
            st.success("Admin Login Successful ✅")
        else:
            st.error("Invalid Credentials")

# ---------------- ADMIN DASHBOARD ----------------
if st.session_state.logged_in and st.session_state.role == "admin":

    st.subheader("📂 Upload Dataset")
    uploaded_file = st.file_uploader("Upload CSV", type=["csv"])

    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        df.to_csv(DATA_PATH, index=False)
        st.success("Dataset Uploaded Successfully ✅")
        st.dataframe(df.head())

    if os.path.exists(DATA_PATH):
        df = pd.read_csv(DATA_PATH)

        st.subheader("🤖 Train Model")

        if st.button("Train Model"):
            if "Target_Next_Close" not in df.columns:
                st.error("Dataset must contain 'Target_Next_Close'")
            else:
                acc = train_model(df)
                st.success(f"Model Trained ✅ | Accuracy: {round(acc*100,2)}%")

    if st.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.role = None
        st.rerun()

# =================================================
# USER LOGIN + RESET
# =================================================
elif menu == "User Login":

    option = st.radio("Select Option", ["New User", "Existing User"])

    # REGISTER
    if option == "New User":

        st.subheader("📝 Register")

        name = st.text_input("Full Name")
        email = st.text_input("Email")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Register"):

            hashed_password = hash_password(password)
            new_user = pd.DataFrame([[name, email, username, hashed_password]],
                                    columns=["Name", "Email", "Username", "Password"])

            if os.path.exists(USER_DB):
                users = pd.read_csv(USER_DB)

                if username in users["Username"].values:
                    st.error("Username already exists")
                else:
                    users = pd.concat([users, new_user], ignore_index=True)
                    users.to_csv(USER_DB, index=False)
                    st.success("Registered Successfully ✅")
            else:
                new_user.to_csv(USER_DB, index=False)
                st.success("Registered Successfully ✅")

    # LOGIN
    elif option == "Existing User":

        st.subheader("🔐 User Login")

        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            if os.path.exists(USER_DB):
                users = pd.read_csv(USER_DB)
                user_row = users[users["Username"] == username]

                if not user_row.empty and verify_password(
                        user_row.iloc[0]["Password"], password):
                    st.session_state.logged_in = True
                    st.session_state.role = "user"
                    st.success("Login Successful ✅")
                else:
                    st.error("Invalid Credentials")
            else:
                st.error("No users registered.")

        st.divider()
        st.subheader("🔑 Forgot Password")

        reset_email = st.text_input("Enter Registered Email")

        if st.button("Send OTP"):
            if os.path.exists(USER_DB):
                users = pd.read_csv(USER_DB)
                user_row = users[users["Email"] == reset_email]

                if not user_row.empty:
                    otp = str(random.randint(100000, 999999))
                    st.session_state.otp = otp
                    st.session_state.reset_email = reset_email

                    if send_otp_email(reset_email, otp):
                        st.success("OTP Sent Successfully ✅")
                else:
                    st.error("Email not found.")
            else:
                st.error("No users registered.")

        if "otp" in st.session_state:
            entered_otp = st.text_input("Enter OTP")

            if st.button("Verify OTP"):
                if entered_otp == st.session_state.otp:
                    st.session_state.otp_verified = True
                    st.success("OTP Verified ✅")
                else:
                    st.error("Invalid OTP")

        if "otp_verified" in st.session_state and st.session_state.otp_verified:

            new_password = st.text_input("New Password", type="password")

            if st.button("Update Password"):

                users = pd.read_csv(USER_DB)
                users.loc[
                    users["Email"] == st.session_state.reset_email,
                    "Password"
                ] = hash_password(new_password)

                users.to_csv(USER_DB, index=False)

                st.success("Password Updated Successfully ✅")

                del st.session_state.otp
                del st.session_state.otp_verified
                del st.session_state.reset_email