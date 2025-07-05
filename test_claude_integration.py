#!/usr/bin/env python3
"""
Simple test script to verify Claude 3 Haiku integration
"""

import os
from dotenv import load_dotenv
from anthropic import Anthropic

# Load environment variables
load_dotenv()

def test_claude_integration():
    """Test the Claude 3 Haiku integration"""
    
    # Check if API key is set
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("❌ ANTHROPIC_API_KEY not found in environment variables")
        print("Please set your Anthropic API key in a .env file or environment variable")
        return False
    
    try:
        # Initialize Anthropic client
        client = Anthropic(api_key=api_key)
        
        # Test message
        test_prompt = "Hello! Can you help me with a simple question about relationships?"
        
        print("🤖 Testing Claude 3 Haiku integration...")
        
        response = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=100,
            messages=[
                {
                    "role": "user",
                    "content": test_prompt
                }
            ]
        )
        
        if response.content and len(response.content) > 0:
            content = response.content[0]
            if hasattr(content, 'text'):
                print("✅ Claude 3 Haiku integration successful!")
                print(f"Response: {content.text[:100]}...")
                return True
            else:
                print(f"⚠️  Unexpected response format: {type(content)}")
                return False
        else:
            print("❌ Empty response received")
            return False
            
    except Exception as e:
        print(f"❌ Error testing Claude integration: {e}")
        return False

if __name__ == "__main__":
    test_claude_integration() 