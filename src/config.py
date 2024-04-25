import os

import stripe

config = {
    # "db_connection_string": "sqlite:///./.db/dev.db",
    "db_connection_string": "postgresql+psycopg2://postgres.irlgafcrfahfczuryude:@aws-0-us-east-1.pooler.supabase.com:5432/postgres",
    # postgresql://neondb_owner:{neon_pass}@ep-falling-hat-a5ca29nd.us-east-2.aws.neon.tech/neondb?sslmode=require
    "table_names_prefix": "test_",
    "front_domain": "http://localhost:3000",
    "auth0_domain": "https://inter-prep.us.auth0.com",
    "auth0_api_audience": "inter-prep-api",
    "auth0_algorithms": ["RS256"],
}


stripe.api_key = os.environ.get("STRIPE_API_KEY", "")
