import os
from cassandra.cluster import Cluster
import redis


def connect_to_cassandra(cassandra_host, cassandra_port):
    cluster = Cluster([cassandra_host], port=cassandra_port)
    try:
        session = cluster.connect()

        # Create keyspace and table if they do not exist
        session.execute(
            """
        CREATE KEYSPACE IF NOT EXISTS test_keyspace WITH REPLICATION = {
            'class': 'SimpleStrategy',
            'replication_factor': 1
        }
        """
        )
        session.set_keyspace("test_keyspace")
        session.execute(
            """
        CREATE TABLE IF NOT EXISTS test_table (
            id UUID PRIMARY KEY,
            value text
        )
        """
        )

        # Insert a test value
        from uuid import uuid4

        test_id = uuid4()
        session.execute(
            "INSERT INTO test_table (id, value) VALUES (%s, %s)",
            (test_id, "test_value"),
        )

        # Retrieve the test value
        rows = session.execute("SELECT value FROM test_table WHERE id=%s", (test_id,))
        for row in rows:
            print(f"Connected to Cassandra, retrieved value: {row.value}")
    finally:
        cluster.shutdown()


def connect_to_redis(redis_host, redis_port):
    r = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)
    r.set("test_key", "test_value")
    value = r.get("test_key")
    print(f"Connected to Redis, retrieved value: {value}")


if __name__ == "__main__":
    print(f"Cassandra internal docker network")
    cassandra_host = os.getenv("CASSANDRA_HOST", "localhost")
    cassandra_port = int(os.getenv("CASSANDRA_PORT", 9042))
    connect_to_cassandra(cassandra_host, cassandra_port)

    print(f"Cassandra external host network")
    cassandra_host_ext = os.getenv("CASSANDRA_HOST_EXT", "localhost")
    cassandra_port_ext = int(os.getenv("CASSANDRA_PORT_EXT", 9042))
    connect_to_cassandra(cassandra_host_ext, cassandra_port_ext)

    print(f"Redis internal docker network")
    redis_host = os.getenv("REDIS_HOST", "localhost")
    redis_port = int(os.getenv("REDIS_PORT", 6379))
    connect_to_redis(redis_host, redis_port)

    print(f"Redis external host network")
    redis_host_ext = os.getenv("REDIS_HOST_EXT", "localhost")
    redis_port_ext = int(os.getenv("REDIS_PORT_EXT", 6379))
    connect_to_redis(redis_host_ext, redis_port_ext)
