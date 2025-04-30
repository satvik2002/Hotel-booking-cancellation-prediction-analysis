import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
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
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Total Bookings", df.shape[0])
    st.metric("Total Cancellations", df[df['is_canceled'] == 1].shape[0])
    st.metric("Cancellation Rate (%)", f"{round((df['is_canceled'].sum()/df.shape[0])*100, 2)}%")

with col2:
    st.metric("Avg. Lead Time", round(non_canceled['lead_time'].mean(), 2))
    st.metric("Avg. Stay Duration", round(non_canceled['stay_duration'].mean(), 2))
    st.metric("Avg. ADR", round(non_canceled['adr'].mean(), 2))

with col3:
    total_guests = (non_canceled['adults'] + non_canceled['children'] + non_canceled['babies']).sum()
    st.metric("Total Guests", int(total_guests))
    st.metric("Repeat Guest Rate (%)", f"{round((non_canceled['is_repeated_guest'].sum()/len(non_canceled))*100, 2)}%")
    st.metric("Revenue", f"${round(non_canceled['revenue'].sum(), 2):,}")

# Visualizations
st.header("📈 Visual Analysis")

# Bookings & Cancellations by Hotel
st.subheader("Bookings & Cancellations by Hotel")
hotel_data = df.groupby('hotel')['is_canceled'].value_counts().unstack().fillna(0)
hotel_data.columns = ['Confirmed', 'Canceled']
hotel_data = hotel_data[['Canceled', 'Confirmed']]
st.bar_chart(hotel_data)

# Monthly Bookings
st.subheader("Monthly Bookings and Cancellations")
month_order = ['January', 'February', 'March', 'April', 'May', 'June',
               'July', 'August', 'September', 'October', 'November', 'December']
monthly_data = df.groupby(['month', 'is_canceled']).size().unstack().reindex(month_order)
monthly_data.columns = ['Confirmed', 'Canceled']
st.line_chart(monthly_data)

# ADR by Hotel Type
st.subheader("ADR by Hotel Type")
adr_by_hotel = non_canceled.groupby('hotel')['adr'].mean()
st.bar_chart(adr_by_hotel)

# Stay Duration by Customer Type
st.subheader("Avg. Stay Duration by Customer Type")
stay_by_customer = non_canceled.groupby('customer_type')['stay_duration'].mean()
st.line_chart(stay_by_customer)

# Repeat Guest % by Month
st.subheader("Repeat Guest % by Month")
repeat_by_month = non_canceled.groupby('month')['is_repeated_guest'].mean() * 100
repeat_by_month = repeat_by_month.reindex(month_order)
st.line_chart(repeat_by_month)

# Revenue by Market Segment
st.subheader("Revenue by Market Segment")
segment_revenue = non_canceled.groupby('market_segment')['revenue'].sum().sort_values(ascending=False)
st.bar_chart(segment_revenue)

# Top Countries by Revenue
st.subheader("Top 10 Countries by Revenue")
country_revenue = non_canceled.groupby('country')['revenue'].sum().sort_values(ascending=False).head(10)
fig = px.bar(country_revenue, title='Top 10 Countries by Revenue', labels={'value': 'Revenue', 'country': 'Country'})
st.plotly_chart(fig)

# Monthly Revenue Trend
st.subheader("Monthly Revenue Trend")
monthly_revenue = non_canceled.groupby('month')['revenue'].sum().reindex(month_order)
st.line_chart(monthly_revenue)

st.success("✅ Dashboard loaded successfully.")

