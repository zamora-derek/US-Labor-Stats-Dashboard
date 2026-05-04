import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date


@st.cache_data  # allows streamlit to store the data and not have to get the data each time
def load_data():
    main = pd.read_csv('data/bls_data.csv', index_col='Date', parse_dates=True)
    state = pd.read_csv('data/state_data.csv', parse_dates=['Date'])
    return main, state


data, state_df = load_data()
today_date = date.today()

st.set_page_config(layout="wide")  # stretches the dashboard to fit page


tab_home, tab_wages, tab_inflation, tab_labor, tab_map = st.tabs([
    "Home",
    "Purchasing Power",
    "Inflation",
    "Labor Market",
    "Regional Trends"
])

# HOME TAB

with tab_home:
    st.title("U.S. Economic Dashboard")
    st.write("This dashboard tracks economic metrics using live data from the Bureau of Labor Statistics (BLS).")
    st.write("---")
    st.write("The values below show the change year over year.")

    cpi_cur_date = data['CPI'].last_valid_index()  # Gets the latest date where a value is present
    job_cur_date = data['Jobs'].last_valid_index()
    emps_cur_date = data['Non Farm Emp'].last_valid_index()
    unemp_cur_date = data['Unemployment Rate'].last_valid_index()

    cur_cpi = data.loc[cpi_cur_date, 'CPI'].item()  # gets data at latest date
    prev_cpi = data.loc[(cpi_cur_date - pd.DateOffset(years=1)), 'CPI'].item()  # gets data at latest date -1 year

    cur_jobs = data.loc[job_cur_date, 'Jobs'].item()
    prev_jobs = data.loc[(job_cur_date - pd.DateOffset(years=1)), 'Jobs'].item()

    cur_unemp = data.loc[unemp_cur_date, 'Unemployment Rate'].item()
    prev_unemp = data.loc[(unemp_cur_date - pd.DateOffset(years=1)), 'Unemployment Rate'].item()

    cur_emps = data.loc[cpi_cur_date, 'Non Farm Emp'].item()
    prev_emps = data.loc[(cpi_cur_date - pd.DateOffset(years=1)), 'Non Farm Emp'].item()

    # percent change in current to year prior
    cpi_per = ((cur_cpi - prev_cpi) / prev_cpi) * 100
    emps_per = ((cur_emps - prev_emps) / prev_emps) * 100

    # change in job openings and unemp rate
    jobs_change = cur_jobs - prev_jobs
    unemp_change = cur_unemp - prev_unemp

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.metric(
            label="CPI",
            value=f"{cur_cpi:.2f}",
            delta=f"{cpi_per:.2f}%",
            delta_color="inverse"  # changes color to red when positive as more inflation is bad
        )

    with c2:
        st.metric(
            label="Total Nonfarm Employees",
            value=f"{cur_emps / 1000:.1f}M",  # change from thousandths to millions for readability
            delta=f"{emps_per:.2f}%"
        )

    with c3:
        st.metric(
            label="Unemployment Rate",
            value=f"{cur_unemp:.1f}%",
            delta=f"{unemp_change:.1f} pp",  # pp = percentage points, change in percent
            delta_color="inverse"  # color change
        )
    with c4:
        st.metric(
            label="Job Openings Rate",
            value=f"{cur_jobs:.1f}%",
            delta=f"{jobs_change:.1f} pp",
        )

    st.write("---")
    st.write(
        f"Data was last updated on {data.index[-1].strftime('%B %Y')}.")

# WAGES TAB

with tab_wages:
    st.header("Nominal vs. Real Wages")

    # calculations
    data['Real Wage Raw'] = (data['Hourly Earnings'] / data['CPI']) * 100
    s_nom = data['Hourly Earnings'].dropna().iloc[0]
    s_real = data['Real Wage Raw'].dropna().iloc[0]
    data['Real Wage'] = data['Real Wage Raw'] * (s_nom / s_real)

    wages_fig = px.line(data,
                        y=['Hourly Earnings', 'Real Wage'],
                        color_discrete_map={
                            "Hourly Earnings": "blue",
                            "Real Wage": "green"
                        }
                        )
    wages_fig.add_annotation(
        text="Missing data for Real Wage on October 2025 due to government shutdown.",
        xref="paper", yref="paper",  # paper = coordinate plane
        x=0, y=-0.2,
        showarrow=False,
        font=dict(size=12, color="gray")
    )
    wages_fig.update_layout(  # makes one box on hover for both lines
        hovermode="x unified",
    )

    wages_fig.update_traces(hovertemplate="$%{y:.2f}")  # necessary for formatting text in hover box

    wages_fig.update_xaxes(range=['2006-01-01', today_date])
    wages_fig.update_yaxes(title='USD Per Hour')
    wages_fig.update_layout(legend_title_text='Wage Type')

    st.plotly_chart(wages_fig, use_container_width=True)

