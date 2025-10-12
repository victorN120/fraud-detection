import streamlit as st
import pandas as pd
import json
from kafka import KafkaConsumer
import time

# UI setup
st.set_page_config(layout="wide")
st.title("📊 Real-Time Fraud Detection Dashboard")
st.markdown("### 🔄 Live Transaction Stream")

# Initialize session state for persistent data
if 'data' not in st.session_state:
    st.session_state.data = []
    st.session_state.fraud_count = 0
    st.session_state.normal_count = 0
    st.session_state.unknown_count = 0
    st.session_state.error_log = []

# Kafka connection with error handling
@st.cache_resource
def get_kafka_consumer():
    try:
        consumer = KafkaConsumer(
            'transactions',
            bootstrap_servers='localhost:9092',
            auto_offset_reset='latest',
            enable_auto_commit=True,
            group_id='dashboard-group',
            value_deserializer=lambda x: json.loads(x.decode('utf-8')),
            consumer_timeout_ms=1000  # 1 second timeout
        )
        return consumer
    except Exception as e:
        st.error(f"❌ Kafka Connection Error: {str(e)}")
        st.info("Make sure Kafka is running on localhost:9092")
        return None

# Get consumer
consumer = get_kafka_consumer()

# Create placeholders
metric_cols = st.columns(3)
table_placeholder = st.empty()
status_placeholder = st.empty()
debug_expander = st.expander("🔍 Debug Information")

# Auto-refresh button
if st.button("🔄 Refresh Data") or consumer:
    if consumer is None:
        st.error("Cannot connect to Kafka. Please check your Kafka server.")
    else:
        try:
            # Poll messages with timeout
            messages = consumer.poll(timeout_ms=1000, max_records=10)
            
            if messages:
                msg_count = sum(len(msgs) for msgs in messages.values())
                status_placeholder.success(f"✅ Received {msg_count} messages")
                
                for topic_partition, msgs in messages.items():
                    for msg in msgs:
                        try:
                            tx = msg.value
                            
                            # Debug: Show raw message structure
                            with debug_expander:
                                st.json(tx)
                                st.write("Available keys:", list(tx.keys()) if isinstance(tx, dict) else "Not a dict")
                            
                            # Add to data list
                            st.session_state.data.append(tx)
                            
                            # Safe access to 'prediction' key with .get()
                            # Check multiple possible key names
                            prediction = None
                            if isinstance(tx, dict):
                                # Try different possible key names
                                prediction = (
                                    tx.get('prediction') or 
                                    tx.get('pred') or 
                                    tx.get('label') or 
                                    tx.get('fraud') or
                                    tx.get('is_fraud') or
                                    'UNKNOWN'
                                )
                            else:
                                prediction = 'UNKNOWN'
                            
                            # Convert to uppercase for comparison
                            prediction = str(prediction).upper()
                            
                            # Count predictions
                            if prediction in ['FRAUD', '1', 'TRUE', 'YES']:
                                st.session_state.fraud_count += 1
                            elif prediction in ['NOT_FRAUD', 'NORMAL', '0', 'FALSE', 'NO']:
                                st.session_state.normal_count += 1
                            else:
                                st.session_state.unknown_count += 1
                                
                        except Exception as e:
                            error_msg = f"Error processing message: {str(e)}"
                            st.session_state.error_log.append(error_msg)
                            with debug_expander:
                                st.error(error_msg)
                                st.write("Raw message:", msg.value)
            else:
                status_placeholder.info("⏳ Waiting for new messages...")
            
            # Display metrics
            with metric_cols[0]:
                st.metric("🔴 Fraud Count", st.session_state.fraud_count)
            with metric_cols[1]:
                st.metric("🟢 Normal Count", st.session_state.normal_count)
            with metric_cols[2]:
                st.metric("❓ Unknown", st.session_state.unknown_count)
            
            # Display data table
            if st.session_state.data:
                df = pd.DataFrame(st.session_state.data)
                
                # Show column names for debugging
                with debug_expander:
                    st.write("DataFrame columns:", df.columns.tolist())
                
                table_placeholder.dataframe(df.tail(10), use_container_width=True)
            else:
                table_placeholder.info("No data received yet. Waiting for transactions...")
            
            # Show error log if any
            if st.session_state.error_log:
                with debug_expander:
                    st.warning("Error Log:")
                    for err in st.session_state.error_log[-5:]:  # Show last 5 errors
                        st.text(err)
                
        except Exception as e:
            st.error(f"❌ Error reading from Kafka: {str(e)}")
            st.exception(e)

# Control buttons
col1, col2 = st.columns(2)
with col1:
    if st.button("🗑️ Clear Data"):
        st.session_state.data = []
        st.session_state.fraud_count = 0
        st.session_state.normal_count = 0
        st.session_state.unknown_count = 0
        st.session_state.error_log = []
        st.rerun()

with col2:
    auto_refresh = st.checkbox("🔄 Auto-refresh every 2 seconds")
    
if auto_refresh:
    time.sleep(2)
    st.rerun()
