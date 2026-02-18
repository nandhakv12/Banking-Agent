"""
Transaction Tools
Tools for viewing transaction history
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from firebase.firestore import get_transactions as db_get_transactions
import json


def get_transaction_history(user_id: str, account_id: str, limit: int = 10) -> str:
    """
    Get transaction history for a specific account
    
    Args:
        user_id: User's unique ID
        account_id: Account ID to get transactions for
        limit: Number of recent transactions to return (default 10, max 50)
    
    Returns:
        JSON string with transaction history
    """
    if limit > 50:
        limit = 50
    
    result = db_get_transactions(account_id, user_id, limit)
    return json.dumps(result, indent=2)


# ============================================================
# TOOL DEFINITIONS FOR LANGCHAIN (LEGACY - NOT USED)
# ============================================================

TRANSACTION_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_transaction_history",
            "description": "Get recent transaction history for a bank account. Shows credits, debits, and transfers.",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "User's unique ID"
                    },
                    "account_id": {
                        "type": "string",
                        "description": "Account ID to get transactions for"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Number of recent transactions to return (default 10, max 50)"
                    }
                },
                "required": ["user_id", "account_id"]
            }
        }
    }
]

# Tool function mapping
TOOL_FUNCTIONS = {
    "get_transaction_history": get_transaction_history
}


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":
    print("🧪 Testing Transaction Tools...\n")
    
    print("📋 Available Tools:")
    for i, tool in enumerate(TRANSACTION_TOOLS, 1):
        print(f"\n{i}. {tool['function']['name']}")
        print(f"   Description: {tool['function']['description']}")
    
    print("\n✅ Transaction tools loaded successfully!")
    print(f"✅ Tool functions: {list(TOOL_FUNCTIONS.keys())}")