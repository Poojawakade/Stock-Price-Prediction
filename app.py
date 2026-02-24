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

# =============================
# CONFIGURATION
# =============================
st.set_page_config(page_title="Stock Prediction System", layout="wide")

DATA_PATH = "uploaded_stock_data.csv"
MODEL_PATH = "model.pkl"
USER_DB = "users.csv"

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

# -------- EMAIL CONFIG --------
SENDER_EMAIL = "your_email@gmail.com"
SENDER_PASSWORD = "your_app_password"  # Gmail App Password

# =============================
# PASSWORD HASHING
# =============================
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(stored_password, provided_password):
    return stored_password == hash_password(provided_password)

# =============================
# SEND OTP EMAIL
# =============================
def send_otp_email(receiver_email, otp):
    subject = "Password Reset OTP"
    body = f"Your OTP for password reset is: {otp}"

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = SENDER_EMAIL
    msg["To"] = receiver_email

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, receiver_email, msg.as_string())

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
# USER LOGIN / REGISTER / RESET
# =================================================
elif menu == "User Login":

    option = st.radio("Select Option", ["New User", "Existing User", "Forgot Password"])

    # ---------------- REGISTER ----------------
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

    # ---------------- LOGIN ----------------
    elif option == "Existing User":

        st.subheader("🔐 User Login")

        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login"):

            if not os.path.exists(USER_DB):
                st.error("No users registered.")
            else:
                users = pd.read_csv(USER_DB)
                user_row = users[users["Username"] == username]

                if not user_row.empty and verify_password(
                        user_row.iloc[0]["Password"], password):

                    st.session_state.logged_in = True
                    st.session_state.role = "user"
                    st.success("Login Successful ✅")
                else:
                    st.error("Invalid Credentials")

    # ---------------- FORGOT PASSWORD ----------------
    elif option == "Forgot Password":

        st.subheader("🔑 Reset Password via OTP")

        username = st.text_input("Username")

        if st.button("Send OTP"):

            if os.path.exists(USER_DB):
                users = pd.read_csv(USER_DB)
                user_row = users[users["Username"] == username]

                if not user_row.empty:
                    otp = str(random.randint(100000, 999999))
                    st.session_state.otp = otp
                    st.session_state.reset_user = username

                    try:
                        send_otp_email(user_row.iloc[0]["Email"], otp)
                        st.success("OTP Sent to Registered Email ✅")
                    except:
                        st.error("Email sending failed.")
                else:
                    st.error("User not found.")

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
                    users["Username"] == st.session_state.reset_user,
                    "Password"
                ] = hash_password(new_password)

                users.to_csv(USER_DB, index=False)

                del st.session_state.otp
                del st.session_state.otp_verified
                del st.session_state.reset_user

                st.success("Password Updated Successfully ✅")

# =================================================
# USER DASHBOARD
# =================================================
if st.session_state.logged_in and st.session_state.role == "user":

    st.title("📊 Stock Dashboard")

    if not os.path.exists(DATA_PATH):
        st.error("Dataset not uploaded by admin.")
        st.stop()

    df = pd.read_csv(DATA_PATH)
    df["Date"] = pd.to_datetime(df["Date"])

    # KPIs
    st.subheader("📌 Market Overview")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Records", len(df))
    col2.metric("Avg Close", round(df["Close"].mean(), 2))
    col3.metric("Highest Price", round(df["High"].max(), 2))
    col4.metric("Lowest Price", round(df["Low"].min(), 2))

    st.divider()

    # Stock Selection
    stock_list = df["Stock"].unique()
    selected_stock = st.selectbox("Select Stock", stock_list)
    stock_df = df[df["Stock"] == selected_stock]

    # Chart
    st.subheader("📈 Historical Chart")

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=stock_df["Date"],
        y=stock_df["Close"],
        mode="lines",
        name="Close"
    ))

    st.plotly_chart(fig, use_container_width=True)

    # Prediction
    if st.button("🔮 Predict Next 5 Days"):

        if not os.path.exists(MODEL_PATH):
            st.error("Model not trained.")
            st.stop()

        model = joblib.load(MODEL_PATH)
        last_price = stock_df["Close"].values[-1]
        predictions = predict_next_5_days(model, last_price)

        st.subheader("📅 5-Day Forecast")

        for i, p in enumerate(predictions):
            st.write(f"Day {i+1}: ₹ {round(p,2)}")

        avg_pred = np.mean(predictions)

        if avg_pred > last_price * 1.02:
            recommendation = "🟢 BUY"
        elif avg_pred < last_price * 0.98:
            recommendation = "🔴 SELL"
        else:
            recommendation = "🟡 HOLD"

        st.subheader("📢 Recommendation")
        st.success(recommendation)

    if st.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.role = None
        st.rerun()