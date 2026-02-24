# ---------------- LOGIN ----------------
elif option == "Existing User":

    st.subheader("🔐 User Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    col1, col2 = st.columns([1,1])

    with col1:
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

    # 🔥 Forgot Password Button Near Login
    with col2:
        if st.button("Forgot Password?"):
            st.session_state.reset_mode = True
            st.session_state.reset_user = username
            st.rerun()


    # ================= RESET PASSWORD FLOW =================
    if "reset_mode" in st.session_state and st.session_state.reset_mode:

        st.divider()
        st.subheader("🔑 Reset Password")

        if st.button("Send OTP"):

            if os.path.exists(USER_DB):
                users = pd.read_csv(USER_DB)
                user_row = users[users["Username"] == username]

                if not user_row.empty:
                    otp = str(random.randint(100000, 999999))
                    st.session_state.otp = otp
                    st.session_state.otp_verified = False

                    # 🔥 SHOW OTP ON SCREEN (NO EMAIL)
                    st.info(f"Your OTP is: {otp}")
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
                    users["Username"] == username,
                    "Password"
                ] = hash_password(new_password)

                users.to_csv(USER_DB, index=False)

                del st.session_state.otp
                del st.session_state.otp_verified
                del st.session_state.reset_mode

                st.success("Password Updated Successfully ✅")
                st.rerun()