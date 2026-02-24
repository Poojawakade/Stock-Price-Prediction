import streamlit as st
import pandas as pd
import numpy as np
import os
import joblib
import plotly.graph_objects as go
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split

# -----------------------------
# CONFIG
# -----------------------------
st.set_page_config(page_title="Stock Prediction App", layout="wide")

DATA_PATH = "uploaded_stock_data.csv"
MODEL_PATH = "model.pkl"
USER_DB = "users.csv"

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

# -----------------------------
# SESSION STATE INIT
# -----------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.role = None

# -----------------------------
# HELPER FUNCTIONS
# -----------------------------
def train_model(df):
    X = df[["Close"]]
    y = df["Target_Next_Close"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    model = LinearRegression()
    model.fit(X_train, y_train)

    joblib.dump(model, MODEL_PATH)

    accuracy = model.score(X_test, y_test)
    return accuracy


def predict_next_5_days(model, last_price):
    predictions = []
    current_price = last_price

    for _ in range(5):
        pred = model.predict([[current_price]])[0]
        predictions.append(pred)
        current_price = pred

    return predictions


# -----------------------------
# MAIN PAGE
# -----------------------------
st.title("📈 Stock Price Prediction System")

menu = st.sidebar.selectbox("Select Role", ["Home", "Admin Login", "User Login"])

# =====================================================
# HOME
# =====================================================
if menu == "Home":
    st.write("Welcome to the Stock Prediction App 🚀")

# =====================================================
# ADMIN LOGIN
# =====================================================
elif menu == "Admin Login":

    st.subheader("🔐 Admin Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):

        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            st.session_state.logged_in = True
            st.session_state.role = "admin"
            st.success("Admin Login Successful")
        else:
            st.error("Invalid Credentials")

# -----------------------------
# ADMIN DASHBOARD
# -----------------------------
if st.session_state.logged_in and st.session_state.role == "admin":

    st.subheader("📂 Upload Dataset")

    uploaded_file = st.file_uploader("Upload CSV", type=["csv"])

    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        df.to_csv(DATA_PATH, index=False)
        st.success("Dataset Uploaded Successfully")
        st.dataframe(df.head())

    if os.path.exists(DATA_PATH):

        df = pd.read_csv(DATA_PATH)

        st.subheader("🤖 Train Model")

        if st.button("Train Model"):
            if "Target_Next_Close" not in df.columns:
                st.error("Dataset must contain 'Target_Next_Close' column")
            else:
                accuracy = train_model(df)
                st.success(f"Model Trained Successfully ✅ | Accuracy: {round(accuracy*100,2)}%")

    if st.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.role = None
        st.rerun()

# =====================================================
# USER LOGIN
# =====================================================
elif menu == "User Login":

    option = st.radio("Select Option", ["New User", "Existing User"])

    # -----------------------------
    # NEW USER REGISTRATION
    # -----------------------------
    if option == "New User":

        st.subheader("📝 Register")

        name = st.text_input("Full Name")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Submit"):

            new_user = pd.DataFrame([[name, username, password]],
                                    columns=["Name", "Username", "Password"])

            if os.path.exists(USER_DB):
                users = pd.read_csv(USER_DB)
                users = pd.concat([users, new_user], ignore_index=True)
            else:
                users = new_user

            users.to_csv(USER_DB, index=False)

            st.success("User Registered Successfully ✅")

    # -----------------------------
    # EXISTING USER LOGIN
    # -----------------------------
    else:

        st.subheader("🔐 User Login")

        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login"):

            if not os.path.exists(USER_DB):
                st.error("No users registered yet.")
            else:
                users = pd.read_csv(USER_DB)

                if ((users["Username"] == username) &
                    (users["Password"] == password)).any():

                    st.session_state.logged_in = True
                    st.session_state.role = "user"
                    st.success("Login Successful ✅")
                else:
                    st.error("Invalid Credentials")

# =====================================================
# USER DASHBOARD
# =====================================================
if st.session_state.logged_in and st.session_state.role == "user":

    st.title("📊 Stock Analytics Dashboard")

    if not os.path.exists(DATA_PATH):
        st.error("Dataset not found. Please contact admin.")
        st.stop()

    df = pd.read_csv(DATA_PATH)
    df["Date"] = pd.to_datetime(df["Date"])

    # -----------------------------
    # KPIs
    # -----------------------------
    st.subheader("📌 Market Overview")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Records", len(df))
    col2.metric("Average Close", round(df["Close"].mean(), 2))
    col3.metric("Highest Price", round(df["High"].max(), 2))
    col4.metric("Lowest Price", round(df["Low"].min(), 2))

    st.divider()

    # -----------------------------
    # STOCK SELECTION
    # -----------------------------
    stock_list = df["Stock"].unique()
    selected_stock = st.selectbox("Select Stock", stock_list)

    stock_df = df[df["Stock"] == selected_stock]

    # -----------------------------
    # CHART
    # -----------------------------
    st.subheader("📈 Historical Price Chart")

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=stock_df["Date"],
        y=stock_df["Close"],
        mode="lines",
        name="Close Price"
    ))

    st.plotly_chart(fig, use_container_width=True)

    # -----------------------------
    # PREDICTION
    # -----------------------------
    if st.button("🔮 Predict Next 5 Days"):

        if not os.path.exists(MODEL_PATH):
            st.error("Model not trained yet.")
            st.stop()

        model = joblib.load(MODEL_PATH)

        last_price = stock_df["Close"].values[-1]

        predictions = predict_next_5_days(model, last_price)

        st.subheader("📅 5-Day Forecast")

        for i, p in enumerate(predictions):
            st.write(f"Day {i+1}: ₹ {round(p,2)}")

        # Recommendation
        avg_pred = np.mean(predictions)

        if avg_pred > last_price * 1.02:
            recommendation = "🟢 BUY"
        elif avg_pred < last_price * 0.98:
            recommendation = "🔴 SELL"
        else:
            recommendation = "🟡 HOLD"

        st.subheader("📢 Recommendation")
        st.success(f"{recommendation}")

    if st.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.role = None
        st.rerun()