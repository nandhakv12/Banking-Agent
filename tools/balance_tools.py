"""
Balance Tools
Tools for checking account balances
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from firebase.firestore import get_balance as db_get_balance, get_accounts as db_get_accounts
import json


def check_balance(user_id: str, account_id: str) -> str:
    """
    Check the balance of a specific account
    
    Args:
        user_id: User's unique ID
        account_id: Account ID to check balance for
    
    Returns:
        JSON string with balance information
    """
    result = db_get_balance(account_id, user_id)
    return json.dumps(result, indent=2)


def get_total_balance(user_id: str) -> str:
    """
    Get total balance across all accounts
    
    Args:
        user_id: User's unique ID
    
    Returns:
        JSON string with total balance and breakdown by account
    """
    result = db_get_accounts(user_id)
    return json.dumps(result, indent=2)


# ============================================================
# TOOL DEFINITIONS FOR LANGCHAIN (LEGACY - NOT USED)
# ============================================================

BALANCE_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "check_balance",
            "description": "Check the current balance of a specific bank account.",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "User's unique ID"
                    },
                    "account_id": {
                        "type": "string",
                        "description": "Account ID to check balance for"
                    }
                },
                "required": ["user_id", "account_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_total_balance",
            "description": "Get total balance across all user's accounts with breakdown.",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "User's unique ID"
                    }
                },
                "required": ["user_id"]
            }
        }
    }
]

# Tool function mapping
TOOL_FUNCTIONS = {
    "check_balance": check_balance,
    "get_total_balance": get_total_balance
}


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":
    print("🧪 Testing Balance Tools...\n")
    
    print("📋 Available Tools:")
    for i, tool in enumerate(BALANCE_TOOLS, 1):
        print(f"\n{i}. {tool['function']['name']}")
        print(f"   Description: {tool['function']['description']}")
    
    print("\n✅ Balance tools loaded successfully!")
    print(f"✅ Tool functions: {list(TOOL_FUNCTIONS.keys())}")