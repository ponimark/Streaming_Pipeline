import json
import time
import random
from datetime import datetime
from kafka import KafkaProducer
from docs import config
from docs.logger_activate import logger  # Ensure this sets up your logger

# ---------------------------
# Kafka Producer Configuration
# ---------------------------
producer = KafkaProducer(
    bootstrap_servers="localhost:9092",  # Or your Docker Kafka broker
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

# ---------------
# Event Generator
# ---------------
actions = [
    "login", "logout", "ad_click", "view_product", "add_to_cart",
    "remove_from_cart", "purchase", "search"
]

ACTION_WEIGHTS = [8, 8, 15, 30, 10, 5, 4, 20]

def generate_event():
    return {
        "user_id": random.randint(1, 1000),
        "action": random.choices(actions, weights=ACTION_WEIGHTS, k=1)[0],
        "event_time_raw": datetime.utcnow().isoformat(timespec='milliseconds'),
        "device": random.choice(config.DEVICES)
    }

def success_callback(event):
    def _log_success(record_metadata):
        logger.info(f"✅ Sent: {json.dumps(event)} | Offset: {record_metadata.offset}")
    return _log_success

# ------------------
# Produce Continuously
# ------------------
MESSAGES_PER_SECOND = 10

try:
    topic = config.KAFKA_CONFIG["topic"]
    logger.info(f"✅ Starting Kafka Producer to topic: {topic}")

    while True:
        for _ in range(MESSAGES_PER_SECOND):
            event = generate_event()
            future = producer.send(topic, value=event)
            future.add_callback(success_callback(event)) \
                  .add_errback(lambda e: logger.error(f"❌ Failed to send event: {e}"))
        # Wait for all messages to be sent
        producer.flush()
        time.sleep(1)

except KeyboardInterrupt:
    logger.info("🚫 Kafka Producer stopped manually.")
except Exception as e:
    logger.exception(f"🔥 Unexpected error in producer: {e}")
finally:
    producer.close()
    logger.info("🔌 Kafka Producer connection closed.")
