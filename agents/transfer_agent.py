"""
Transfer Agent V2 - Smart Transfer
Supports both internal (between own accounts) and external (to friends)
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from anthropic import Anthropic
from config import ANTHROPIC_API_KEY, CLAUDE_MODEL, MAX_TOKENS
from tools.transfer_tools_v2 import external_transfer, internal_transfer
import json


class TransferAgent:
    """Agent specialized in money transfers"""
    
    def __init__(self):
        self.client = Anthropic(api_key=ANTHROPIC_API_KEY)
        self.model = CLAUDE_MODEL
        
        # Two types of transfers
        self.tools = [
            {
                "name": "external_transfer",
                "description": "Transfer money to another person's account using their account ID. Auto-detects recipient name for confirmation.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "user_id": {"type": "string", "description": "Sender's user ID"},
                        "from_account_type": {
                            "type": "string",
                            "enum": ["checking", "savings"],
                            "description": "Your account type to send FROM (checking or savings)"
                        },
                        "to_account_id": {
                            "type": "string",
                            "description": "Recipient's full account ID (the long ID they gave you)"
                        },
                        "amount": {"type": "number", "description": "Amount to send in USD"},
                        "memo": {"type": "string", "description": "Optional note"}
                    },
                    "required": ["user_id", "from_account_type", "to_account_id", "amount"]
                }
            },
            {
                "name": "internal_transfer",
                "description": "Transfer between your own accounts (checking to savings or vice versa)",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "user_id": {"type": "string", "description": "User's ID"},
                        "from_account_type": {
                            "type": "string",
                            "enum": ["checking", "savings"],
                            "description": "Account type to transfer FROM"
                        },
                        "to_account_type": {
                            "type": "string",
                            "enum": ["checking", "savings"],
                            "description": "Account type to transfer TO"
                        },
                        "amount": {"type": "number", "description": "Amount to transfer"},
                        "memo": {"type": "string", "description": "Optional note"}
                    },
                    "required": ["user_id", "from_account_type", "to_account_type", "amount"]
                }
            }
        ]
        
        self.tool_functions = {
            "external_transfer": external_transfer,
            "internal_transfer": internal_transfer
        }
        
        self.system_prompt = """You are a smart banking transfer agent. Handle TWO types of transfers:

🔹 INTERNAL TRANSFER (between user's own accounts):
Ask: FROM (checking/savings) → TO (checking/savings) → Amount
Example: "Transfer $50 from my checking to my savings"

🔹 EXTERNAL TRANSFER (to another person):
Ask: FROM (checking/savings) → TO (account ID) → Amount
When user provides account ID, YOU WILL automatically show recipient's name for confirmation!
Example: "Send $100 to account abc-123"

IMPORTANT RULES:
1. If user says "to my friend" or "to someone" or provides an ACCOUNT ID → Use external_transfer
2. If user says "between my accounts" or "to my savings" → Use internal_transfer
3. ALWAYS show recipient name BEFORE confirming external transfers
4. DO NOT ask for verification, user IDs, or complex confirmations

WORKFLOW for EXTERNAL:
User: "Send $50 to account xyz-789"
You: [Call external_transfer - it will show recipient name]
Tool returns: "Sending to John Smith's CHECKING account"
You: "I'm about to send $50 to John Smith's checking account. Confirm?"
User: "Yes"
You: [Transfer completes] "✅ Sent $50 to John Smith!"

WORKFLOW for INTERNAL:
User: "Move $100 from checking to savings"
You: [Call internal_transfer immediately - all info present!]

Be smart, friendly, and secure!"""

    def run(self, user_message: str, user_id: str, conversation_history: list = None) -> dict:
        """Run the transfer agent"""
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
                        
                        if tool_name == "external_transfer":
                            print(f"💸 External Transfer: ${tool_input.get('amount')} to {tool_input.get('to_account_id')[:8]}...")
                        else:
                            print(f"🔄 Internal Transfer: {tool_input.get('from_account_type')} → {tool_input.get('to_account_type')}")
                        
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
    print("🧪 Testing Smart Transfer Agent...\n")
    agent = TransferAgent()
    print("✅ Smart transfer agent with external support loaded!")