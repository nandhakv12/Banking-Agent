"""
Account Agent
Specialized agent for account creation and management
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from anthropic import Anthropic
from config import ANTHROPIC_API_KEY, CLAUDE_MODEL, MAX_TOKENS
from tools.account_tools import create_bank_account, get_all_accounts, get_account_details
import json


class AccountAgent:
    """Agent specialized in account operations"""
    
    def __init__(self):
        self.client = Anthropic(api_key=ANTHROPIC_API_KEY)
        self.model = CLAUDE_MODEL
        
        # Tools in correct Anthropic format
        self.tools = [
            {
                "name": "create_bank_account",
                "description": "Create a new bank account (checking or savings) for the user. Checking requires minimum $25, savings requires $100.",
                "input_schema": {
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
                            "description": "Optional custom name for the account"
                        }
                    },
                    "required": ["user_id", "account_type", "initial_deposit"]
                }
            },
            {
                "name": "get_all_accounts",
                "description": "Get a list of all bank accounts for the user with their balances and details.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "user_id": {
                            "type": "string",
                            "description": "User's unique ID"
                        }
                    },
                    "required": ["user_id"]
                }
            },
            {
                "name": "get_account_details",
                "description": "Get detailed information about a specific bank account.",
                "input_schema": {
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
        ]
        
        # Tool function mapping
        self.tool_functions = {
            "create_bank_account": create_bank_account,
            "get_all_accounts": get_all_accounts,
            "get_account_details": get_account_details
        }
        
        self.system_prompt = """You are a specialized banking agent focused on account management.

Your responsibilities:
- Help users create new bank accounts (checking or savings)
- Show users their existing accounts
- Provide account details and information

Important rules:
- Checking accounts require minimum $25 deposit
- Savings accounts require minimum $100 deposit
- Maximum 5 accounts per user
- Always confirm account type and deposit amount before creating
- Be helpful and explain account features (interest rates, benefits)

For checking accounts:
- 0.01% APY interest rate
- Lower minimum deposit ($25)
- Best for daily transactions

For savings accounts:
- 2.50% APY interest rate
- Higher minimum deposit ($100)
- Best for saving money

Always be professional, clear, and helpful."""

    def run(self, user_message: str, user_id: str, conversation_history: list = None) -> dict:
        """
        Run the account agent with user message
        
        Args:
            user_message: User's message
            user_id: User's ID for account operations
            conversation_history: Previous conversation messages
            
        Returns:
            Dict with response and updated conversation history
        """
        if conversation_history is None:
            conversation_history = []
        
        # Add user message
        conversation_history.append({
            "role": "user",
            "content": user_message
        })
        
        # Keep calling Claude until we get a final response
        while True:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=MAX_TOKENS,
                system=self.system_prompt,
                tools=self.tools,
                messages=conversation_history
            )
            
            # Check stop reason
            if response.stop_reason == "end_turn":
                # Final response
                final_text = ""
                for block in response.content:
                    if hasattr(block, 'text'):
                        final_text += block.text
                
                conversation_history.append({
                    "role": "assistant",
                    "content": response.content
                })
                
                return {
                    "response": final_text,
                    "conversation_history": conversation_history
                }
            
            elif response.stop_reason == "tool_use":
                # Claude wants to use tools
                conversation_history.append({
                    "role": "assistant",
                    "content": response.content
                })
                
                # Execute tools
                tool_results = []
                for block in response.content:
                    if block.type == "tool_use":
                        tool_name = block.name
                        tool_input = block.input
                        
                        # Add user_id to tool input if not present
                        if 'user_id' not in tool_input:
                            tool_input['user_id'] = user_id
                        
                        print(f"🔧 Using tool: {tool_name}")
                        
                        # Execute tool
                        if tool_name in self.tool_functions:
                            result = self.tool_functions[tool_name](**tool_input)
                        else:
                            result = json.dumps({"error": f"Unknown tool: {tool_name}"})
                        
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": result
                        })
                
                # Add tool results to conversation
                conversation_history.append({
                    "role": "user",
                    "content": tool_results
                })
                
                # Continue loop - Claude will process results
            else:
                # Unexpected stop reason
                return {
                    "response": "I encountered an issue. Please try again.",
                    "conversation_history": conversation_history
                }


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":
    print("🧪 Testing Account Agent...\n")
    
    # Need a real user_id - use one from your Firebase tests
    test_user_id = "test-user-123"  # Replace with real user_id
    
    agent = AccountAgent()
    
    # Test 1: Ask about accounts
    print("1️⃣  User: What accounts can I create?")
    result = agent.run("What types of accounts can I create?", test_user_id)
    print(f"   Agent: {result['response']}\n")
    
    # Test 2: Create account (will fail without real user_id)
    print("2️⃣  User: I want to open a savings account")
    result = agent.run("I want to open a savings account with $500", test_user_id, result['conversation_history'])
    print(f"   Agent: {result['response']}\n")
    
    print("✅ Account agent test complete!")