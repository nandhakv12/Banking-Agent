"""
Supervisor Agent
Routes user requests to the appropriate specialized agent
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from anthropic import Anthropic
from config import ANTHROPIC_API_KEY, CLAUDE_MODEL, MAX_TOKENS
from agents.account_agent import AccountAgent
from agents.balance_agent import BalanceAgent
from agents.transfer_agent import TransferAgent
from agents.transaction_agent import TransactionAgent


class SupervisorAgent:
    """Supervisor agent that routes requests to specialized agents"""
    
    def __init__(self):
        self.client = Anthropic(api_key=ANTHROPIC_API_KEY)
        self.model = CLAUDE_MODEL
        
        # Initialize specialized agents
        self.account_agent = AccountAgent()
        self.balance_agent = BalanceAgent()
        self.transfer_agent = TransferAgent()
        self.transaction_agent = TransactionAgent()
        
        # Routing tools - CORRECT FORMAT
        self.routing_tools = [
            {
                "name": "route_to_account_agent",
                "description": "Route to account agent for creating new accounts or viewing account information",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "user_message": {
                            "type": "string",
                            "description": "The user's message to pass to the account agent"
                        }
                    },
                    "required": ["user_message"]
                }
            },
            {
                "name": "route_to_balance_agent",
                "description": "Route to balance agent for checking balances or account summaries",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "user_message": {
                            "type": "string",
                            "description": "The user's message to pass to the balance agent"
                        }
                    },
                    "required": ["user_message"]
                }
            },
            {
                "name": "route_to_transfer_agent",
                "description": "Route to transfer agent for moving money between accounts",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "user_message": {
                            "type": "string",
                            "description": "The user's message to pass to the transfer agent"
                        }
                    },
                    "required": ["user_message"]
                }
            },
            {
                "name": "route_to_transaction_agent",
                "description": "Route to transaction agent for viewing transaction history",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "user_message": {
                            "type": "string",
                            "description": "The user's message to pass to the transaction agent"
                        }
                    },
                    "required": ["user_message"]
                }
            },
            {
                "name": "respond_directly",
                "description": "Respond directly without routing (greetings, general questions)",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "response": {
                            "type": "string",
                            "description": "Direct response to give the user"
                        }
                    },
                    "required": ["response"]
                }
            }
        ]
        
        self.system_prompt = """You are a banking supervisor that routes customer requests.

Specialized agents:
- Account Agent: Creates accounts, shows account info
- Balance Agent: Checks balances, summaries
- Transfer Agent: Transfers money
- Transaction Agent: Shows history

Route based on intent:
- Create/open account → route_to_account_agent
- Check balance → route_to_balance_agent  
- Transfer money → route_to_transfer_agent
- View transactions → route_to_transaction_agent
- Greetings/general → respond_directly"""

    def chat(self, user_message: str, user_id: str, conversation_history: list = None) -> dict:
        """
        Main chat interface - routes to appropriate agent
        
        Args:
            user_message: User's message
            user_id: User's unique ID from login
            conversation_history: Previous conversation
            
        Returns:
            Dict with response and updated history
        """
        if conversation_history is None:
            conversation_history = []
        
        # DEBUG: Print user_id
        print(f"🔑 Supervisor received user_id: {user_id}")
        
        # Add user message
        conversation_history.append({
            "role": "user",
            "content": user_message
        })
        
        # Ask supervisor to route
        response = self.client.messages.create(
            model=self.model,
            max_tokens=MAX_TOKENS,
            system=self.system_prompt,
            tools=self.routing_tools,
            messages=conversation_history
        )
        
        # Process routing decision
        final_response = ""
        
        for block in response.content:
            if block.type == "tool_use":
                tool_name = block.name
                tool_input = block.input
                
                print(f"📍 Supervisor routing to: {tool_name}")
                
                if tool_name == "route_to_account_agent":
                    print(f"   Passing user_id: {user_id}")
                    result = self.account_agent.run(
                        tool_input["user_message"],
                        user_id  # ← CORRECT: Pass real user_id
                    )
                    final_response = result["response"]
                    conversation_history = result["conversation_history"]
                
                elif tool_name == "route_to_balance_agent":
                    print(f"   Passing user_id: {user_id}")
                    result = self.balance_agent.run(
                        tool_input["user_message"],
                        user_id  # ← CORRECT: Pass real user_id
                    )
                    final_response = result["response"]
                    conversation_history = result["conversation_history"]
                
                elif tool_name == "route_to_transfer_agent":
                    print(f"   Passing user_id: {user_id}")
                    result = self.transfer_agent.run(
                        tool_input["user_message"],
                        user_id  # ← CORRECT: Pass real user_id
                    )
                    final_response = result["response"]
                    conversation_history = result["conversation_history"]
                
                elif tool_name == "route_to_transaction_agent":
                    print(f"   Passing user_id: {user_id}")
                    result = self.transaction_agent.run(
                        tool_input["user_message"],
                        user_id  # ← CORRECT: Pass real user_id
                    )
                    final_response = result["response"]
                    conversation_history = result["conversation_history"]
                
                elif tool_name == "respond_directly":
                    final_response = tool_input["response"]
                    conversation_history.append({
                        "role": "assistant",
                        "content": final_response
                    })
            
            elif hasattr(block, 'text'):
                # Fallback - direct response
                final_response += block.text
        
        if not final_response:
            final_response = "I'm here to help! Ask me to open accounts, check balances, transfer money, or view transactions."
            conversation_history.append({
                "role": "assistant",
                "content": final_response
            })
        
        return {
            "response": final_response,
            "conversation_history": conversation_history
        }


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":
    print("🧪 Testing Supervisor Agent...\n")
    
    supervisor = SupervisorAgent()
    test_user_id = "mWlt8jHUOdbO5re9vZxX9RoTIJe2"  # Use a real Firebase UID
    
    # Test 1: Greeting
    print("1️⃣  User: Hello!")
    result = supervisor.chat("Hello!", test_user_id)
    print(f"   Supervisor: {result['response']}\n")
    
    # Test 2: Account question
    print("2️⃣  User: I want to open a savings account")
    result = supervisor.chat("I want to open a savings account", test_user_id, result['conversation_history'])
    print(f"   Supervisor: {result['response']}\n")
    
    # Test 3: Balance question
    print("3️⃣  User: What's my balance?")
    result = supervisor.chat("What's my balance?", test_user_id, result['conversation_history'])
    print(f"   Supervisor: {result['response']}\n")
    
    print("✅ Supervisor agent test complete!")