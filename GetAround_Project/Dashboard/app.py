import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px 
import plotly.graph_objects as go
import openpyxl

# Page settings
st.set_page_config(
    page_title="GetAround",
    layout="wide",
    initial_sidebar_state='auto'
)

# Data import
@st.cache_data
def load_data():
    data = pd.read_excel('get_around_delay_analysis.xlsx')
    return data


# Storing data in a variable
data = load_data()
st.session_state["data"] = data


# Title
st.markdown("<h1 style='text-align: center; margin-bottom: 100px;'><span style='font-size: 80px;'>GetAround Analysis Dashboard</h1>", unsafe_allow_html=True)

st.subheader("Lateness at checkout problematic visualization")
st.markdown("<div style='margin-left: 30px;'></div>", unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1 : 

    #Figure #1
    data_filtred = data[data['time_delta_with_previous_rental_in_minutes'].notna() & data['delay_at_checkout_in_minutes'].notna()]
    total_rows = len(data_filtred[data_filtred['delay_at_checkout_in_minutes'] <= 0])
    delay_gt_0 = len(data_filtred[data_filtred['delay_at_checkout_in_minutes'] > 0])
    delay_gt_previous = len(data_filtred[data_filtred['delay_at_checkout_in_minutes'] > data_filtred['time_delta_with_previous_rental_in_minutes']])
    percentage_gt_0 = (delay_gt_0 / total_rows) * 100
    percentage_gt_previous = (delay_gt_previous / total_rows) * 100

    colors = ['#317AC1', '#eb2f2f', '#77021d']
    labels = ['Rentals without delay or in advance at checkout', 'Rentals with delay at checkout', 'Rentals with delay at checkout preventing the next rental from being done on time']
    values = [total_rows, delay_gt_0, delay_gt_previous]

    fig = go.Figure(data=[go.Pie(labels=labels, values=values)])

    fig.update_traces(marker=dict(colors=colors))

    fig.update_layout(title='Percentage of checkout delays',
                    showlegend=True)

    st.plotly_chart(fig, use_container_width=True)

with col2 : 

#Figure #2
    ended_rentals = data[data['state'] == 'ended']
    canceled_rentals = data[data['state'] == 'canceled']

    colors = ['#317AC1', '#eb2f2f']
    labels = ['Ended rentals', 'Canceled rentals']
    values = [len(ended_rentals), len(canceled_rentals)]

    fig = go.Figure(data=[go.Pie(labels=labels, values=values)])

    fig.update_traces(marker=dict(colors=colors))

    fig.update_layout(title='Percentage of canceled rentals',
                    showlegend=True)

    st.plotly_chart(fig, use_container_width=True)


#Figure #3
data_hist = data.loc[(data['delay_at_checkout_in_minutes'] > 0) & (data['delay_at_checkout_in_minutes'] < 720)]
fig = px.histogram(data_hist['delay_at_checkout_in_minutes'], nbins=50, histnorm='percent', color_discrete_sequence=['#317AC1'])
fig.update_layout(
    xaxis_title='Minutes late at checkout',
    yaxis_title='Percentage of all delays',
    title='Distribution of delays according to their duration in minutes')
fig.update_xaxes(
    dtick=20)
fig.update_traces(
    name='Delay at checkout in minutes')
fig.update_traces(
    hovertemplate='Delay at checkout in minutes: %{x}<br>Percentage of all delays: %{y:.2f}%<extra></extra>'
)
st.plotly_chart(fig, use_container_width=True)

st.subheader("Potential effects of adding a minimum delay between two locations")
st.markdown("<div style='margin-left: 30px;'></div>", unsafe_allow_html=True)

col1, col2 = st.columns(2)
col1_width = 350
col2_width = 350

with col1 : 

    #Figure #4
    minimal_delay_between_rentals_in_minutes = [5, 15, 30, 60, 90, 120]
    categories = ['connect', 'mobile', 'all']

    bar_width = 2
    opacity = 0.8

    prct_connect = []
    prct_mobile = []
    prct_total = []

    for delay in minimal_delay_between_rentals_in_minutes:
        count_connect = len(data[(data['checkin_type'] == 'connect') & (data['time_delta_with_previous_rental_in_minutes'] < delay)])
        count_mobile = len(data[(data['checkin_type'] == 'mobile') & (data['time_delta_with_previous_rental_in_minutes'] < delay)])
        count_total = len(data[data['time_delta_with_previous_rental_in_minutes'] < delay])
        
        total_connect = len(data[data['checkin_type'] == 'connect'])
        total_mobile = len(data[data['checkin_type'] == 'mobile'])
        total = data['time_delta_with_previous_rental_in_minutes'].notna().sum()
        
        percentage_connect = (count_connect / total) * 100
        percentage_mobile = (count_mobile / total) * 100
        percentage_total = (count_total / total) * 100

        prct_connect.append(percentage_connect)
        prct_mobile.append(percentage_mobile)
        prct_total.append(percentage_total)

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=minimal_delay_between_rentals_in_minutes,
        y=prct_connect,
        name='connect',
        marker_color='#FD9089',
        hovertemplate='Percentage: %{y:.2f}%<extra></extra>'
    ))

    fig.add_trace(go.Bar(
        x=minimal_delay_between_rentals_in_minutes,
        y=prct_mobile,
        name='mobile',
        marker_color='#FE4B4B',
        hovertemplate='Percentage: %{y:.2f}%<extra></extra>'
    ))

    fig.add_trace(go.Bar(
        x=minimal_delay_between_rentals_in_minutes,
        y=prct_total,
        name='total',
        marker_color='#77021D',
        hovertemplate='Percentage: %{y:.2f}%<extra></extra>'
    ))

    fig.update_layout(
        barmode='group',
        xaxis_title='Minimal delay added between two rentals in minutes',
        yaxis_title='Percentage of rentals affected',
        title='Percentage of rentals affected by the add of a minimal delay between two rentals',
        xaxis=dict(
            tickmode='array',
            tickvals=minimal_delay_between_rentals_in_minutes),
        legend=dict(
            title="Checkin method",
            title_font=dict(size=14))
    )

    st.plotly_chart(fig, use_container_width=False)

