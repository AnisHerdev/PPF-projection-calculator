import streamlit as st

def calculate(ppf_amount, rate_of_interest, duration):
    interest = ppf_amount * (rate_of_interest/100) * (duration/12)
    return (interest + ppf_amount, interest)

st.header("PPF Projection Calculator")

left_column, right_column = st.columns(2)

ppf_amount = left_column.number_input(
    label="Enter the PPF Amount",
    min_value=0,
    max_value=1_000_000,
    value=100_000,
    step=1_000,
    help="Enter the initial amount you already have in your PPF account."
)
monthly_investment = left_column.number_input(
    label="Enter the Monthly Investment",
    min_value=0,
    max_value=1_50_000,
    value=1_000,
    step=1_000,
    help="Enter the amount you want to invest monthly in your PPF account."
)
rate_of_interest = right_column.number_input(
    label="Enter your Rate of Interest",
    min_value=0.0,
    max_value=100.0,
    value=7.1,
    step=0.1,
    help="Enter the rate of interest for your PPF account."
)
duration_unit = right_column.radio("Select Duration Unit", ["Months", "Years"])

duration = right_column.number_input(
    label=f"Enter your Duration (in {duration_unit})",
    min_value=0,
    max_value=100,
    value=12 if duration_unit == "Months" else 1,
    step=1,
    help="Enter the duration for your PPF account."
)

if duration_unit == "Years":
    duration_in_months = duration * 12
else:
    duration_in_months = duration

if "projection" not in st.session_state:
    st.session_state.projection, st.session_state.interest = calculate(ppf_amount, rate_of_interest, duration_in_months)

if st.columns(7)[3].button("Calculate"):
    st.session_state.projection, st.session_state.interest = calculate(ppf_amount, rate_of_interest, duration_in_months)

st.write("Your PPF projection is:", st.session_state.projection)
st.write("Your PPF interest is:", st.session_state.interest)
