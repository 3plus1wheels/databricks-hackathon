import os
from dotenv import load_dotenv

load_dotenv()

DATABRICKS_HOST = os.environ.get("DATABRICKS_HOST", "")
DATABRICKS_TOKEN = os.environ.get("DATABRICKS_TOKEN", "")
DATABRICKS_WAREHOUSE_ID = os.environ.get("DATABRICKS_WAREHOUSE_ID", "")
DATABRICKS_CATALOG = os.environ.get("DATABRICKS_CATALOG", "workbench")
DATABRICKS_SCHEMA = os.environ.get("DATABRICKS_SCHEMA", "default")

# Genie Space ID — find it in Databricks UI: AI/BI > Genie, copy the space ID from the URL
GENIE_SPACE_ID = os.environ.get("GENIE_SPACE_ID", "")
