#!/bin/bash

# Start the scheduler process in the background
echo "Starting scheduler for daily updates..."
python scheduler.py &

# Wait a moment to ensure the first data collection starts
sleep 5

# Start the Streamlit app
echo "Starting Streamlit dashboard..."
streamlit run app.py


#chmod +x start_system.sh
#./start_system.sh