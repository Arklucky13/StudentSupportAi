
import os

from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

supabase_url = os.getenv("SUPABASE_URL")
supabase_secret_key = os.getenv("SUPABASE_SECRET_KEY")

if not supabase_url or not supabase_secret_key:
    raise RuntimeError(
        "Set SUPABASE_URL and SUPABASE_SECRET_KEY in .env"
    )

supabase = create_client(
    supabase_url,
    supabase_secret_key,
)
