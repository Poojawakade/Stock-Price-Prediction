import streamlit as st
import random
import string

st.set_page_config(page_title="Login System", page_icon="🔐")

# ---------------------------
# Dummy user database
# ---------------------------
if "users" not in st.session_state:
    st.session_state.users = {
        "user@gmail.com": "password123"
    }

if "otp" not in st.session_state:
    st.session_state.otp = None

if "reset_email" not in st.session_state:
    st.session_state.reset_email = None

if "otp_verified" not in st.session_state:
    st.session_state.otp_verified = False


# ---------------------------
# Helper function to generate OTP
# ---------------------------
def generate_otp():
    return ''.join(random.choices(string.digits, k=6))


# ---------------------------
# Tabs: Login / Forgot Password
# ---------------------------
tab1, tab2 = st.tabs(["Login", "Forgot Password"])

# ===========================
# LOGIN TAB
# ===========================
with tab1:
    st.subheader("Login")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if email in st.session_state.users and st.session_state.users[email] == password:
            st.success("Login Successful 🎉")
        else:
            st.error("Invalid Email or Password")


# ===========================
# FORGOT PASSWORD TAB
# ===========================
with tab2:
    st.subheader("Forgot Password")

    reset_email = st.text_input("Enter your registered email")

    if st.button("Send OTP"):
        if reset_email in st.session_state.users:
            otp = generate_otp()
            st.session_state.otp = otp
            st.session_state.reset_email = reset_email
            st.session_state.otp_verified = False

            # 🔥 OTP SHOWN ON SCREEN (Demo Mode)
            st.info(f"Your OTP is: {otp}")

        else:
            st.error("Email not registered")

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
            st.session_state.users[st.session_state.reset_email] = new_password
            st.success("Password Reset Successful 🎉")
            st.session_state.otp = None
            st.session_state.otp_verified = False