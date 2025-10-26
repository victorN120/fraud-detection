import streamlit as st
import pandas as pd
import json
from kafka import KafkaConsumer
from kafka.errors import KafkaError
import time
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Page configuration
st.set_page_config(
    layout="wide", 
    page_title="Fraud Detection Dashboard",
    initial_sidebar_state="expanded"
)

# Enhanced CSS for professional dashboard styling
st.markdown("""
<style>
    /* ========== MAIN APP BACKGROUND ========== */
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%) !important;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif !important;
    }

    /* ========== MAIN CONTAINER ========== */
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
        max-width: 100% !important;
    }

    /* ========== SIDEBAR STYLING ========== */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%) !important;
        box-shadow: 4px 0 15px rgba(0, 0, 0, 0.1) !important;
    }

    section[data-testid="stSidebar"] * {
        color: white !important;
    }

    section[data-testid="stSidebar"] .stMarkdown {
        color: white !important;
    }

    section[data-testid="stSidebar"] label {
        color: white !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
    }

    section[data-testid="stSidebar"] .stSlider label {
        color: white !important;
    }

    section[data-testid="stSidebar"] hr {
        margin: 1rem 0 !important;
        border-color: rgba(255, 255, 255, 0.2) !important;
    }

    /* ========== METRICS STYLING ========== */
    div[data-testid="stMetricValue"] {
        font-size: 3rem !important;
        font-weight: 900 !important;
        color: #1a1a1a !important;
        text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.05) !important;
    }

    div[data-testid="stMetricLabel"] {
        font-size: 1.2rem !important;
        font-weight: 700 !important;
        color: #333 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
    }

    div[data-testid="stMetricDelta"] {
        font-size: 1.1rem !important;
        font-weight: 600 !important;
    }

    div[data-testid="stMetric"] {
        background: white !important;
        padding: 1.5rem !important;
        border-radius: 15px !important;
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.15) !important;
        border: none !important;
        transition: transform 0.3s ease, box-shadow 0.3s ease !important;
    }

    div[data-testid="stMetric"]:hover {
        transform: translateY(-5px) !important;
        box-shadow: 0 12px 24px rgba(0, 0, 0, 0.2) !important;
    }

    /* ========== TYPOGRAPHY ========== */
    h1 {
        font-size: 3.5rem !important;
        font-weight: 900 !important;
        color: #1a1a1a !important;
        margin-bottom: 0.5rem !important;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.1) !important;
        letter-spacing: -0.5px !important;
    }

    h2 {
        font-size: 2rem !important;
        font-weight: 700 !important;
        color: #333 !important;
        margin-top: 1rem !important;
        margin-bottom: 1rem !important;
    }

    h3 {
        font-size: 1.5rem !important;
        font-weight: 700 !important;
        color: #444 !important;
        margin-bottom: 0.75rem !important;
    }

    h4 {
        font-size: 1.25rem !important;
        font-weight: 600 !important;
        color: #555 !important;
    }

    /* ========== BUTTONS ========== */
    .stButton button {
        border-radius: 10px !important;
        font-weight: 700 !important;
        font-size: 1.1rem !important;
        padding: 0.75rem 2rem !important;
        border: none !important;
        transition: all 0.3s ease !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
    }

    .stButton button:hover {
        transform: translateY(-3px) !important;
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.2) !important;
    }

    .stButton button[kind="primary"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
    }

    /* ========== DATAFRAME & TABLES ========== */
    div[data-testid="stDataFrame"] {
        border-radius: 15px !important;
        overflow: hidden !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1) !important;
        background: white !important;
    }

    div[data-testid="stDataFrame"] table {
        font-size: 0.95rem !important;
    }

    div[data-testid="stDataFrame"] thead tr th {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        font-size: 0.85rem !important;
        letter-spacing: 0.5px !important;
        padding: 1rem !important;
    }

    /* ========== ALERT BOXES ========== */
    div[data-testid="stAlert"] {
        border-radius: 12px !important;
        border: none !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1) !important;
        font-size: 1.1rem !important;
        font-weight: 600 !important;
        padding: 1.5rem !important;
    }

    /* Success alert */
    div[data-baseweb="notification"][kind="success"] {
        background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%) !important;
        border-left: 5px solid #28a745 !important;
    }

    /* Error alert */
    div[data-baseweb="notification"][kind="error"] {
        background: linear-gradient(135deg, #f8d7da 0%, #f5c6cb 100%) !important;
        border-left: 5px solid #dc3545 !important;
    }

    /* Info alert */
    div[data-baseweb="notification"][kind="info"] {
        background: linear-gradient(135deg, #d1ecf1 0%, #bee5eb 100%) !important;
        border-left: 5px solid #17a2b8 !important;
    }

    /* Warning alert */
    div[data-baseweb="notification"][kind="warning"] {
        background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%) !important;
        border-left: 5px solid #ffc107 !important;
    }

    /* ========== INPUT ELEMENTS ========== */
    .stSlider > div > div > div {
        background: rgba(255, 255, 255, 0.3) !important;
    }

    .stNumberInput input {
        border-radius: 8px !important;
        border: 2px solid #e0e0e0 !important;
        padding: 0.5rem !important;
        font-size: 1rem !important;
    }

    .stNumberInput input:focus {
        border-color: #667eea !important;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1) !important;
    }

    .stCheckbox label {
        font-size: 1rem !important;
        font-weight: 500 !important;
    }

    .stMultiSelect > div {
        border-radius: 8px !important;
    }

    /* ========== RADIO BUTTONS ========== */
    div.row-widget.stRadio > div {
        flex-direction: row !important;
        gap: 1rem !important;
    }

    /* ========== PLOTLY CHARTS ========== */
    .js-plotly-plot {
        border-radius: 15px !important;
        overflow: hidden !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1) !important;
        background: white !important;
    }

    /* ========== EXPANDER ========== */
    div[data-testid="stExpander"] {
        border-radius: 10px !important;
        border: 2px solid #e0e0e0 !important;
        background: white !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05) !important;
    }

    div[data-testid="stExpander"]:hover {
        border-color: #667eea !important;
    }

    /* ========== DIVIDER ========== */
    hr {
        margin: 2rem 0 !important;
        border: none !important;
        border-top: 2px solid rgba(0, 0, 0, 0.1) !important;
    }

    /* ========== SCROLLBAR ========== */
    ::-webkit-scrollbar {
        width: 10px !important;
        height: 10px !important;
    }

    ::-webkit-scrollbar-track {
        background: #f1f1f1 !important;
        border-radius: 5px !important;
    }

    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        border-radius: 5px !important;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #764ba2 0%, #667eea 100%) !important;
    }

    /* ========== LOADING SPINNER ========== */
    div[data-testid="stSpinner"] > div {
        border-top-color: #667eea !important;
    }

    /* ========== TOOLTIPS ========== */
    .stTooltipIcon {
        color: #667eea !important;
    }

    /* ========== CODE BLOCKS ========== */
    code {
        background-color: #f4f4f4 !important;
        border-radius: 4px !important;
        padding: 2px 6px !important;
        font-family: 'Courier New', monospace !important;
        color: #c7254e !important;
    }

    pre {
        background-color: #f8f9fa !important;
        border-radius: 8px !important;
        padding: 1rem !important;
        border-left: 4px solid #667eea !important;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'data' not in st.session_state:
    st.session_state.data = []
    st.session_state.fraud_count = 0
    st.session_state.normal_count = 0
    st.session_state.unknown_count = 0
    st.session_state.error_log = []
    st.session_state.total_messages = 0
    st.session_state.last_update = None

@st.cache_resource
def get_kafka_consumer():
    """Create and return a Kafka consumer with error handling"""
    try:
        consumer = KafkaConsumer(
            'transactions',
            bootstrap_servers='localhost:9092',
            auto_offset_reset='latest',
            enable_auto_commit=True,
            group_id='dashboard-group',
            value_deserializer=lambda x: json.loads(x.decode('utf-8')),
            consumer_timeout_ms=1000,
            session_timeout_ms=10000,
            heartbeat_interval_ms=3000
        )
        return consumer
    except KafkaError as e:
        st.error(f"❌ Kafka Connection Error: {str(e)}")
        return None
    except Exception as e:
        st.error(f"❌ Unexpected Error: {str(e)}")
        return None

def normalize_prediction(value):
    """Normalize prediction values to standard format"""
    if value is None:
        return 'UNKNOWN'
    
    val_str = str(value).strip().upper()
    
    if val_str in ['FRAUD', '1', 'TRUE', 'YES', 'FRAUDULENT']:
        return 'FRAUD'
    elif val_str in ['NOT_FRAUD', 'NORMAL', '0', 'FALSE', 'NO', 'LEGITIMATE', 'NOT FRAUD']:
        return 'NOT_FRAUD'
    else:
        return 'UNKNOWN'

# Sidebar controls
with st.sidebar:
    st.title("⚙️ Controls")
    st.markdown("---")
    
    st.subheader("🔄 Refresh Settings")
    auto_refresh = st.toggle("Auto-refresh", value=False)
    refresh_interval = st.slider("Interval (seconds)", 1, 10, 2)
    
    st.markdown("---")
    st.subheader("📊 Data Settings")
    max_records = st.number_input("Max records", 100, 5000, 1000, 100)
    
    st.markdown("---")
    st.subheader("🎨 Display")
    show_charts = st.checkbox("Show charts", value=True)
    show_table = st.checkbox("Show table", value=True)
    show_debug = st.checkbox("Show debug", value=False)
    
    st.markdown("---")
    if st.button("🗑️ Clear Data", use_container_width=True, type="primary"):
        st.session_state.data = []
        st.session_state.fraud_count = 0
        st.session_state.normal_count = 0
        st.session_state.unknown_count = 0
        st.session_state.total_messages = 0
        st.session_state.error_log = []
        st.session_state.last_update = None
        st.rerun()

# Main header
st.title("🛡️ Real-Time Fraud Detection Dashboard")
st.markdown("### 🔄 Live Transaction Stream")
st.markdown("---")

# Initialize consumer
consumer = get_kafka_consumer()

# Connection status
col1, col2 = st.columns([3, 1])
with col1:
    if consumer:
        st.success("✅ Connected to Kafka", icon="✅")
    else:
        st.error("❌ Not connected to Kafka", icon="❌")

with col2:
    if st.session_state.last_update:
        st.info(f"🕐 {st.session_state.last_update.strftime('%H:%M:%S')}")

st.markdown("---")

# Fetch new messages
if consumer:
    try:
        messages = consumer.poll(timeout_ms=1000, max_records=10)
        if messages:
            count = sum(len(msgs) for msgs in messages.values())
            st.session_state.total_messages += count
            st.session_state.last_update = datetime.now()
            
            for _, msgs in messages.items():
                for msg in msgs:
                    try:
                        tx = msg.value
                        
                        raw_prediction = (
                            tx.get('prediction') or 
                            tx.get('label') or 
                            tx.get('fraud') or
                            tx.get('is_fraud')
                        )
                        
                        prediction = normalize_prediction(raw_prediction)
                        tx['prediction'] = prediction
                        st.session_state.data.append(tx)

                        if prediction == 'FRAUD':
                            st.session_state.fraud_count += 1
                        elif prediction == 'NOT_FRAUD':
                            st.session_state.normal_count += 1
                        else:
                            st.session_state.unknown_count += 1
                            st.session_state.error_log.append(
                                f"Unknown prediction: '{raw_prediction}' in message: {tx.get('id', 'N/A')}"
                            )
                            
                    except Exception as e:
                        error_msg = f"Error processing message: {str(e)}"
                        st.session_state.error_log.append(error_msg)
            
    except KafkaError as e:
        st.error(f"❌ Kafka polling error: {str(e)}")
    except Exception as e:
        st.error(f"❌ Error reading messages: {str(e)}")

# Key Metrics
st.subheader("📈 Key Metrics")

metric_cols = st.columns(4)

total_transactions = st.session_state.fraud_count + st.session_state.normal_count + st.session_state.unknown_count
fraud_rate = (st.session_state.fraud_count / total_transactions * 100) if total_transactions > 0 else 0

with metric_cols[0]:
    st.metric(
        "🔴 Fraud", 
        st.session_state.fraud_count,
        delta=f"{fraud_rate:.1f}%" if fraud_rate > 0 else None,
        delta_color="inverse"
    )

with metric_cols[1]:
    st.metric(
        "🟢 Normal", 
        st.session_state.normal_count,
        delta=f"{(st.session_state.normal_count / total_transactions * 100) if total_transactions > 0 else 0:.1f}%"
    )

with metric_cols[2]:
    st.metric(
        "❓ Unknown", 
        st.session_state.unknown_count
    )

with metric_cols[3]:
    st.metric(
        "📨 Total", 
        st.session_state.total_messages
    )

st.markdown("---")

# Data visualization
if st.session_state.data:
    df = pd.DataFrame(st.session_state.data)
    
    # Keep only most recent records
    if len(st.session_state.data) > max_records:
        st.session_state.data = st.session_state.data[-max_records:]
        df = pd.DataFrame(st.session_state.data)

    # Filters
    st.subheader("🔍 Filters")
    
    filter_col1, filter_col2, filter_col3 = st.columns(3)
    
    with filter_col1:
        if 'amount' in df.columns and not df['amount'].empty:
            max_amount = float(df['amount'].max())
            min_amount = float(df['amount'].min())

            # Handle case where all amounts are the same
            if min_amount == max_amount:
                st.info(f"All transactions have the same amount: ${min_amount:.2f}")
            else:
                amount_range = st.slider(
                    "Amount Range",
                    min_amount,
                    max_amount,
                    (min_amount, max_amount),
                    format="$%.2f"
                )
                df = df[(df['amount'] >= amount_range[0]) & (df['amount'] <= amount_range[1])]
    
    with filter_col2:
        if 'prediction' in df.columns:
            prediction_filter = st.multiselect(
                "Prediction Type",
                options=['FRAUD', 'NOT_FRAUD', 'UNKNOWN'],
                default=['FRAUD', 'NOT_FRAUD', 'UNKNOWN']
            )
            df = df[df['prediction'].isin(prediction_filter)]
    
    with filter_col3:
        if 'type' in df.columns:
            available_types = df['type'].unique().tolist()
            if available_types:
                type_filter = st.multiselect(
                    "Transaction Type",
                    options=available_types,
                    default=available_types
                )
                df = df[df['type'].isin(type_filter)]

    st.markdown("---")

    # Charts
    if show_charts and not df.empty:
        st.subheader("📊 Analytics")
        
        chart_col1, chart_col2 = st.columns(2)
        
        with chart_col1:
            if 'prediction' in df.columns:
                prediction_counts = df['prediction'].value_counts()
                
                fig = go.Figure(data=[go.Pie(
                    labels=prediction_counts.index,
                    values=prediction_counts.values,
                    hole=0.5,
                    marker=dict(
                        colors=['#ff4757', '#2ed573', '#ffa502'],
                        line=dict(color='white', width=3)
                    ),
                    textinfo='label+percent+value',
                    textfont=dict(size=16, color='white', family='Arial Black'),
                    hovertemplate='<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>'
                )])
                
                fig.update_layout(
                    title={
                        'text': "<b>Prediction Distribution</b>",
                        'font': {'size': 22, 'color': '#1a1a1a', 'family': 'Arial Black'},
                        'x': 0.5,
                        'xanchor': 'center'
                    },
                    height=450,
                    showlegend=True,
                    legend=dict(
                        orientation="v",
                        yanchor="middle",
                        y=0.5,
                        xanchor="left",
                        x=1.05,
                        font=dict(size=14, family='Arial', color='#333')
                    ),
                    paper_bgcolor='white',
                    plot_bgcolor='white',
                    margin=dict(l=20, r=150, t=80, b=20)
                )
                st.plotly_chart(fig, use_container_width=True)
        
        with chart_col2:
            if 'amount' in df.columns and 'prediction' in df.columns:
                fig = px.box(
                    df, 
                    x='prediction', 
                    y='amount',
                    color='prediction',
                    color_discrete_map={'FRAUD': '#ff4757', 'NOT_FRAUD': '#2ed573', 'UNKNOWN': '#ffa502'},
                    title="<b>Amount Distribution by Prediction</b>"
                )
                
                fig.update_layout(
                    height=450,
                    showlegend=False,
                    title={
                        'font': {'size': 22, 'color': '#1a1a1a', 'family': 'Arial Black'},
                        'x': 0.5,
                        'xanchor': 'center'
                    },
                    paper_bgcolor='white',
                    plot_bgcolor='#f8f9fa',
                    xaxis=dict(
                        title=dict(text='<b>Prediction</b>', font=dict(size=14, color='#333')),
                        tickfont=dict(size=12, color='#333')
                    ),
                    yaxis=dict(
                        title=dict(text='<b>Amount ($)</b>', font=dict(size=14, color='#333')),
                        tickfont=dict(size=12, color='#333'),
                        gridcolor='#e0e0e0'
                    )
                )
                st.plotly_chart(fig, use_container_width=True)
        
        # Time series
        if 'timestamp' in df.columns:
            try:
                df_time = df.copy()
                df_time['timestamp'] = pd.to_datetime(df_time['timestamp'], errors='coerce')
                df_time = df_time.dropna(subset=['timestamp'])
                
                if not df_time.empty:
                    st.markdown("#### 📈 Transactions Over Time")
                    
                    time_data = df_time.groupby([
                        df_time['timestamp'].dt.floor('min'), 
                        'prediction'
                    ]).size().unstack(fill_value=0)
                    
                    fig = go.Figure()
                    colors = {'FRAUD': '#ff4757', 'NOT_FRAUD': '#2ed573', 'UNKNOWN': '#ffa502'}
                    
                    for col in time_data.columns:
                        fig.add_trace(go.Scatter(
                            x=time_data.index,
                            y=time_data[col],
                            mode='lines+markers',
                            name=col,
                            line=dict(color=colors.get(col, '#6c757d'), width=4),
                            marker=dict(size=10, line=dict(width=2, color='white')),
                            hovertemplate='<b>%{fullData.name}</b><br>Time: %{x}<br>Count: %{y}<extra></extra>'
                        ))
                    
                    fig.update_layout(
                        height=400,
                        hovermode='x unified',
                        legend=dict(
                            orientation="h",
                            yanchor="bottom",
                            y=1.02,
                            xanchor="right",
                            x=1,
                            font=dict(size=14, family='Arial', color='#333')
                        ),
                        paper_bgcolor='white',
                        plot_bgcolor='#f8f9fa',
                        xaxis=dict(
                            title=dict(text='<b>Time</b>', font=dict(size=14, color='#333')),
                            gridcolor='#e0e0e0',
                            tickfont=dict(size=12, color='#333')
                        ),
                        yaxis=dict(
                            title=dict(text='<b>Transaction Count</b>', font=dict(size=14, color='#333')),
                            gridcolor='#e0e0e0',
                            tickfont=dict(size=12, color='#333')
                        )
                    )
                    st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                st.warning(f"Could not create time series: {str(e)}")

        st.markdown("---")

    # Transaction table
    if show_table and not df.empty:
        st.subheader("📋 Recent Transactions")
        
        display_columns = [col for col in ['id', 'amount', 'type', 'timestamp', 'prediction'] if col in df.columns]
        if display_columns:
            recent_df = df[display_columns].tail(50).iloc[::-1].reset_index(drop=True)
            
            def highlight_rows(row):
                if 'prediction' in row:
                    if row['prediction'] == 'FRAUD':
                        return ['background-color: #ffebee; color: #c62828; font-weight: 700'] * len(row)
                    elif row['prediction'] == 'NOT_FRAUD':
                        return ['background-color: #e8f5e9; color: #2e7d32; font-weight: 700'] * len(row)
                    else:
                        return ['background-color: #fff9e6; color: #f57c00; font-weight: 700'] * len(row)
                return [''] * len(row)
            
            styled_df = recent_df.style.apply(highlight_rows, axis=1)
            
            if 'amount' in recent_df.columns:
                styled_df = styled_df.format({'amount': '${:.2f}'})
            
            st.dataframe(styled_df, use_container_width=True, height=500)
        else:
            st.dataframe(df.tail(50).iloc[::-1], use_container_width=True, height=500)
else:
    st.info("🔌 No data received yet. Waiting for transactions from Kafka...", icon="📡")

# Debug section
if show_debug:
    st.markdown("---")
    st.subheader("🔍 Debug Information")
    
    debug_col1, debug_col2 = st.columns(2)
    
    with debug_col1:
        st.markdown("**System Status**")
        st.json({
            "Consumer Connected": consumer is not None,
            "Data Points": len(st.session_state.data),
            "Total Messages": st.session_state.total_messages,
            "Errors Logged": len(st.session_state.error_log)
        })
    
    with debug_col2:
        if st.session_state.data:
            st.markdown("**Latest Message Sample**")
            st.json(st.session_state.data[-1])
    
    if st.session_state.error_log:
        st.markdown("**Recent Errors**")
        with st.expander("View Errors"):
            for error in st.session_state.error_log[-10:]:
                st.error(error)
        
        if st.button("Clear Error Log"):
            st.session_state.error_log = []
            st.rerun()

# Auto-refresh logic
if auto_refresh:
    time.sleep(refresh_interval)
    st.rerun()
