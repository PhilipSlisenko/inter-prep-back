import os

import stripe

config = {
    # "db_connection_string": "sqlite:///./.db/dev.db",
    "db_connection_string": "postgresql+psycopg2://postgres.irlgafcrfahfczuryude:W909WFPSMHJxTWf2@aws-0-us-east-1.pooler.supabase.com:5432/postgres",
    "table_names_prefix": "test_",
    "front_domain": "http://localhost:3000",
    "auth0_domain": "https://inter-prep.us.auth0.com",
    "auth0_api_audience": "inter-prep-api",
    "auth0_algorithms": ["RS256"],
}


stripe.api_key = os.environ.get("STRIPE_API_KEY", "")
