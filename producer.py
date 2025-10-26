from kafka import KafkaProducer
import json
import random
from uuid import uuid4
from datetime import datetime
import time

# Connect to Kafka with error handling
try:
    producer = KafkaProducer(
        bootstrap_servers='localhost:9092',
        value_serializer=lambda x: json.dumps(x).encode('utf-8'),
        acks='all',
        retries=3,
        max_in_flight_requests_per_connection=1
    )
    print("🚀 Kafka Producer started...")
except Exception as e:
    print(f"❌ Failed to connect to Kafka: {e}")
    exit(1)

try:
    message_count = 0
    while True:
        # Generate random prediction with 70% normal, 30% fraud
        is_fraud = random.random() < 0.3
        prediction = "FRAUD" if is_fraud else "NOT_FRAUD"
        
        transaction = {
            "id": str(uuid4()),
            "amount": round(random.uniform(10, 1000), 2),
            "type": random.choice(["online", "in-store"]),
            "timestamp": datetime.utcnow().isoformat(),
            "prediction": prediction  # Consistent field name
        }
        
        # Send with callback for error handling
        future = producer.send("transactions", transaction)
        
        try:
            record_metadata = future.get(timeout=10)
            message_count += 1
            emoji = "🔴" if is_fraud else "🟢"
            print(f"{emoji} [{message_count}] Sent: ID={transaction['id'][:8]}..., "
                  f"Amount=${transaction['amount']}, Type={transaction['type']}, "
                  f"Prediction={prediction}")
        except Exception as e:
            print(f"❌ Failed to send message: {e}")
        
        time.sleep(1)

except KeyboardInterrupt:
    print("\n🛑 Stopping producer...")
finally:
    producer.flush()
    producer.close()
    print(f"✅ Producer closed. Total messages sent: {message_count}")
