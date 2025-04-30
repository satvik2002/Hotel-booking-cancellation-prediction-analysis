import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import warnings

warnings.filterwarnings('ignore')

st.set_page_config(layout="wide")
st.title("🏨 Hotel Booking Analysis Dashboard")

# Load dataset
@st.cache_data
def load_data():
    df = pd.read_csv("HotelData - Final.csv")
    df.fillna(0, inplace=True)
    df['arrival_date'] = pd.to_datetime(df['arrival_date'])
    df['month'] = df['arrival_date'].dt.month_name()
    df['weekday'] = df['arrival_date'].dt.day_name()
    df['stay_duration'] = df['stays_in_weekend_nights'] + df['stays_in_week_nights']
    df['revenue'] = df['adr'] * df['stay_duration']
    return df

df = load_data()
non_canceled = df[df['is_canceled'] == 0]

# KPIs
st.subheader("📊 Key Performance Indicators (KPIs)")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Bookings", df.shape[0])
col2.metric("Total Cancellations", df[df['is_canceled'] == 1].shape[0])
col3.metric("Cancellation Rate (%)", round((df['is_canceled'] == 1).sum() / df.shape[0] * 100, 2))
col4.metric("Average Lead Time", round(non_canceled['lead_time'].mean(), 2))

col5, col6, col7, col8 = st.columns(4)
col5.metric("Avg. Stay Duration", round(non_canceled['stay_duration'].mean(), 2))
col6.metric("Total Guests", int((non_canceled['adults'] + non_canceled['children'] + non_canceled['babies']).sum()))
col7.metric("Repeat Guest Rate (%)", round((non_canceled['is_repeated_guest'] == 1).sum() / len(non_canceled) * 100, 2))
col8.metric("Room Mismatch Rate (%)", round((non_canceled['reserved_room_type'] != non_canceled['assigned_room_type']).sum() / len(non_canceled) * 100, 2))

# Revenue Calculations
total_revenue = round(non_canceled['revenue'].sum(), 2)
revenue_per_booking = round(total_revenue / len(non_canceled), 2)
st.metric("💰 Total Revenue", f"${total_revenue:,.2f}")
st.metric("💳 Revenue Per Booking", f"${revenue_per_booking:,.2f}")

# --- Visualizations ---
st.subheader("📉 Booking Trends")

# Bookings & Cancellations by Hotel
st.markdown("#### Bookings & Cancellations by Hotel")
hotel_data = df.groupby('hotel')['is_canceled'].value_counts().unstack().fillna(0)
hotel_data.columns = ['Confirmed Bookings', 'Total Cancellations']
hotel_data = hotel_data[['Total Cancellations', 'Confirmed Bookings']]

fig1, ax1 = plt.subplots()
hotel_data.plot(kind='bar', stacked=False, ax=ax1, color=['#d9534f', '#f7b7a3'])
ax1.set_title('Bookings & Cancellations by Hotel')
ax1.set_ylabel('Bookings Count')
st.pyplot(fig1)

# Monthly Bookings & Cancellations
st.markdown("#### Monthly Bookings & Cancellations")
month_order = ['January', 'February', 'March', 'April', 'May', 'June',
               'July', 'August', 'September', 'October', 'November', 'December']
monthly_data = df.groupby(['month', 'is_canceled']).size().unstack().reindex(month_order)
monthly_data.columns = ['Confirmed Bookings', 'Total Cancellations']

fig2, ax2 = plt.subplots()
ax2.plot(monthly_data.index, monthly_data['Confirmed Bookings'], marker='o', label='Confirmed Bookings', color='#f7b7a3')
ax2.plot(monthly_data.index, monthly_data['Total Cancellations'], marker='o', label='Total Cancellations', color='#d9534f')
ax2.set_title('Bookings & Cancellations by Month')
ax2.legend()
st.pyplot(fig2)

# Cancellations by Weekday
st.markdown("#### Cancellations by Weekday")
cancel_by_weekday = df[df['is_canceled'] == 1].groupby('weekday').size()
weekday_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
cancel_by_weekday = cancel_by_weekday.reindex(weekday_order[::-1])

fig3, ax3 = plt.subplots()
cancel_by_weekday.plot(kind='barh', ax=ax3, color='#d9534f')
ax3.set_title('Cancellations by Weekday')
st.pyplot(fig3)

# ADR by Hotel
st.markdown("#### Average Daily Rate by Hotel")
adr_by_hotel = df[df['is_canceled'] == 0].groupby('hotel')['adr'].mean()

fig4, ax4 = plt.subplots()
adr_by_hotel.plot(kind='bar', ax=ax4, color='#d9534f')
for i, val in enumerate(adr_by_hotel):
    ax4.text(i, val + 1, f"{val:.0f}", ha='center')
ax4.set_title('ADR by Hotel')
st.pyplot(fig4)

# Stay Duration by Customer Type
st.markdown("#### Avg. Stay Duration by Customer Type")
stay_by_customer = non_canceled.groupby('customer_type')['stay_duration'].mean().sort_values(ascending=False)

fig5, ax5 = plt.subplots()
stay_by_customer.plot(kind='line', marker='o', ax=ax5, color='#d9534f')
ax5.fill_between(stay_by_customer.index, stay_by_customer.values, color='#d9534f', alpha=0.2)
ax5.set_ylabel('Avg Stay Duration')
st.pyplot(fig5)

# Repeat Guest % by Month
st.markdown("#### Repeat Guest % by Month")
df['arrival_date_month'] = pd.Categorical(df['month'], categories=month_order, ordered=True)
repeat_month = df[df['is_canceled'] == 0].groupby('arrival_date_month').apply(
    lambda x: (x['is_repeated_guest'].sum() / len(x)) * 100
)

fig6, ax6 = plt.subplots()
repeat_month.plot(marker='o', ax=ax6, color='#d9534f')
for i, val in enumerate(repeat_month):
    ax6.text(i, val + 0.3, f"{val:.2f}%", ha='center')
ax6.set_title('Repeat Guest % by Month')
st.pyplot(fig6)

# Revenue by Market Segment
st.subheader("💼 Revenue Insights")

segment_revenue = non_canceled.groupby('market_segment')['revenue'].sum().sort_values(ascending=False)

fig7, ax7 = plt.subplots()
segment_revenue.plot(kind='bar', ax=ax7, color='#d9534f')
ax7.set_title('Revenue by Market Segment')
st.pyplot(fig7)

# Revenue by Country
country_revenue = non_canceled.groupby('country')['revenue'].sum().sort_values(ascending=False).head(10)

fig8, ax8 = plt.subplots()
ax8.plot(country_revenue.index, country_revenue.values, marker='o', color='#d9534f')
ax8.fill_between(country_revenue.index, country_revenue.values, color='#d9534f', alpha=0.2)
ax8.set_title('Top 10 Countries by Revenue')
st.pyplot(fig8)

# Monthly Revenue
monthly_revenue = non_canceled.groupby('month')['revenue'].sum().reindex(month_order)

fig9, ax9 = plt.subplots()
ax9.plot(monthly_revenue.index, monthly_revenue.values, marker='o', color='#d9534f')
ax9.set_title('Monthly Revenue Trend')
st.pyplot(fig9)

st.success("Dashboard Ready! ✅")

