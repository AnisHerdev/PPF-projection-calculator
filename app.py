import streamlit as st
import pandas as pd
import plotly.express as px

def calculate(ppf_amount, rate_of_interest, duration, monthly_investment):
    lifetime_interest=0
    total_interest_yearly = 0
    projection={"Month":[],"Interest":[],"Amount_in_account":[], "Invested_Amount":[], "Accumulated_Interest":[]}
    cumulative_investment = ppf_amount
    
    for i in range(duration*12):
        ppf_amount += monthly_investment
        cumulative_investment += monthly_investment
        
        interest = ppf_amount * (rate_of_interest/1200)
        total_interest_yearly += interest
        lifetime_interest += interest
        
        if (i+1)%12==0:
            ppf_amount+=total_interest_yearly
            total_interest_yearly=0
            
        projection["Month"].append(i+1)
        projection["Amount_in_account"].append(ppf_amount)
        projection["Interest"].append(interest)
        projection["Invested_Amount"].append(cumulative_investment)
        projection["Accumulated_Interest"].append(ppf_amount - cumulative_investment)
        
    return (round(ppf_amount,2), round(lifetime_interest,2),cumulative_investment , projection)

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
    st.session_state.total_amount, st.session_state.interest, st.session_state.cumulative_investment, st.session_state.projection = calculate(ppf_amount, rate_of_interest, duration, monthly_investment)

# st.markdown("""
# <style>
# div.stButton > button:first-child {
#     background-color: #4CAF50; /* Green */
#     color: white;
# }
# </style>""", unsafe_allow_html=True)
if st.columns(7)[3].button("Calculate"):
    st.session_state.total_amount, st.session_state.interest, st.session_state.cumulative_investment, st.session_state.projection = calculate(ppf_amount, rate_of_interest, duration, monthly_investment)

st.write("Total investment:", st.session_state.cumulative_investment)
st.write("Estimated maturity value:", st.session_state.total_amount)
st.write("Total interest earned:", st.session_state.interest)

st.dataframe(st.session_state.projection)
# Visualizations
if st.session_state.projection:
    df = pd.DataFrame(st.session_state.projection)

    st.subheader("Growth of Investment Over Time")
    st.area_chart(df, x="Month", y=["Invested_Amount", "Accumulated_Interest"], color=["#1f77b4", "#ff7f0e"])

    st.subheader("Maturity Breakdown")
    total_invested = duration*12*monthly_investment + ppf_amount
    total_interest = st.session_state.interest
    
    # Check if we have valid data for pie chart
    if total_invested > 0 or total_interest > 0:
        fig = px.pie(
            values=[total_invested, total_interest], 
            names=["Total Invested", "Total Interest"], 
            title="Investment vs Interest",
            color_discrete_sequence=["#1f77b4", "#ff7f0e"]
        )
        st.plotly_chart(fig)


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