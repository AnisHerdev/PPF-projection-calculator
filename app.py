import streamlit as st

def calculate(ppf_amount, rate_of_interest, duration, monthly_investment):
    lifetime_interest=0
    total_interest_yearly = 0
    projection={"Month":[],"Interest":[],"Amount_in_account":[]}
    for i in range(duration*12):
        ppf_amount += monthly_investment
        interest = round(ppf_amount * (rate_of_interest/1200),2)
        total_interest_yearly += interest
        lifetime_interest += interest
        
        if (i+1)%12==0:
            ppf_amount+=total_interest_yearly
            total_interest_yearly=0
        projection["Month"].append(i+1)
        projection["Amount_in_account"].append(ppf_amount)
        projection["Interest"].append(interest)
        
    return (ppf_amount, lifetime_interest, projection)

st.header("PPF Projection Calculator")

left_column, right_column = st.columns(2)

ppf_amount = left_column.number_input(
    label="Enter the PPF Amount",
    min_value=0,
    max_value=1_000_000,
    value=100_000,
    step=1_000,
    help="Enter the initial lump sum deposit for your PPF account."
)
monthly_investment = left_column.number_input(
    label="Enter the Monthly Investment",
    min_value=0,
    max_value=1_50_000,
    value=1_000,
    step=1_000,
    help="Enter the amount you want to invest monthly in your PPF account."
)
left_column.caption("Note: This calculation assumes investment is made before the 5th of every month.")
if monthly_investment * 12 > 150000:
    st.warning("Note: Maximum investment in PPF is ₹1.5 Lakhs per year.")
rate_of_interest = right_column.number_input(
    label="Enter your Rate of Interest",
    min_value=0.0,
    max_value=100.0,
    value=7.1,
    step=0.1,
    help="Enter the rate of interest for your PPF account."
)

duration = right_column.number_input(
    label=f"Enter your Duration (in Years)",
    min_value=0,
    max_value=100,
    value=15,
    step=1,
    help="Enter the duration for your PPF account."
)
if duration<15:
    st.error("Duration should be a minimum of 15 years")

if "projection" not in st.session_state:
    st.session_state.total_amount, st.session_state.interest, st.session_state.projection = calculate(ppf_amount, rate_of_interest, duration, monthly_investment)

if st.columns(7)[3].button("Calculate"):
    st.session_state.total_amount, st.session_state.interest, st.session_state.projection = calculate(ppf_amount, rate_of_interest, duration, monthly_investment)

st.write("Total investment:", duration*12*monthly_investment+ppf_amount)
st.write("Estimated maturity value:", st.session_state.total_amount)
st.write("Total interest earned:", st.session_state.interest)
st.dataframe(st.session_state.projection)

with st.expander("Important Information about PPF"):
    st.markdown("""
    ### Why invest before the 5th?
    Interest in a PPF account is calculated on the **lowest balance** between the 5th and the last day of the month. 
    If you deposit after the 5th, you lose interest on that deposit for the entire month. 
    To maximize returns, always deposit on or before the 5th.

    ### Key Rules
    - **Interest Rate**: Currently 7.1% p.a. (subject to quarterly revision by the Govt).
    - **Investment Limits**: Minimum ₹500, Maximum ₹1.5 Lakh per financial year.
    - **Lock-in Period**: 15 years. Partial withdrawals allowed after 5 years.
    - **Tax Benefits**: EEE Status - Principal, Interest, and Maturity amount are all tax-free.
    - **Compounding**: Interest is calculated monthly but compounded annually.

    > **Note**: This calculator projects returns based on the current interest rate and does not account for **inflation**. The real value of the maturity amount may be lower in terms of purchasing power.
    """)
