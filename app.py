import streamlit as st
import pandas as pd
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt

st.set_page_config(page_title="Hotel Booking Dashboard", layout="wide")
st.title("🏨 Hotel Booking Analysis Dashboard")

# Load dataset
@st.cache_data
def load_data():
    return pd.read_csv("HotelData - Final.csv")

df = load_data()

# Sidebar filters
st.sidebar.header("🔍 Filter the Data")
years = df['arrival_date_year'].unique()
selected_year = st.sidebar.selectbox("Select Year", sorted(years, reverse=True))
filtered_df = df[df['arrival_date_year'] == selected_year]

# KPIs
st.subheader("📊 Key Performance Indicators (KPIs)")
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Bookings", len(filtered_df))
with col2:
    st.metric("Cancel Rate", f"{filtered_df['is_canceled'].mean() * 100:.2f}%")
with col3:
    st.metric("Avg Lead Time", f"{filtered_df['lead_time'].mean():.2f} days")
with col4:
    st.metric("Avg ADR", f"${filtered_df['adr'].mean():.2f}")

st.divider()

# Cancellations over time
st.subheader("📅 Monthly Booking Cancellations")
cancel_month = df.groupby(['arrival_date_month'])['is_canceled'].mean().reset_index()
fig1 = px.bar(cancel_month, x='arrival_date_month', y='is_canceled',
              labels={'is_canceled': 'Cancellation Rate'}, title='Monthly Cancellation Rate')
st.plotly_chart(fig1, use_container_width=True)

# Market segment analysis
st.subheader("🧳 Market Segment Analysis")
segment = df['market_segment'].value_counts().reset_index()
fig2 = px.pie(segment, names='index', values='market_segment', title='Bookings by Market Segment')
st.plotly_chart(fig2, use_container_width=True)

# Heatmap of correlation
st.subheader("📈 Correlation Heatmap")
numeric_cols = df.select_dtypes(include=['float64', 'int64'])
corr = numeric_cols.corr()
fig3, ax = plt.subplots(figsize=(12, 6))
sns.heatmap(corr, cmap="coolwarm", annot=True, fmt=".1f", ax=ax)
st.pyplot(fig3)

# Room type comparison
st.subheader("🛏 Reserved vs Assigned Room Types")
room_df = df[df['reserved_room_type'] != df['assigned_room_type']]
room_mismatch_rate = len(room_df) / len(df) * 100
st.write(f"Room mismatch rate: **{room_mismatch_rate:.2f}%**")
fig4 = px.histogram(room_df, x='reserved_room_type', color='assigned_room_type',
                    title="Mismatch between Reserved and Assigned Room Types")
st.plotly_chart(fig4, use_container_width=True)

st.markdown("---")
st.markdown("📌 Built with ❤️ using Streamlit | Deployed on Render")