# INFLATION TAB

with tab_inflation:
    st.header("Inflation Analysis")
    data['Inflation Rate'] = data['CPI'].pct_change(periods=12) * 100

    inflation_plot = data[
        ['Inflation Rate']].dropna()  # drops empty rows that cannot be calculated due to missing 12 months prior

    inf_fig = px.line(inflation_plot,
                      y='Inflation Rate',
                      title="Annual Inflation Rate (Yearly % Change)")
    inf_fig.update_yaxes(title='Percent Change')


    inf_fig.update_layout(
        hovermode="x unified",
    )

    inf_fig.update_traces(hovertemplate="%{y:.2f}%")  # same hover format as wages plot


    # line at y=2 to match Fed's goal of 2% interest
    inf_fig.add_hline(y=2.0, line_dash="dot", line_color="green",
                      annotation_text="Fed Target (2%)", annotation_position='bottom right')

    st.plotly_chart(inf_fig, use_container_width=True)

# LABOR TAB

with tab_labor:
    st.header("The Beveridge Curve")
    bev_data = data.dropna(subset=['Jobs', 'Unemployment Rate'])
    bev_fig = px.scatter(bev_data, x='Unemployment Rate', y='Jobs',
                         color=bev_data.index.year,
                         color_continuous_scale='sunset')

    bev_fig.update_layout(
        margin={"r": 0, "t": 0, "l": 0, "b": 0},  # removes white padding around plot to show text below
        height=400,
    )

    st.plotly_chart(bev_fig, use_container_width=True)

    st.write('### Understanding the Beveridge Curve')
    st.write(
        'The curve typically slopes downward: The vacancy rate decreases as the unemployment rate increases. Location on the curve itself indicates the health of the labor market; a low unemployment rate and a high vacancy rate indicate a “tight” labor market and a growing economy. An economy shifting from recession to expansion and vice versa represents movements along the Beveridge curve. In contrast, changes in the efficiency of the job matching process correspond to shifts in the entire curve. ')
    st.write(
        'From the Federal Reserve Bank of St. Louis. (https://www.stlouisfed.org/on-the-economy/2022/jul/beveridge-curve-labor-market-recovery)')

# STATES TAB

with tab_map:
    st.header("State Job Growth")

    current = state_df['Date'].max()
    past = current - pd.DateOffset(years=1)

    # get current, past, then calculate percent growth
    current_states = state_df[state_df['Date'] == current].set_index('State')
    past_states = state_df[state_df['Date'] == past].set_index('State')
    current_states['Job Growth %'] = ((current_states['Jobs'] - past_states['Jobs']) / past_states['Jobs']) * 100

    # calculations for best and worst states
    growth_df = current_states['Job Growth %'].reset_index()
    top_5 = growth_df.nlargest(5, 'Job Growth %')
    bot_5 = growth_df.nsmallest(5, 'Job Growth %').sort_values('Job Growth %')

    col_map, col_high, col_low = st.columns([6, 1, 1])  # map, top5, bot 5

    with col_map:
        map_fig = px.choropleth(
            growth_df,
            locations='State',
            locationmode="USA-states",
            color='Job Growth %',
            scope="usa",
            color_continuous_scale="RdYlGn",  # red to green scale
            range_color=[-3, 3],
            title=f"Total Job Growth by State ({past.strftime('%B %Y')} - {current.strftime('%B %Y')})"
            # updating title to match data
        )

        map_fig.update_layout(
            margin={"r": 0, "t": 50, "l": 0, "b": 0},  # removes white padding around map to make it look bigger
            height=450,
        )
        st.plotly_chart(map_fig, use_container_width=True)

    st.markdown(  # changes the font size of the metrics using CSS
        """
    <style>
    [data-testid="stMetricValue"] {
        font-size: 25px;
    }
    </style>
    """,
        unsafe_allow_html=True,
    )

    with col_high:
        st.write("### :green[Top 5]")

        for i, row in top_5.iterrows():
            st.metric(row['State'], f"{row['Job Growth %']:.2f}%")

    with col_low:
        st.write("### :red[Bottom 5]")
        for i, row in bot_5.iterrows():
            st.metric(row['State'], f"{row['Job Growth %']:.2f}%")
