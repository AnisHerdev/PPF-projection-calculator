import streamlit as st
import pandas as pd
import plotly.express as px

def format_indian_currency(value):
    value = float(value)
    s = "{:.2f}".format(value)
    integer_part, decimal_part = s.split('.')
    
    if len(integer_part) <= 3:
        return f"₹ {integer_part}.{decimal_part}"
        
    last_3 = integer_part[-3:]
    rest = integer_part[:-3]
    
    # Insert commas every 2 digits in 'rest' from right to left
    rest_reversed = rest[::-1]
    chunks = [rest_reversed[i:i+2] for i in range(0, len(rest_reversed), 2)]
    rest_formatted = ",".join(chunks)[::-1]
    
    return f"₹ {rest_formatted},{last_3}.{decimal_part}"
    
def calculate(ppf_amount, rate_of_interest, duration, investment_amount, frequency):
    lifetime_interest=0
    total_interest_yearly = 0
    projection={"Month":[],"Interest":[],"Amount_in_account":[], "Invested_Amount":[], "Accumulated_Interest":[]}
    cumulative_investment = ppf_amount
    
    for i in range(duration*12):
        # Add investment based on frequency
        if frequency == "Monthly":
            ppf_amount += investment_amount
            cumulative_investment += investment_amount
        elif frequency == "Yearly":
            # Add yearly investment at the start of the financial year (Month 1, 13, 25...)
            if i % 12 == 0:
                ppf_amount += investment_amount
                cumulative_investment += investment_amount
        
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
        
    return (round(ppf_amount,2), round(lifetime_interest,2), cumulative_investment, projection)

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

investment_frequency = left_column.radio("Investment Frequency", ["Monthly", "Yearly"])

investment_amount = left_column.number_input(
    label=f"Enter the {investment_frequency} Investment",
    min_value=0,
    max_value=1_50_000,
    value=1_000 if investment_frequency == "Monthly" else 12_000,
    step=1_000,
    help=f"Enter the amount you want to invest {investment_frequency.lower()} in your PPF account."
)

if investment_frequency == "Monthly":
    left_column.caption("Note: This calculation assumes investment is made before the 5th of every month.")
    if investment_amount * 12 > 150000:
        st.warning("Note: Maximum investment in PPF is ₹1.5 Lakhs per year.")
else:
    left_column.caption("Note: This calculation assumes investment is made before the 5th of April every year.")
    if investment_amount > 150000:
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
    st.session_state.total_amount, st.session_state.interest, st.session_state.cumulative_investment, st.session_state.projection = calculate(ppf_amount, rate_of_interest, duration, investment_amount, investment_frequency)

if st.columns(7)[3].button("Calculate"):
    st.session_state.total_amount, st.session_state.interest, st.session_state.cumulative_investment, st.session_state.projection = calculate(ppf_amount, rate_of_interest, duration, investment_amount, investment_frequency)


col1, col2, col3 = st.columns(3)
col1.metric("Total Investment", format_indian_currency(st.session_state.cumulative_investment))
col2.metric("Maturity Value", format_indian_currency(st.session_state.total_amount))
col3.metric("Total Interest", format_indian_currency(st.session_state.interest))

# Visualizations
if st.session_state.projection:
    df = pd.DataFrame(st.session_state.projection)
    
    st.subheader("Projection Table")
    breakdown_type = st.radio("View Projection Breakdown", ["Monthly", "Yearly"], horizontal=True)
    
    if breakdown_type == "Yearly":
        # Filter for end of each year (Month 12, 24, 36...)
        df_display = df[df['Month'] % 12 == 0].copy()
        df_display['Year'] = df_display['Month'] // 12
        # Reorder columns to show Year first
        cols = ['Year'] + [col for col in df_display.columns if col != 'Year']
        st.dataframe(df_display[cols], hide_index=True)
    else:
        st.dataframe(df, hide_index=True)

    st.subheader("Growth of Investment Over Time")
    st.area_chart(df, x="Month", y=["Invested_Amount", "Accumulated_Interest"], color=["#1f77b4", "#ff7f0e"])

    st.subheader("Maturity Breakdown")
    total_invested = st.session_state.cumulative_investment
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