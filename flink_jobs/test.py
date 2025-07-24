from pyflink.datastream import StreamExecutionEnvironment
from pyflink.common.watermark_strategy import WatermarkStrategy
from pyflink.datastream.connectors.kafka import KafkaSource, KafkaOffsetsInitializer
from pyflink.common.serialization import SimpleStringSchema


env = StreamExecutionEnvironment.get_execution_environment()

kafka_source = (
    KafkaSource.builder()
    .set_bootstrap_servers("kafka:29092")
    .set_topics("app_events")
    .set_group_id("flink_test_group")
    .set_starting_offsets(KafkaOffsetsInitializer.earliest())
    .set_value_only_deserializer(SimpleStringSchema())
    .build()
)

ds = env.from_source(
    source=kafka_source,
    watermark_strategy=WatermarkStrategy.for_monotonous_timestamps(),
    source_name="Kafka Source"
)

ds.print()
env.execute("Flink Kafka Test Consumer")
