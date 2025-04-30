import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# Authentication
users = {"admin": "admin123", "user": "pass"}

def login():
    st.title("🔐 Hotel Dashboard Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if users.get(username) == password:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.rerun()
        else:
            st.error("Invalid username or password")

# Load Data
@st.cache_data

def load_data():
    df = pd.read_csv("HotelData - Final.csv")
    df.fillna(0, inplace=True)
    df['arrival_date'] = pd.to_datetime(df['arrival_date'], dayfirst=True, errors='coerce')
    df['stay_duration'] = df['stays_in_weekend_nights'] + df['stays_in_week_nights']
    df['revenue'] = df['adr'] * df['stay_duration']
    df['month'] = df['arrival_date'].dt.month_name()
    df['year'] = df['arrival_date'].dt.year
    df['weekday'] = df['arrival_date'].dt.day_name()
    return df

def main():
    df = load_data()
    month_order = ['January', 'February', 'March', 'April', 'May', 'June',
                   'July', 'August', 'September', 'October', 'November', 'December']

    # Page Navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["KPIs", "Cancellation Analysis", "Behavior Analysis", "Revenue Analysis"])
    
    # Sidebar Filters
    st.sidebar.header("🔍 Filters")
    selected_years = st.sidebar.multiselect("Select Year", sorted(df['year'].unique()), default=sorted(df['year'].unique()))
    selected_customer_types = st.sidebar.multiselect("Select Customer Type", df['customer_type'].unique(), default=list(df['customer_type'].unique()))
    selected_segments = st.sidebar.multiselect("Select Market Segment", df['market_segment'].unique(), default=list(df['market_segment'].unique()))

    # Filter data
    df = df[df['year'].isin(selected_years)]
    df = df[df['customer_type'].isin(selected_customer_types)]
    df = df[df['market_segment'].isin(selected_segments)]
    non_canceled = df[df['is_canceled'] == 0]


    if page == "KPIs":
        st.title("Hotel Booking Analysis Dashboard")
        st.header("📊 Key Performance Indicators")

        kpi_sets = [
            [("Total Bookings", df.shape[0]),
             ("Total Cancellations", df[df['is_canceled'] == 1].shape[0]),
             ("Cancellation Rate (%)", f"{round((df['is_canceled'].sum()/df.shape[0])*100, 2)}%")],
            [("Avg. Lead Time", round(non_canceled['lead_time'].mean(), 2)),
             ("Avg. Stay Duration", round(non_canceled['stay_duration'].mean(), 2)),
             ("Avg. ADR", round(non_canceled['adr'].mean(), 2))],
            [("Total Guests", int((non_canceled['adults'] + non_canceled['children'] + non_canceled['babies']).sum())),
             ("Repeat Guest Rate (%)", f"{round((non_canceled['is_repeated_guest'].sum()/len(non_canceled))*100, 2)}%"),
             ("Revenue", f"€{round(non_canceled['revenue'].sum(), 2):,}")],
            [("Booking Change Rate (%)", f"{round((non_canceled['booking_changes'] > 0).sum() / len(non_canceled) * 100, 2)}%"),
             ("Room Type Mismatch Rate (%)", f"{round((non_canceled['reserved_room_type'] != non_canceled['assigned_room_type']).sum() / len(non_canceled) * 100, 2)}%"),
             ("Avg. Waiting Days", round(non_canceled['days_in_waiting_list'].mean(), 2))]
        ]

        for kpis in kpi_sets:
            col1, col2, col3 = st.columns(3)
            for i, (label, value) in enumerate(kpis):
                with [col1, col2, col3][i]:
                    st.metric(label, value)

    elif page == "Cancellation Analysis":
        st.header("📉 Cancellation Analysis")
        st.subheader("Bookings & Cancellations by Hotel")
        
        # Data preparation
        hotel_data = df.groupby('hotel')['is_canceled'].value_counts().unstack().fillna(0)
        hotel_data.columns = ['Confirmed', 'Canceled']
        hotel_data = hotel_data[['Canceled', 'Confirmed']].reset_index()
        
        # Melt for plotting
        hotel_data_melted = hotel_data.melt(id_vars='hotel', var_name='Status', value_name='Count')
        
        # Add formatted label with 'k'
        hotel_data_melted['Label'] = (hotel_data_melted['Count'] / 1000).round(1).astype(str) + 'k'
        
        # Plotly bar chart
        fig0 = px.bar(
            hotel_data_melted,
            x='hotel',
            y='Count',
            color='Status',
            barmode='group',
            text='Label',
            title='Bookings & Cancellations by Hotel'
        )
        fig0.update_traces(textposition='outside')
        st.plotly_chart(fig0)

        st.subheader("Monthly Bookings and Cancellations")
        monthly_data = df.groupby(['month', 'is_canceled']).size().unstack().reindex(month_order)
        monthly_data.columns = ['Confirmed', 'Canceled']
        monthly_data = monthly_data.reset_index().rename(columns={'month': 'Month'})
        figm = px.bar(monthly_data, x='Month', y=['Canceled', 'Confirmed'], barmode='group',
                      title='Monthly Bookings and Cancellations', text_auto=True)
        st.plotly_chart(figm)

        st.subheader("Cancellations by Weekday")
        cancel_by_weekday = df[df['is_canceled'] == 1].groupby('weekday').size()
        weekday_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        cancel_by_weekday = cancel_by_weekday.reindex(weekday_order[::-1]).reset_index()
        cancel_by_weekday.columns = ['Weekday', 'Count']
        fig7 = px.bar(cancel_by_weekday, x='Count', y='Weekday', orientation='h', text='Count',
                      title='Cancellations by Weekday')
        fig7.update_traces(textposition='outside')        
        st.plotly_chart(fig7)

    elif page == "Behavior Analysis":
        st.header("📋 Behavior Analysis")

        st.subheader("ADR by Hotel Type")
        adr_by_hotel = non_canceled.groupby('hotel')['adr'].mean().round(2).reset_index()
        fig1 = px.bar(adr_by_hotel, x='hotel', y='adr', text='adr', title='ADR by Hotel Type')
        st.plotly_chart(fig1)

        st.subheader("Avg. Stay Duration by Customer Type")
        stay_by_customer = non_canceled.groupby('customer_type')['stay_duration'].mean().round(2).reset_index()
        fig2 = px.bar(stay_by_customer, x='customer_type', y='stay_duration', text='stay_duration',
                      title='Avg. Stay Duration by Customer Type')
        st.plotly_chart(fig2)

        st.subheader("Repeat Guest % by Month")
        repeat_by_month = non_canceled.groupby('month')['is_repeated_guest'].mean() * 100
        repeat_by_month = repeat_by_month.reindex(month_order).round(2).reset_index()
        fig3 = px.bar(repeat_by_month, x='month', y='is_repeated_guest', text='is_repeated_guest',
                      title='Repeat Guest % by Month', labels={'is_repeated_guest': 'Repeat Guest %'})
        fig3.update_traces(textposition='outside')
        st.plotly_chart(fig3)

    elif page == "Revenue Analysis":
        st.header("💰 Revenue Analysis")

        st.subheader("Revenue by Market Segment")
        segment_revenue = non_canceled.groupby('market_segment')['revenue'].sum().sort_values(ascending=False) / 1_000_000
        segment_revenue = segment_revenue.round(2).reset_index()
        fig4 = px.bar(segment_revenue, x='market_segment', y='revenue', text='revenue',
                      title='Revenue by Market Segment (in Millions)')
        fig4.update_traces(textposition='outside')
        st.plotly_chart(fig4)

        st.subheader("Top 10 Countries by Revenue")
        country_revenue = non_canceled.groupby('country')['revenue'].sum().sort_values(ascending=False).head(10) / 1_000_000
        country_revenue = country_revenue.round(2).reset_index()
        fig5 = px.bar(country_revenue, x='country', y='revenue', text='revenue',
                      title='Top 10 Countries by Revenue (in Millions)')
        fig5.update_traces(textposition='outside')
        st.plotly_chart(fig5)

        st.subheader("Monthly Revenue Trend")
        monthly_revenue = non_canceled.groupby('month')['revenue'].sum().reindex(month_order) / 1_000_000
        monthly_revenue = monthly_revenue.round(2).reset_index()
        fig6 = px.line(monthly_revenue, x='month', y='revenue', text='revenue',
                       title='Monthly Revenue Trend (in Millions)')
        fig6.update_traces(textposition='outside')
        st.plotly_chart(fig6)

    # Logout Button
    if st.sidebar.button("🚪 Logout"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.experimental_rerun()

# Run App
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    login()
else:
    main()