with col2 :

    #Figure #5
    data_filtred = data.loc[data['delay_at_checkout_in_minutes'] > data['time_delta_with_previous_rental_in_minutes'],:]
    additional_delay_between_rentals_in_minutes = [5, 15, 30, 60, 90, 120]
    categories = ['connect', 'mobile', 'all']

    bar_width = 2
    opacity = 0.8

    prct_connect = []
    prct_mobile = []
    prct_total = []

    for delay in additional_delay_between_rentals_in_minutes:
        count_connect = len(data_filtred[(data_filtred['checkin_type'] == 'connect') & (data_filtred['delay_at_checkout_in_minutes'] <= data_filtred['time_delta_with_previous_rental_in_minutes'] + delay)])
        count_mobile = len(data_filtred[(data_filtred['checkin_type'] == 'mobile') & (data_filtred['delay_at_checkout_in_minutes'] <= data_filtred['time_delta_with_previous_rental_in_minutes'] + delay)])
        count_total = len(data_filtred.loc[data_filtred['delay_at_checkout_in_minutes'] <= data_filtred['time_delta_with_previous_rental_in_minutes'] + delay])

        total_problematic_rentals = len(data_filtred)
        
        percentage_connect = (count_connect / total_problematic_rentals) * 100
        percentage_mobile = (count_mobile / total_problematic_rentals) * 100
        percentage_total = (count_total / total_problematic_rentals) * 100

        prct_connect.append(percentage_connect)
        prct_mobile.append(percentage_mobile)
        prct_total.append(percentage_total)

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=minimal_delay_between_rentals_in_minutes,
        y=prct_connect,
        name='connect',
        marker_color='#9FCDA8',
        hovertemplate='Percentage: %{y:.2f}%<extra></extra>'
    ))

    fig.add_trace(go.Bar(
        x=minimal_delay_between_rentals_in_minutes,
        y=prct_mobile,
        name='mobile',
        marker_color='#24D26D',
        hovertemplate='Percentage: %{y:.2f}%<extra></extra>'
    ))

    fig.add_trace(go.Bar(
        x=minimal_delay_between_rentals_in_minutes,
        y=prct_total,
        name='total',
        marker_color='#003E1C',
        hovertemplate='Percentage: %{y:.2f}%<extra></extra>'
    ))

    fig.update_layout(
        barmode='group',
        xaxis_title='Minimum delay added between two rentals in minutes',
        yaxis_title='Percentage of problematic rentals avoided',
        title='Percentage of problematic rentals avoided with the add of a minimum delay between two rentals',
        xaxis=dict(
            tickmode='array',
            tickvals=minimal_delay_between_rentals_in_minutes),
        legend=dict(
            title="Checkin method",
            title_font=dict(size=14))
    )

    st.plotly_chart(fig, use_container_width=False)

col1._lock.width = col1_width
col2._lock.width = col2_width

#Figure #6
additional_delay_between_rentals_in_minutes = [5, 15, 30, 60, 90, 120]
categories = ['connect', 'mobile', 'all']
data_filtred_pbtics = data.loc[data['delay_at_checkout_in_minutes'] > data['time_delta_with_previous_rental_in_minutes'],:]

bar_width = 2
opacity = 0.8

prct_connect_avoided = []
prct_mobile_avoided = []
prct_total_avoided = []
prct_connect_affected = []
prct_mobile_affected = []
prct_total_affected = []

