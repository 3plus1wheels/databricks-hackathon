import os
from dotenv import load_dotenv

load_dotenv()

DATABRICKS_HOST = os.environ.get("DATABRICKS_HOST", "")
DATABRICKS_TOKEN = os.environ.get("DATABRICKS_TOKEN", "")
DATABRICKS_WAREHOUSE_ID = os.environ.get("DATABRICKS_WAREHOUSE_ID", "")
DATABRICKS_CATALOG = os.environ.get("DATABRICKS_CATALOG", "workbench")
DATABRICKS_SCHEMA = os.environ.get("DATABRICKS_SCHEMA", "default")
