import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# Load Data
@st.cache_data
def load_data():
    df = pd.read_csv("HotelData - Final.csv")
    df.fillna(0, inplace=True)
    df['arrival_date'] = pd.to_datetime(df['arrival_date'], dayfirst=True, errors='coerce')
    df['stay_duration'] = df['stays_in_weekend_nights'] + df['stays_in_week_nights']
    df['revenue'] = df['adr'] * df['stay_duration']
    df['month'] = df['arrival_date'].dt.month_name()
    return df

df = load_data()
non_canceled = df[df['is_canceled'] == 0]

# Page Setup
st.title("Hotel Booking Analysis Dashboard")
st.markdown("This dashboard provides insights into hotel booking trends and performance KPIs.")

# KPIs
st.header("📊 Key Performance Indicators")

# KPI Set 1
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Bookings", df.shape[0])
with col2:
    st.metric("Total Cancellations", df[df['is_canceled'] == 1].shape[0])
with col3:
    st.metric("Cancellation Rate (%)", f"{round((df['is_canceled'].sum()/df.shape[0])*100, 2)}%")

# KPI Set 2
col4, col5, col6 = st.columns(3)
with col4:
    st.metric("Avg. Lead Time", round(non_canceled['lead_time'].mean(), 2))
with col5:
    st.metric("Avg. Stay Duration", round(non_canceled['stay_duration'].mean(), 2))
with col6:
    st.metric("Avg. ADR", round(non_canceled['adr'].mean(), 2))

# KPI Set 3
total_guests = (non_canceled['adults'] + non_canceled['children'] + non_canceled['babies']).sum()
col7, col8, col9 = st.columns(3)
with col7:
    st.metric("Total Guests", int(total_guests))
with col8:
    st.metric("Repeat Guest Rate (%)", f"{round((non_canceled['is_repeated_guest'].sum()/len(non_canceled))*100, 2)}%")
with col9:
    st.metric("Revenue", f"${round(non_canceled['revenue'].sum(), 2):,}")

# KPI Set 4
booking_change_rate = 100.0 * (non_canceled['booking_changes'] > 0).sum() / len(non_canceled)
mismatch_room_rate = 100.0 * (non_canceled['reserved_room_type'] != non_canceled['assigned_room_type']).sum() / len(non_canceled)
avg_waiting_days = round(non_canceled['days_in_waiting_list'].mean(), 2)

col10, col11, col12 = st.columns(3)
with col10:
    st.metric("Booking Change Rate (%)", f"{round(booking_change_rate, 2)}%")
with col11:
    st.metric("Room Type Mismatch Rate (%)", f"{round(mismatch_room_rate, 2)}%")
with col12:
    st.metric("Avg. Waiting Days", avg_waiting_days)

# Visualizations
st.header("📈 Visual Analysis")

# Bookings & Cancellations by Hotel
st.subheader("Bookings & Cancellations by Hotel")
hotel_data = df.groupby(['hotel', 'is_canceled']).size().reset_index(name='count')
hotel_data['Status'] = hotel_data['is_canceled'].map({0: 'Confirmed', 1: 'Canceled'})
fig1 = px.bar(hotel_data, x='hotel', y='count', color='Status', barmode='group',
              text='count', title='Bookings & Cancellations by Hotel')
fig1.update_traces(textposition='outside')
st.plotly_chart(fig1)

# Monthly Bookings and Cancellations
st.subheader("Monthly Bookings and Cancellations")
month_order = ['January', 'February', 'March', 'April', 'May', 'June',
               'July', 'August', 'September', 'October', 'November', 'December']
monthly_data = df.groupby([df['arrival_date'].dt.month_name(), 'is_canceled']).size().reset_index(name='count')
monthly_data.columns = ['month', 'is_canceled', 'count']
monthly_data['Status'] = monthly_data['is_canceled'].map({0: 'Confirmed', 1: 'Canceled'})
monthly_data['month'] = pd.Categorical(monthly_data['month'], categories=month_order, ordered=True)
fig2 = px.bar(monthly_data.sort_values('month'), x='month', y='count', color='Status', barmode='group',
              text='count', title='Monthly Bookings and Cancellations')
fig2.update_traces(textposition='outside')
st.plotly_chart(fig2)

# ADR by Hotel Type
st.subheader("ADR by Hotel Type")
adr_by_hotel = non_canceled.groupby('hotel')['adr'].mean().reset_index()
fig3 = px.bar(adr_by_hotel, x='hotel', y='adr', text='adr', title='ADR by Hotel Type')
fig3.update_traces(textposition='outside')
st.plotly_chart(fig3)

# Stay Duration by Customer Type
st.subheader("Avg. Stay Duration by Customer Type")
stay_by_customer = non_canceled.groupby('customer_type')['stay_duration'].mean().reset_index()
fig4 = px.line(stay_by_customer, x='customer_type', y='stay_duration', text='stay_duration', markers=True,
               title='Avg. Stay Duration by Customer Type')
fig4.update_traces(textposition='top center')
st.plotly_chart(fig4)

# Repeat Guest % by Month
st.subheader("Repeat Guest % by Month")
repeat_by_month = non_canceled.groupby('month')['is_repeated_guest'].mean() * 100
repeat_by_month = repeat_by_month.reindex(month_order).reset_index()
fig5 = px.line(repeat_by_month, x='month', y='is_repeated_guest', text='is_repeated_guest', markers=True,
               title='Repeat Guest % by Month')
fig5.update_traces(textposition='top center')
st.plotly_chart(fig5)

# Revenue by Market Segment
st.subheader("Revenue by Market Segment")
segment_revenue = non_canceled.groupby('market_segment')['revenue'].sum().sort_values(ascending=False).reset_index()
fig6 = px.bar(segment_revenue, x='market_segment', y='revenue', text='revenue', title='Revenue by Market Segment')
fig6.update_traces(texttemplate='%{text:.2s}', textposition='outside')
st.plotly_chart(fig6)

# Top Countries by Revenue
st.subheader("Top 10 Countries by Revenue")
country_revenue = non_canceled.groupby('country')['revenue'].sum().sort_values(ascending=False).head(10).reset_index()
fig7 = px.bar(country_revenue, x='country', y='revenue', text='revenue', title='Top 10 Countries by Revenue')
fig7.update_traces(textposition='outside')
st.plotly_chart(fig7)

# Monthly Revenue Trend
st.subheader("Monthly Revenue Trend")
monthly_revenue = non_canceled.groupby(df['arrival_date'].dt.month_name())['revenue'].sum().reindex(month_order).reset_index()
monthly_revenue.columns = ['month', 'revenue']
fig8 = px.line(monthly_revenue, x='month', y='revenue', text='revenue', markers=True, title='Monthly Revenue Trend')
fig8.update_traces(textposition='top center')
st.plotly_chart(fig8)

st.success("✅ Dashboard loaded successfully.")