for delay in minimal_delay_between_rentals_in_minutes:
    count_connect_avoided = len(data_filtred_pbtics[(data_filtred_pbtics['checkin_type'] == 'connect') & (data_filtred_pbtics['delay_at_checkout_in_minutes'] <= data_filtred['time_delta_with_previous_rental_in_minutes'] + delay)])
    count_mobile_avoided = len(data_filtred_pbtics[(data_filtred_pbtics['checkin_type'] == 'mobile') & (data_filtred_pbtics['delay_at_checkout_in_minutes'] <= data_filtred['time_delta_with_previous_rental_in_minutes'] + delay)])
    count_total_avoided = len(data_filtred_pbtics.loc[data_filtred_pbtics['delay_at_checkout_in_minutes'] <= data_filtred_pbtics['time_delta_with_previous_rental_in_minutes'] + delay])
    count_connect_affected = len(data[(data['checkin_type'] == 'connect') & (data['time_delta_with_previous_rental_in_minutes'] < delay)])
    count_mobile_affected = len(data[(data['checkin_type'] == 'mobile') & (data['time_delta_with_previous_rental_in_minutes'] < delay)])
    count_total_affected = len(data[data['time_delta_with_previous_rental_in_minutes'] < delay])

    total_problematic_rentals = len(data_filtred_pbtics)
    total_connect = len(data[data['checkin_type'] == 'connect'])
    total_mobile = len(data[data['checkin_type'] == 'mobile'])
    total = data['time_delta_with_previous_rental_in_minutes'].notna().sum()
    
    percentage_connect_avoided = (count_connect_avoided / total_problematic_rentals) * 100
    percentage_mobile_avoided = (count_mobile_avoided / total_problematic_rentals) * 100
    percentage_total_avoided = (count_total_avoided / total_problematic_rentals) * 100
    percentage_connect_affected = (count_connect_affected / total) * 100
    percentage_mobile_affected = (count_mobile_affected / total) * 100
    percentage_total_affected = (count_total_affected / total) * 100

    prct_connect_avoided.append(percentage_connect_avoided)
    prct_mobile_avoided.append(percentage_mobile_avoided)
    prct_total_avoided.append(percentage_total_avoided)
    prct_connect_affected.append(percentage_connect_affected)
    prct_mobile_affected.append(percentage_mobile_affected)
    prct_total_affected.append(percentage_total_affected)
    
    fig = go.Figure()

fig.add_trace(go.Scatter(
    x=minimal_delay_between_rentals_in_minutes,
    y=prct_connect_avoided,
    name='Problematic rentals avoided (connect)/Problematic rentals',
    mode='lines',
    line=dict(color='#9FCDA8'),
    hovertemplate='Percentage: %{y:.2f}%<extra></extra>'
))

fig.add_trace(go.Scatter(
    x=minimal_delay_between_rentals_in_minutes,
    y=prct_mobile_avoided,
    name='Problematic rentals avoided (mobile)/Problematic rentals',
    mode='lines',
    line=dict(color='#24D26D'),
    hovertemplate='Percentage: %{y:.2f}%<extra></extra>'
))

fig.add_trace(go.Scatter(
    x=minimal_delay_between_rentals_in_minutes,
    y=prct_total_avoided,
    name='Problematic rentals avoided (total)/Problematic rentals',
    mode='lines',
    line=dict(color='#003E1C'),
    hovertemplate='Percentage: %{y:.2f}%<extra></extra>'
))

fig.add_trace(go.Scatter(
    x=minimal_delay_between_rentals_in_minutes,
    y=prct_connect_affected,
    name='Rentals affected (connect)/All rentals',
    mode='lines',
    line=dict(color='#FD9089'),
    hovertemplate='Percentage: %{y:.2f}%<extra></extra>'
))

fig.add_trace(go.Scatter(
    x=minimal_delay_between_rentals_in_minutes,
    y=prct_mobile_affected,
    name='Rentals affected (mobile)/All rentals',
    mode='lines',
    line=dict(color='#FE4B4B'),
    hovertemplate='Percentage: %{y:.2f}%<extra></extra>'
))

fig.add_trace(go.Scatter(
    x=minimal_delay_between_rentals_in_minutes,
    y=prct_total_affected,
    name='Rentals affected (total)/All rentals',
    mode='lines',
    line=dict(color='#77021D'),
    hovertemplate='Percentage: %{y:.2f}%<extra></extra>'
))

fig.update_layout(
    xaxis_title='Minimum delay added between two rentals in minutes',
    yaxis_title='Percentage',
    title='Summary of the positive and negative effects of adding a minimum delay between two rentals',
    xaxis=dict(
        tickmode='array',
        tickvals=minimal_delay_between_rentals_in_minutes,
        ticktext=minimal_delay_between_rentals_in_minutes
    ),
    legend=dict(
        title="Effects",
        title_font=dict(size=14))
)

fig_height = 500

st.plotly_chart(fig, use_container_width=True)

fig_style = f"display: block; margin: 0 auto; max-height: {fig_height}px;"