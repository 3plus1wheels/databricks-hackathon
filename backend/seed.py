"""Create Delta tables for Workbench in Databricks."""

from databricks import sql as dbsql
import config


def main():
    conn = dbsql.connect(
        server_hostname=config.DATABRICKS_HOST.replace("https://", ""),
        http_path=f"/sql/1.0/warehouses/{config.DATABRICKS_WAREHOUSE_ID}",
        access_token=config.DATABRICKS_TOKEN,
    )

    fqn = f"{config.DATABRICKS_CATALOG}.{config.DATABRICKS_SCHEMA}"

    with conn.cursor() as cur:
        # Create catalog/schema if needed
        cur.execute(f"CREATE CATALOG IF NOT EXISTS {config.DATABRICKS_CATALOG}")
        cur.execute(f"CREATE SCHEMA IF NOT EXISTS {fqn}")

        # Tasks table
        cur.execute(f"""
            CREATE TABLE IF NOT EXISTS {fqn}.tasks (
                task_id STRING NOT NULL,
                title STRING NOT NULL,
                description STRING NOT NULL,
                status STRING NOT NULL DEFAULT 'todo',
                assigned_agents STRING DEFAULT '[]',
                created_at TIMESTAMP,
                updated_at TIMESTAMP,
                result STRING
            )
        """)

        # Messages table
        cur.execute(f"""
            CREATE TABLE IF NOT EXISTS {fqn}.messages (
                message_id STRING NOT NULL,
                task_id STRING NOT NULL,
                role STRING NOT NULL,
                content STRING NOT NULL,
                agent_name STRING,
                created_at TIMESTAMP,
                metadata STRING
            )
        """)

    conn.close()
    print(f"Tables created in {fqn}")


if __name__ == "__main__":
    main()
