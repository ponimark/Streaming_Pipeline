from kafka.admin import KafkaAdminClient, NewTopic

admin_client = KafkaAdminClient(
    bootstrap_servers="localhost:9092",
    client_id='topic_creator'
)

topic_name = "app_events"

# Check if topic already exists
existing_topics = admin_client.list_topics()
if topic_name not in existing_topics:
    topic = NewTopic(
        name=topic_name,
        num_partitions=3,
        replication_factor=1
    )
    admin_client.create_topics([topic])
    print(f"✅ Topic '{topic_name}' created successfully.")
else:
    print(f"ℹ️ Topic '{topic_name}' already exists.")

admin_client.close()
