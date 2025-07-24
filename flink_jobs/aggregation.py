from pyflink.datastream import StreamExecutionEnvironment
from pyflink.table import StreamTableEnvironment, EnvironmentSettings

def create_kafka_source_table(t_env):
    ddl = """
        CREATE TABLE user_events (
            user_id INT,
            action STRING,
            event_time_raw STRING,
            event_time AS TO_TIMESTAMP(event_time_raw, 'yyyy-MM-dd''T''HH:mm:ss.SSS'),
            device STRING,
            WATERMARK FOR event_time AS event_time - INTERVAL '5' SECOND
        ) WITH (
            'connector' = 'kafka',
            'topic' = 'app_events',
            'properties.bootstrap.servers' = 'kafka:29092',
            'properties.group.id' = 'flink_consumer_group_debug_session',
            'scan.startup.mode' = 'latest-offset',
            'format' = 'json',
            'json.ignore-parse-errors' = 'true'
        )
        """
    t_env.execute_sql(ddl)


def create_aggregation_sink_table(t_env):
    ddl = """
        CREATE TABLE apple_app_aggregates (
            user_id INT,
            session_id STRING,
            session_start TIMESTAMP(3),
            session_end TIMESTAMP(3),
            device STRING,
            session_duration STRING,
            did_login BOOLEAN,
            did_purchase BOOLEAN,
            total_actions BIGINT,
            PRIMARY KEY (user_id, device, session_start, session_end) NOT ENFORCED
        ) WITH (
            'connector' = 'jdbc',
            'url' = 'jdbc:postgresql://host.docker.internal:5432/postgres',
            'table-name' = 'apple_app_aggregates',
            'driver' = 'org.postgresql.Driver',
            'username' = 'postgres',
            'password' = 'poni'
        )
        """
    t_env.execute_sql(ddl)


def insert_into_aggregation_sink(t_env):
    query = """
        INSERT INTO apple_app_aggregates
  SELECT
    user_id,
    CONCAT(CAST(user_id AS STRING), '_', DATE_FORMAT(window_start, 'yyyyMMddHHmmss')) AS session_id,
    window_start as session_start,
    window_end as session_end,
    device,
    '5 MINUTE' as session_duration,
   MAX(CASE WHEN action = 'login' THEN TRUE ELSE FALSE END) AS did_login,
   MAX(CASE WHEN action = 'purchase' THEN TRUE ELSE FALSE END) AS did_purchase,
    count(*) AS total_actions
  FROM TABLE(
    TUMBLE(
      TABLE user_events,
      DESCRIPTOR(event_time),
      INTERVAL '5' minute 
    )
  )
        GROUP BY user_id, device, window_start, window_end
"""
    t_env.execute_sql(query)


if __name__ == "__main__":
    env_settings = EnvironmentSettings.in_streaming_mode()
    env = StreamExecutionEnvironment.get_execution_environment()

    env.set_parallelism(1)
    env.enable_checkpointing(10000)  # checkpoint every 10 seconds

    t_env = StreamTableEnvironment.create(env, environment_settings=env_settings)



    create_kafka_source_table(t_env)
    create_aggregation_sink_table(t_env)
    insert_into_aggregation_sink(t_env)
