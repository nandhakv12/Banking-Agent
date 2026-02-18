"""
Transfer Tools
Tools for transferring money between accounts
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from firebase.firestore import transfer_money as db_transfer_money
import json


def transfer_between_accounts(user_id: str, from_account_id: str, to_account_id: str, 
                              amount: float, memo: str = "") -> str:
    """
    Transfer money from one account to another
    
    Args:
        user_id: User's unique ID
        from_account_id: Source account ID
        to_account_id: Destination account ID
        amount: Amount to transfer in USD
        memo: Optional memo/note for the transfer
    
    Returns:
        JSON string with transfer result
    """
    result = db_transfer_money(user_id, from_account_id, to_account_id, amount, memo)
    return json.dumps(result, indent=2)


# ============================================================
# TOOL DEFINITIONS FOR LANGCHAIN (LEGACY - NOT USED)
# ============================================================

TRANSFER_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "transfer_between_accounts",
            "description": "Transfer money from one bank account to another. Maximum $10,000 per transfer. Always confirm amount and accounts with user before executing.",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "User's unique ID"
                    },
                    "from_account_id": {
                        "type": "string",
                        "description": "Source account ID to transfer FROM"
                    },
                    "to_account_id": {
                        "type": "string",
                        "description": "Destination account ID to transfer TO"
                    },
                    "amount": {
                        "type": "number",
                        "description": "Amount to transfer in USD"
                    },
                    "memo": {
                        "type": "string",
                        "description": "Optional memo or note for the transfer"
                    }
                },
                "required": ["user_id", "from_account_id", "to_account_id", "amount"]
            }
        }
    }
]

# Tool function mapping
TOOL_FUNCTIONS = {
    "transfer_between_accounts": transfer_between_accounts
}


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":
    print("🧪 Testing Transfer Tools...\n")
    
    print("📋 Available Tools:")
    for i, tool in enumerate(TRANSFER_TOOLS, 1):
        print(f"\n{i}. {tool['function']['name']}")
        print(f"   Description: {tool['function']['description']}")
    
    print("\n✅ Transfer tools loaded successfully!")
    print(f"✅ Tool functions: {list(TOOL_FUNCTIONS.keys())}")