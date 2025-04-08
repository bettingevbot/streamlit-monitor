import streamlit as st
import pandas as pd
import psycopg2
from datetime import datetime, timedelta
import time

# Database configuration
DATABASE_CONFIG = {
    "dbname": "horse_aus",
    "user": "postgres",
    "password": "postgres",
    "host": "localhost",
    "port": "5432"
}

def get_db_connection():
    return psycopg2.connect(**DATABASE_CONFIG)

def get_latest_logs(minutes=60):
    """Get logs from the last hour from PostgreSQL"""
    try:
        conn = get_db_connection()
        query = """
        SELECT 
            timestamp,
            log_level,
            line_number,
            message
        FROM logs_horse_aus
        WHERE timestamp >= NOW() - INTERVAL '%s minutes'
        ORDER BY timestamp DESC
        """
        df = pd.read_sql_query(query, conn, params=(minutes,))
        conn.close()
        return df
    except Exception as e:
        st.error(f"Database error: {str(e)}")
        return pd.DataFrame()

def main():
    st.title("Horse Racing Bot Monitor")

    # Add a time filter
    time_filter = st.sidebar.selectbox(
        "Show logs from last:",
        ["15 minutes", "30 minutes", "1 hour", "2 hours", "4 hours", "8 hours", "24 hours"]
    )
    
    time_minutes = {
        "15 minutes": 15,
        "30 minutes": 30,
        "1 hour": 60,
        "2 hours": 120,
        "4 hours": 240,
        "8 hours": 480,
        "24 hours": 1440
    }[time_filter]

    # Create placeholder for the logs
    logs_placeholder = st.empty()

    # Auto-refresh checkbox
    auto_refresh = st.sidebar.checkbox("Auto-refresh", value=True)
    refresh_interval = st.sidebar.number_input("Refresh interval (seconds)", min_value=1, value=5)

    while True:
        # Get latest logs from database
        df = get_latest_logs(time_minutes)

        if not df.empty:
            # Display the logs in the placeholder
            with logs_placeholder.container():
                st.dataframe(
                    df,
                    column_config={
                        "timestamp": "Time",
                        "log_level": "Level",
                        "line_number": "Line",
                        "message": "Message"
                    },
                    hide_index=True,
                    use_container_width=True
                )

        if not auto_refresh:
            break
            
        time.sleep(refresh_interval)
        st.rerun()

if __name__ == "__main__":
    main()
