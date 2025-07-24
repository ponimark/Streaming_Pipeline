# ---------- Database Config ----------
MYSQL_CONFIG = {
    "host": "localhost",
    "user": "root",             # change if different
    "password": "",  # change to your MySQL password
    "database": "de"
}

POSTGRES_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "user": "postgres",          # will be used later (Flink writes here)
    "password": "",
    "database": "postgres"
}

# ---------- Kafka Config ----------
KAFKA_CONFIG = {
    "bootstrap_servers": "localhost:9092",
    "bootstrap_servers_docker": "kafka:29092",
    "topic": "app_events",
    "group_id": "flink_consumer_group"
}

# ---------- Producer Settings ----------
PRODUCER_SETTINGS = {
    "min_interval": 0.5,   # min seconds between messages
    "max_interval": 2.0    # max seconds between messages
}

# ---------- Misc ----------
DEVICES = ["iPhone 14", "iPhone 15 Pro", "iPad Air","MacBook Pro","iPad Pro"]

