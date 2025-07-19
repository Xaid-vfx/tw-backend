#!/usr/bin/env python3
"""
Interactive Chat Simulator for Couples Therapy AI
Simulates a real chat environment by calling the send_message endpoint in a loop
"""

import requests
import json
import time
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class ChatSimulator:
    def __init__(self, base_url="http://localhost:8000", couple_id=2):
        self.base_url = base_url
        self.couple_id = couple_id
        self.endpoint = f"{base_url}/couples/{couple_id}/messages"
        self.session = requests.Session()
        self.chat_history = []
        self.current_partner = "A"  # Default to Partner A
        
    def print_header(self):
        """Print chat header"""
        print("=" * 60)
        print("🤖 COUPLES THERAPY AI CHAT SIMULATOR")
        print("=" * 60)
        print(f"Couple ID: {self.couple_id}")
        print(f"Endpoint: {self.endpoint}")
        print(f"Current Partner: {self.current_partner}")
        print("Type 'quit', 'exit', or 'bye' to end the chat")
        print("Type 'history' to see chat history")
        print("Type 'clear' to clear chat history")
        print("Type 'partner A' or 'partner B' to switch partners")
        print("=" * 60)
        print()
    
    def send_message(self, message, sender_id="user"):
        """Send a message to the AI endpoint"""
        try:
            payload = {
                "message": message,
                "sender_id": sender_id,
                "partner": self.current_partner
            }
            
            print(f"📤 Sending (Partner {self.current_partner}): {message[:50]}{'...' if len(message) > 50 else ''}")
            
            response = self.session.post(
                self.endpoint,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                ai_response = result.get('ai_response', 'No response received')
                memories_used = result.get('memories_used', 0)
                
                # Store in chat history
                chat_entry = {
                    "timestamp": datetime.now().strftime("%H:%M:%S"),
                    "partner": self.current_partner,
                    "user_message": message,
                    "ai_response": ai_response,
                    "memories_used": memories_used
                }
                self.chat_history.append(chat_entry)
                
                return ai_response, memories_used
            else:
                error_msg = f"❌ Error {response.status_code}: {response.text}"
                print(error_msg)
                return error_msg, 0
                
        except requests.exceptions.ConnectionError:
            error_msg = "❌ Could not connect to server. Make sure the FastAPI server is running: uvicorn app.main:app --reload"
            print(error_msg)
            return error_msg, 0
        except Exception as e:
            error_msg = f"❌ Unexpected error: {e}"
            print(error_msg)
            return error_msg, 0
    
    def display_ai_response(self, response, memories_used):
        """Display AI response in a formatted way"""
        print()
        print("🤖 AI Assistant:")
        print("-" * 40)
        print(response)
        print("-" * 40)
        print(f"💾 Memories used: {memories_used}")
        print()
    
    def show_chat_history(self):
        """Display chat history"""
        if not self.chat_history:
            print("📝 No chat history yet.")
            return
        
        print("\n📝 CHAT HISTORY:")
        print("=" * 60)
        for i, entry in enumerate(self.chat_history, 1):
            print(f"\n{i}. [{entry['timestamp']}] (Partner {entry['partner']})")
            print(f"   👤 You: {entry['user_message'][:100]}{'...' if len(entry['user_message']) > 100 else ''}")
            print(f"   🤖 AI: {entry['ai_response'][:100]}{'...' if len(entry['ai_response']) > 100 else ''}")
            print(f"   💾 Memories: {entry['memories_used']}")
        print("=" * 60)
    
    def clear_history(self):
        """Clear chat history"""
        self.chat_history.clear()
        print("🗑️  Chat history cleared!")
    
    def run(self):
        """Main chat loop"""
        self.print_header()
        
        # Check if server is running
        try:
            response = self.session.get(f"{self.base_url}/docs", timeout=5)
            if response.status_code != 200:
                print("⚠️  Server might not be running properly")
        except:
            print("⚠️  Could not connect to server. Make sure it's running with: uvicorn app.main:app --reload")
        
        print("💬 Start chatting with the AI assistant...\n")
        
        while True:
            try:
                # Get user input
                user_input = input(f"👤 Partner {self.current_partner}: ").strip()
                
                # Handle special commands
                if user_input.lower() in ['quit', 'exit', 'bye']:
                    print("\n👋 Goodbye! Thanks for chatting!")
                    break
                elif user_input.lower() == 'history':
                    self.show_chat_history()
                    continue
                elif user_input.lower() == 'clear':
                    self.clear_history()
                    continue
                elif user_input.lower().startswith('partner '):
                    partner = user_input.split()[1].upper()
                    if partner in ['A', 'B']:
                        self.current_partner = partner
                        print(f"🔄 Switched to Partner {self.current_partner}")
                    else:
                        print("❌ Invalid partner. Use 'partner A' or 'partner B'")
                    continue
                elif not user_input:
                    print("Please enter a message or command.")
                    continue
                
                # Send message to AI
                ai_response, memories_used = self.send_message(user_input)
                self.display_ai_response(ai_response, memories_used)
                
            except KeyboardInterrupt:
                print("\n\n👋 Chat interrupted. Goodbye!")
                break
            except EOFError:
                print("\n\n👋 End of input. Goodbye!")
                break

def main():
    """Main function"""
    print("🚀 Starting Couples Therapy AI Chat Simulator...")
    
    # Configuration
    base_url = os.getenv("API_BASE_URL", "http://localhost:8000")
    couple_id = int(os.getenv("COUPLE_ID", "2"))
    
    # Create and run simulator
    simulator = ChatSimulator(base_url=base_url, couple_id=couple_id)
    simulator.run()

if __name__ == "__main__":
    main() 