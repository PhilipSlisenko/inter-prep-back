import os

import stripe
from typing_extensions import Literal

config_local = {
    # "db_connection_string": "sqlite:///./.db/dev.db",
    "db_connection_string": "postgresql+psycopg2://postgres.irlgafcrfahfczuryude:@aws-0-us-east-1.pooler.supabase.com:5432/postgres",
    # postgresql://neondb_owner:{neon_pass}@ep-falling-hat-a5ca29nd.us-east-2.aws.neon.tech/neondb?sslmode=require
    "table_names_prefix": "test_",
    "front_domain": "http://localhost:3000",
    "auth0_domain": "https://inter-prep.us.auth0.com",
    "auth0_api_audience": "inter-prep-api",
    "auth0_algorithms": ["RS256"],
}

config_prd = {
    "db_connection_string": f"postgresql+psycopg2://postgres:{os.getenv('DB_PASS')}@viaduct.proxy.rlwy.net:54652/railway",
    "table_names_prefix": "test_",
    "front_domain": "https://www.interprep.org",
    "auth0_domain": "https://inter-prep.us.auth0.com",
    "auth0_api_audience": "inter-prep-api",
    "auth0_algorithms": ["RS256"],
}

env: Literal["local", "prd"] = os.getenv("ENV", "local")  # type: ignore

if env == "local":
    config = config_local
if env == "prd":
    config = config_prd

stripe.api_key = os.getenv("STRIPE_API_KEY")
