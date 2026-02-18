"""
Transaction Agent V2 - Simplified  
Auto-shows recent transactions from most active account
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from anthropic import Anthropic
from config import ANTHROPIC_API_KEY, CLAUDE_MODEL, MAX_TOKENS
from tools.balance_tools import get_total_balance
from tools.transaction_tools import get_transaction_history
import json


class TransactionAgent:
    """Agent specialized in transaction history - simplified"""
    
    def __init__(self):
        self.client = Anthropic(api_key=ANTHROPIC_API_KEY)
        self.model = CLAUDE_MODEL
        
        # Two tools - get accounts, then get transactions
        self.tools = [
            {
                "name": "get_total_balance",
                "description": "Get all user accounts to find which one to show transactions for",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "user_id": {"type": "string", "description": "User's unique ID"}
                    },
                    "required": ["user_id"]
                }
            },
            {
                "name": "get_transaction_history",
                "description": "Get transaction history for an account",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "user_id": {"type": "string", "description": "User's unique ID"},
                        "account_id": {"type": "string", "description": "Account ID"},
                        "limit": {"type": "integer", "description": "Number of transactions"}
                    },
                    "required": ["user_id", "account_id"]
                }
            }
        ]
        
        self.tool_functions = {
            "get_total_balance": get_total_balance,
            "get_transaction_history": get_transaction_history
        }
        
        self.system_prompt = """You are a transaction history agent. Make it SIMPLE and AUTOMATIC.

WORKFLOW:
1. User asks for transactions → Get ALL their accounts first
2. Pick the FIRST account (or the one they specify)
3. Show transactions immediately

DO NOT ask for:
❌ Account IDs
❌ Which account
❌ Verification

Just show the transactions!

If user specifies account type (checking/savings), find that account and show its transactions.

Be fast and helpful!"""

    def run(self, user_message: str, user_id: str, conversation_history: list = None) -> dict:
        """Run the transaction agent"""
        if conversation_history is None:
            conversation_history = []
        
        conversation_history.append({
            "role": "user",
            "content": user_message
        })
        
        while True:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=MAX_TOKENS,
                system=self.system_prompt,
                tools=self.tools,
                messages=conversation_history
            )
            
            if response.stop_reason == "end_turn":
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
                conversation_history.append({
                    "role": "assistant",
                    "content": response.content
                })
                
                tool_results = []
                for block in response.content:
                    if block.type == "tool_use":
                        tool_name = block.name
                        tool_input = block.input
                        
                        if 'user_id' not in tool_input:
                            tool_input['user_id'] = user_id
                        
                        print(f"🔧 Using tool: {tool_name}")
                        
                        if tool_name in self.tool_functions:
                            result = self.tool_functions[tool_name](**tool_input)
                        else:
                            result = json.dumps({"error": f"Unknown tool: {tool_name}"})
                        
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": result
                        })
                
                conversation_history.append({
                    "role": "user",
                    "content": tool_results
                })
            else:
                return {
                    "response": "I encountered an issue. Please try again.",
                    "conversation_history": conversation_history
                }


if __name__ == "__main__":
    print("🧪 Testing Auto Transaction Agent...\n")
    agent = TransactionAgent()
    print("✅ Auto transaction agent loaded!")