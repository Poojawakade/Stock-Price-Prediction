st.subheader("📊 Stock Dashboard")

stock = st.selectbox("Select Stock",
                     ["AAPL", "TSLA", "GOOG", "MSFT", "AMZN"])

if "predictions" not in st.session_state:
    st.session_state.predictions = None
    st.session_state.stock_data = None

if st.button("Predict"):

    try:
        preds, data = predict_next_5_days(stock)
        st.session_state.predictions = preds
        st.session_state.stock_data = data
    except:
        st.error("Model not trained yet. Please contact admin.")
        st.stop()

# -------------------------
# SHOW KPIs & RESULTS
# -------------------------

if st.session_state.predictions is not None:

    data = st.session_state.stock_data
    preds = st.session_state.predictions

    # KPIs
    col1, col2, col3 = st.columns(3)

    col1.metric("Current Price",
                round(data['Close'].values[-1], 2))

    col2.metric("52W High",
                round(data['Close'].max(), 2))

    col3.metric("52W Low",
                round(data['Close'].min(), 2))

    # Chart
    st.subheader("📈 Historical Price Chart")

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=data.index,
        y=data['Close'],
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