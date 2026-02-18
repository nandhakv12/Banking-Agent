"""
Account Tools
Tools for account operations that Claude agents will use
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from firebase.firestore import (
    create_account as db_create_account,
    get_accounts as db_get_accounts,
    get_account as db_get_account
)
import json


def create_bank_account(user_id: str, account_type: str, initial_deposit: float, account_name: str = "") -> str:
    """
    Create a new bank account for the user
    
    Args:
        user_id: User's unique ID
        account_type: Type of account - 'checking' or 'savings'
        initial_deposit: Initial deposit amount in USD (min $25 checking, $100 savings)
        account_name: Optional custom name for the account
    
    Returns:
        JSON string with account creation result
    """
    result = db_create_account(user_id, account_type, initial_deposit, account_name)
    return json.dumps(result, indent=2)


def get_all_accounts(user_id: str) -> str:
    """
    Get all bank accounts for the user
    
    Args:
        user_id: User's unique ID
    
    Returns:
        JSON string with list of all accounts and total balance
    """
    result = db_get_accounts(user_id)
    return json.dumps(result, indent=2)


def get_account_details(user_id: str, account_id: str) -> str:
    """
    Get detailed information about a specific account
    
    Args:
        user_id: User's unique ID
        account_id: Account ID to get details for
    
    Returns:
        JSON string with account details
    """
    result = db_get_account(account_id, user_id)
    return json.dumps(result, indent=2)


# ============================================================
# TOOL DEFINITIONS FOR LANGCHAIN (NOT USED IN AGENTS ANYMORE)
# ============================================================

ACCOUNT_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "create_bank_account",
            "description": "Create a new bank account (checking or savings) for the user. Checking requires minimum $25, savings requires $100.",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "User's unique ID from login/session"
                    },
                    "account_type": {
                        "type": "string",
                        "enum": ["checking", "savings"],
                        "description": "Type of account to create"
                    },
                    "initial_deposit": {
                        "type": "number",
                        "description": "Initial deposit amount in USD"
                    },
                    "account_name": {
                        "type": "string",
                        "description": "Optional custom name for the account (e.g., 'Emergency Fund')"
                    }
                },
                "required": ["user_id", "account_type", "initial_deposit"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_all_accounts",
            "description": "Get a list of all bank accounts for the user with their balances and details.",
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
    },
    {
        "type": "function",
        "function": {
            "name": "get_account_details",
            "description": "Get detailed information about a specific bank account.",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "User's unique ID"
                    },
                    "account_id": {
                        "type": "string",
                        "description": "Account ID to get details for"
                    }
                },
                "required": ["user_id", "account_id"]
            }
        }
    }
]

# Tool function mapping
TOOL_FUNCTIONS = {
    "create_bank_account": create_bank_account,
    "get_all_accounts": get_all_accounts,
    "get_account_details": get_account_details
}


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":
    print("🧪 Testing Account Tools...\n")
    
    print("📋 Available Tools:")
    for i, tool in enumerate(ACCOUNT_TOOLS, 1):
        print(f"\n{i}. {tool['function']['name']}")
        print(f"   Description: {tool['function']['description']}")
        print(f"   Parameters: {list(tool['function']['parameters']['properties'].keys())}")
    
    print("\n✅ Account tools loaded successfully!")
    print(f"✅ Tool functions: {list(TOOL_FUNCTIONS.keys())}")