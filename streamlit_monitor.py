import streamlit as st
import time
import os
import glob

# Define the line numbers we want to see
ALLOWED_INFO_LINES = {105, 113, 131, 140, 988, 79, 995, 996, 978}

def check_security():
    """Check password authentication"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False

    if not st.session_state.authenticated:
        password = st.text_input("Enter password:", type="password")
        if password == st.secrets["password"]:
            st.session_state.authenticated = True
        else:
            if password:  # Only show error if they tried to enter a password
                st.error("Wrong password")
            st.stop()

def get_latest_log_file(directory="."):
    """Find the most recent log file in the specified directory"""
    try:
        files = glob.glob(os.path.join(directory, "bot_log_*.csv"))
        if not files:
            return None
        return max(files, key=os.path.getctime)
    except Exception as e:
        st.error(f"Error accessing log directory: {e}")
        return None

def load_data(file_path):
    try:
        filtered_lines = []
        with open(file_path, 'r') as file:
            for line in file:
                parts = line.strip().split(',')
                if len(parts) >= 4:
                    try:
                        line_number = int(parts[3])
                        if parts[2] == 'INFO' and line_number in ALLOWED_INFO_LINES:
                            filtered_lines.append(line)
                    except ValueError:
                        continue

        return ''.join(reversed(filtered_lines))
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None

def main():
    st.title("Live Log Monitor")
    
    # Check security first
    check_security()
    
    # Directory input
    log_dir = st.text_input("Log directory:", ".")

    # Auto-refresh checkbox and interval
    auto_refresh = st.checkbox("Auto-refresh", value=True)
    refresh_interval = st.number_input("Refresh interval (seconds)", min_value=1, value=5)

    # Get the latest log file
    latest_file = get_latest_log_file(log_dir)
    
    if latest_file is None:
        st.warning("No log files found")
        return

    # Display current file name
    st.subheader(f"Current log file: {os.path.basename(latest_file)}")
    
    # Load and display the data
    log_text = load_data(latest_file)
    if log_text is not None:
        st.text_area("Log Output", log_text, height=600)

    if auto_refresh:
        time.sleep(refresh_interval)
        st.rerun()

if __name__ == "__main__":
    main()
