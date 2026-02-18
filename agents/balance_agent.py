"""
Balance Agent V2 - Simplified
Automatically shows all balances without asking
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from anthropic import Anthropic
from config import ANTHROPIC_API_KEY, CLAUDE_MODEL, MAX_TOKENS
from tools.balance_tools import get_total_balance
import json


class BalanceAgent:
    """Agent specialized in balance inquiries - simplified"""
    
    def __init__(self):
        self.client = Anthropic(api_key=ANTHROPIC_API_KEY)
        self.model = CLAUDE_MODEL
        
        # Only one tool - show ALL balances automatically
        self.tools = [
            {
                "name": "get_total_balance",
                "description": "Get total balance across all user's accounts with breakdown. NO verification needed - just show it!",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "user_id": {"type": "string", "description": "User's unique ID"}
                    },
                    "required": ["user_id"]
                }
            }
        ]
        
        self.tool_functions = {
            "get_total_balance": get_total_balance
        }
        
        self.system_prompt = """You are a balance inquiry agent. Make it SIMPLE and INSTANT.

IMPORTANT RULE:
When user asks about balance - IMMEDIATELY show ALL their accounts. 
DO NOT ask for:
❌ Account IDs
❌ Which account they want
❌ Any verification

Just call get_total_balance tool RIGHT AWAY and show:
✅ All accounts with balances
✅ Account types (CHECKING, SAVINGS)
✅ Total across all accounts
✅ Interest rates

Examples:
User: "What's my balance?"
You: [Call get_total_balance IMMEDIATELY]

User: "Show me my money"  
You: [Call get_total_balance IMMEDIATELY]

User: "How much do I have?"
You: [Call get_total_balance IMMEDIATELY]

Be fast and helpful!"""

    def run(self, user_message: str, user_id: str, conversation_history: list = None) -> dict:
        """Run the balance agent"""
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
                        
                        print(f"🔧 Getting all balances...")
                        
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
    print("🧪 Testing Auto Balance Agent...\n")
    agent = BalanceAgent()
    print("✅ Auto balance agent loaded!")