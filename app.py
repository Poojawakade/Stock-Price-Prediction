elif option == "Existing User":

    st.subheader("🔐 User Login")

    username = st.text_input("Username")
    
    col1, col2 = st.columns([4,1])
    with col1:
        password = st.text_input("Password", type="password")
    with col2:
        forgot_clicked = st.button("Forgot?")

    # ---------------- LOGIN ----------------
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

    # ---------------- FORGOT PASSWORD FLOW ----------------
    if forgot_clicked:
        st.session_state.show_reset = True

    if "show_reset" in st.session_state and st.session_state.show_reset:

        st.divider()
        st.subheader("🔑 Reset Password")

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

                # Clear reset session
                del st.session_state.otp
                del st.session_state.otp_verified
                del st.session_state.reset_email
                del st.session_state.show_reset