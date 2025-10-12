from kafka import KafkaProducer
import json
import random
from uuid import uuid4
from datetime import datetime
import time

# Connect to Kafka
producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda x: json.dumps(x).encode('utf-8')
)

print("🚀 Kafka Producer started...")

while True:
    transaction = {
        "id": str(uuid4()),
        "amount": round(random.uniform(10, 1000), 2),
        "type": random.choice(["online", "in-store"]),
        "timestamp": datetime.utcnow().isoformat(),
        "prediction": random.choice(["FRAUD", "NOT_FRAUD"])  # <-- KEY PART!
    }

    producer.send("transactions", transaction)
    print("📤 Sent:", transaction)

    time.sleep(1)  # 1 second delay
