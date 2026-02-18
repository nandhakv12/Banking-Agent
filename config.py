"""
Banking App Configuration
All settings in one place - edit this file to change any setting
"""

import os

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Try to import streamlit for secrets
try:
    import streamlit as st
    _has_streamlit = True
except ImportError:
    _has_streamlit = False

# ============================================================
# ANTHROPIC (Claude AI)
# ============================================================
if _has_streamlit and 'ANTHROPIC_API_KEY' in st.secrets:
    ANTHROPIC_API_KEY = st.secrets['ANTHROPIC_API_KEY']
else:
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

CLAUDE_MODEL = "claude-sonnet-4-5-20250929"
MAX_TOKENS = 4096

# ============================================================
# FIREBASE
# ============================================================
if _has_streamlit and 'FIREBASE_PROJECT_ID' in st.secrets:
    FIREBASE_PROJECT_ID = st.secrets['FIREBASE_PROJECT_ID']
    FIREBASE_SERVICE_ACCOUNT = None  # Will use secrets directly
    FIREBASE_API_KEY = st.secrets.get('FIREBASE_API_KEY')
else:
    FIREBASE_PROJECT_ID = os.getenv("FIREBASE_PROJECT_ID")
    FIREBASE_SERVICE_ACCOUNT = os.getenv("FIREBASE_SERVICE_ACCOUNT")
    FIREBASE_API_KEY = os.getenv("FIREBASE_API_KEY")

# ... rest of config stays the same

# ============================================================
# ANTHROPIC (Claude AI)
# ============================================================
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
CLAUDE_MODEL      = "claude-sonnet-4-5-20250929"
MAX_TOKENS        = 4096

# ============================================================
# LANGSMITH (Tracing & Testing)
# ============================================================
LANGCHAIN_API_KEY      = os.getenv("LANGCHAIN_API_KEY")
LANGCHAIN_PROJECT      = os.getenv("LANGCHAIN_PROJECT", "banking-chatbot")
LANGCHAIN_TRACING_V2   = os.getenv("LANGCHAIN_TRACING_V2", "true")

# ============================================================
# FIREBASE
# ============================================================
FIREBASE_PROJECT_ID      = os.getenv("FIREBASE_PROJECT_ID")
FIREBASE_SERVICE_ACCOUNT = os.getenv("FIREBASE_SERVICE_ACCOUNT")

# ============================================================
# FIRESTORE COLLECTIONS
# ============================================================
COLLECTION_USERS        = "users"
COLLECTION_ACCOUNTS     = "accounts"
COLLECTION_TRANSACTIONS = "transactions"
COLLECTION_SESSIONS     = "sessions"

# ============================================================
# BANKING RULES
# ============================================================
MIN_DEPOSIT = {
    "checking": 25.00,
    "savings":  100.00
}

INTEREST_RATES = {
    "checking": 0.01,   # 0.01% APY
    "savings":  2.50    # 2.50% APY
}

MAX_TRANSFER_AMOUNT    = 10000.00   # Max single transfer
MAX_ACCOUNTS_PER_USER  = 5          # Max accounts per user
SESSION_EXPIRY_HOURS   = 24         # Session expires in 24 hours
ROUTING_NUMBER         = "021000021"

# ============================================================
# SECURITY
# ============================================================
MAX_LOGIN_ATTEMPTS  = 3    # Lock after 3 failed attempts
RATE_LIMIT_REQUESTS = 100  # Max requests per hour
MIN_PASSWORD_LENGTH = 12

# ============================================================
# AGENT SETTINGS
# ============================================================
AGENT_TEMPERATURE  = 0     # 0 = consistent responses
AGENT_MAX_RETRIES  = 3     # Retry failed tool calls
MEMORY_WINDOW_SIZE = 10    # Remember last 10 messages

# ============================================================
# STREAMLIT
# ============================================================
APP_TITLE   = "🏦 SecureBank AI Assistant"
APP_ICON    = "🏦"
APP_LAYOUT  = "wide"

# ============================================================
# VALIDATION
# ============================================================
def validate_config():
    """Validate all required config is present"""
    required = {
        "ANTHROPIC_API_KEY":      ANTHROPIC_API_KEY,
        "FIREBASE_PROJECT_ID":    FIREBASE_PROJECT_ID,
        "FIREBASE_SERVICE_ACCOUNT": FIREBASE_SERVICE_ACCOUNT,
    }

    missing = []
    for key, value in required.items():
        if not value:
            missing.append(key)

    if missing:
        raise ValueError(
            f"Missing required environment variables:\n" +
            "\n".join(f"  ❌ {k}" for k in missing)
        )

    print("✅ Configuration validated successfully!")
    return True


if __name__ == "__main__":
    validate_config()
    print("\n📋 Current Configuration:")
    print(f"  Model:      {CLAUDE_MODEL}")
    print(f"  Project:    {FIREBASE_PROJECT_ID}")
    print(f"  LangSmith:  {LANGCHAIN_PROJECT}")
    print(f"  Max tokens: {MAX_TOKENS}")