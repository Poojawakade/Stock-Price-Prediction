import streamlit as st
import random
import string

st.set_page_config(page_title="Stock Price Prediction System")

# --------------------------
# Session Setup
# --------------------------
if "users" not in st.session_state:
    st.session_state.users = {}

if "page" not in st.session_state:
    st.session_state.page = "main"

if "otp" not in st.session_state:
    st.session_state.otp = None

if "reset_user" not in st.session_state:
    st.session_state.reset_user = None

if "otp_verified" not in st.session_state:
    st.session_state.otp_verified = False


# --------------------------
# OTP Generator
# --------------------------
def generate_otp():
    return ''.join(random.choices(string.digits, k=6))


# --------------------------
# MAIN PAGE (Register/Login Option)
# --------------------------
if st.session_state.page == "main":

    st.title("📈 Stock Price Prediction System")

    option = st.radio("Select Option", ["New User", "Existing User"])

    # ======================
    # REGISTER
    # ======================
    if option == "New User":
        st.subheader("📝 Register")

        full_name = st.text_input("Full Name")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Submit"):
            if username in st.session_state.users:
                st.error("Username already exists")
            else:
                st.session_state.users[username] = password
                st.success("User Registered Successfully ✅")

    # ======================
    # LOGIN
    # ======================
    if option == "Existing User":
        st.subheader("🔐 Login")

        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        col1, col2 = st.columns([1,1])

        with col1:
            if st.button("Login"):
                if username in st.session_state.users and st.session_state.users[username] == password:
                    st.success("Login Successful 🎉")
                else:
                    st.error("Invalid Username or Password")

        with col2:
            if st.button("Forgot Password?"):
                st.session_state.page = "forgot"
                st.session_state.reset_user = username
                st.rerun()


# --------------------------
# FORGOT PASSWORD PAGE
# --------------------------
elif st.session_state.page == "forgot":

    st.title("🔁 Reset Password")

    username = st.text_input("Enter your Username")

    if st.button("Send OTP"):
        if username in st.session_state.users:
            otp = generate_otp()
            st.session_state.otp = otp
            st.session_state.reset_user = username
            st.session_state.otp_verified = False

            # 🔥 OTP SHOWN ON SCREEN
            st.info(f"Your OTP is: {otp}")

        else:
            st.error("Username not found")

    if st.session_state.otp:
        entered_otp = st.text_input("Enter OTP")

        if st.button("Verify OTP"):
            if entered_otp == st.session_state.otp:
                st.session_state.otp_verified = True
                st.success("OTP Verified ✅")
            else:
                st.error("Invalid OTP")

    if st.session_state.otp_verified:
        new_password = st.text_input("Enter New Password", type="password")

        if st.button("Reset Password"):
            st.session_state.users[st.session_state.reset_user] = new_password
            st.success("Password Reset Successful 🎉")

            st.session_state.otp = None
            st.session_state.otp_verified = False
            st.session_state.page = "main"
            st.rerun()

    if st.button("⬅ Back"):
        st.session_state.page = "main"
        st.rerun()