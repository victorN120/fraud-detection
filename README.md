# fraud-detection
Real-time fraud detection using Kafka, Spark, and Streamlit
# 🔍 Real-Time Fraud Detection System

[![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python)](https://www.python.org/)
[![Apache Kafka](https://img.shields.io/badge/Kafka-Streaming-black?logo=apachekafka)](https://kafka.apache.org/)
[![Apache Spark](https://img.shields.io/badge/Spark-StructuredStreaming-orange?logo=apachespark)](https://spark.apache.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-red?logo=streamlit)](https://streamlit.io/)

> A personal project by [victorN120](https://github.com/victorN120)  
> Built to simulate and visualize real-time fraud detection using Apache Kafka, Spark, and Streamlit.

---

## 🚀 Project Overview

This project simulates real-time financial transactions and performs fraud prediction on them using a mock model. The data is streamed live using **Apache Kafka**, processed using **Apache Spark**, and displayed in a **Streamlit web dashboard** with live charts, filters, and metrics.

---

## 🛠️ Technologies Used

- 🐍 Python 3.12
- 🔄 Apache Kafka (message broker)
- ⚡ Apache Spark (real-time processing with Structured Streaming)
- 📊 Streamlit (live dashboard)
- 🐳 Docker + WSL (for local containers)

---

## 📦 Features

- Real-time transaction stream via Kafka producer
- Fraud prediction simulation (`FRAUD` / `NOT_FRAUD`)
- Spark-based streaming consumer
- Web dashboard (Streamlit) with:
  - ✅ Live transaction table
  - 📊 Bar & line charts
  - 🔎 Amount slider to filter data
  - 🔴 Fraud & 🟢 Normal counts
  - 🧪 Debug info for raw messages

---

## 📁 Folder Structure

fraud-detection/
├── producer.py # Kafka producer to simulate transactions
├── spark_fraud_detector.py# Spark Structured Streaming job
├── dashboard.py # Streamlit dashboard
├── docker-compose.yml # Docker setup for Kafka + Zookeeper
└── requirements.txt # Python dependencies

yaml
Copy code

---

## ✅ How to Run This Project Locally

> 💡 Requires Docker, Python 3.12, and WSL2 (or Linux/macOS)

### 1️⃣ Clone the Repo
```bash
git clone https://github.com/victorN120/fraud-detection.git
cd fraud-detection

2️⃣ Start Kafka with Docker
bash

docker compose up -d


bash

docker exec -it fraud-detection-kafka-1 bash
kafka-topics.sh --create --topic transactions --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1
exit

3️⃣ Activate Python Virtual Environment
bash

python3 -m venv fraud-env
source fraud-env/bin/activate
pip install -r requirements.txt

4️⃣ Start the Producer
bash

python producer.py

5️⃣ Start the Spark Consumer
bash

spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.4.1 spark_fraud_detector.py

6️⃣ Start the Streamlit Dashboard
bash

streamlit run dashboard.py
