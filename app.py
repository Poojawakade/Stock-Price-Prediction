import streamlit as st
import random
import string

st.set_page_config(page_title="Login System", page_icon="🔐")

# ---------------------------
# Session State Setup
# ---------------------------
if "users" not in st.session_state:
    st.session_state.users = {
        "user@gmail.com": "password123"
    }

if "page" not in st.session_state:
    st.session_state.page = "login"

if "otp" not in st.session_state:
    st.session_state.otp = None

if "reset_email" not in st.session_state:
    st.session_state.reset_email = None

if "otp_verified" not in st.session_state:
    st.session_state.otp_verified = False


# ---------------------------
# OTP Generator
# ---------------------------
def generate_otp():
    return ''.join(random.choices(string.digits, k=6))


# ===========================
# LOGIN PAGE
# ===========================
if st.session_state.page == "login":

    st.title("🔐 Login")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    col1, col2 = st.columns([1,1])

    with col1:
        if st.button("Login"):
            if email in st.session_state.users and st.session_state.users[email] == password:
                st.success("Login Successful 🎉")
            else:
                st.error("Invalid Email or Password")

    with col2:
        if st.button("Forgot Password?"):
            st.session_state.page = "forgot"
            st.rerun()


# ===========================
# FORGOT PASSWORD PAGE
# ===========================
elif st.session_state.page == "forgot":

    st.title("🔁 Reset Password")

    reset_email = st.text_input("Enter your registered email")

    if st.button("Send OTP"):
        if reset_email in st.session_state.users:
            otp = generate_otp()
            st.session_state.otp = otp
            st.session_state.reset_email = reset_email
            st.session_state.otp_verified = False

            # 🔥 OTP DISPLAYED ON SCREEN (Demo Mode)
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

            # Reset states
            st.session_state.otp = None
            st.session_state.otp_verified = False
            st.session_state.page = "login"
            st.rerun()

    if st.button("⬅ Back to Login"):
        st.session_state.page = "login"
        st.rerun()