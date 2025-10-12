import streamlit as st
import pandas as pd
import json
from kafka import KafkaConsumer
import time

# UI setup
st.set_page_config(layout="wide")
st.title("📊 Real-Time Fraud Detection Dashboard")
st.markdown("### 🔄 Live Transaction Stream")

# Initialize session state
if 'data' not in st.session_state:
    st.session_state.data = []
    st.session_state.fraud_count = 0
    st.session_state.normal_count = 0
    st.session_state.unknown_count = 0
    st.session_state.error_log = []

# Kafka consumer
@st.cache_resource
def get_kafka_consumer():
    try:
        return KafkaConsumer(
            'transactions',
            bootstrap_servers='localhost:9092',
            auto_offset_reset='latest',
            enable_auto_commit=True,
            group_id='dashboard-group',
            value_deserializer=lambda x: json.loads(x.decode('utf-8')),
            consumer_timeout_ms=1000
        )
    except Exception as e:
        st.error(f"❌ Kafka Error: {str(e)}")
        return None

consumer = get_kafka_consumer()

metric_cols = st.columns(3)
table_placeholder = st.empty()
status_placeholder = st.empty()
debug_expander = st.expander("🔍 Debug Info")

# Process messages
if st.button("🔄 Refresh Data") or consumer:
    if consumer:
        try:
            messages = consumer.poll(timeout_ms=1000, max_records=10)
            if messages:
                count = sum(len(msgs) for msgs in messages.values())
                status_placeholder.success(f"✅ Received {count} messages")
                for _, msgs in messages.items():
                    for msg in msgs:
                        try:
                            tx = msg.value
                            if isinstance(tx, dict):
                                prediction = (
                                    tx.get('prediction') or
                                    tx.get('label') or
                                    tx.get('fraud') or
                                    tx.get('is_fraud') or
                                    'UNKNOWN'
                                )
                                prediction = str(prediction).upper()
                                tx['prediction'] = prediction
                                st.session_state.data.append(tx)

                                if prediction in ['FRAUD', '1', 'TRUE', 'YES']:
                                    st.session_state.fraud_count += 1
                                elif prediction in ['NOT_FRAUD', 'NORMAL', '0', 'FALSE', 'NO']:
                                    st.session_state.normal_count += 1
                                else:
                                    st.session_state.unknown_count += 1
                        except Exception as e:
                            st.session_state.error_log.append(str(e))
            else:
                status_placeholder.info("⏳ Waiting for new messages...")
        except Exception as e:
            st.error(f"Kafka read error: {e}")
            st.stop()

# Metrics
with metric_cols[0]: st.metric("🔴 Fraud", st.session_state.fraud_count)
with metric_cols[1]: st.metric("🟢 Normal", st.session_state.normal_count)
with metric_cols[2]: st.metric("❓ Unknown", st.session_state.unknown_count)

# Charts and Filters
if st.session_state.data:
    df = pd.DataFrame(st.session_state.data)

    # Filters
    st.markdown("### 🔍 Filter Transactions")
    min_amount = st.slider("Minimum Amount", 0, int(df.get('amount', pd.Series([0])).max() or 1000), 10)
    df_filtered = df[df.get('amount', 0) >= min_amount]

    # Charts
    st.markdown("### 📊 Charts")
    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        st.bar_chart(df_filtered['prediction'].value_counts())

    if 'timestamp' in df_filtered.columns:
        df_filtered['timestamp'] = pd.to_datetime(df_filtered['timestamp'], errors='coerce')
        line_data = df_filtered.groupby([df_filtered['timestamp'].dt.floor('min'), 'prediction']).size().unstack(fill_value=0)
        with chart_col2:
            st.line_chart(line_data)

    st.markdown("### 📋 Latest Transactions")
    table_placeholder.dataframe(df_filtered.tail(10), use_container_width=True)
else:
    st.info("No data received yet.")

# Clear data
col1, col2 = st.columns(2)
with col1:
    if st.button("🗑️ Clear"):
        for key in ['data', 'fraud_count', 'normal_count', 'unknown_count', 'error_log']:
            st.session_state[key] = []
        st.rerun()

with col2:
    if st.checkbox("🔄 Auto-refresh every 2 seconds"):
        time.sleep(2)
        st.rerun()

