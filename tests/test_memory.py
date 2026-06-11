import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from memory.chat_memory import ChatMemory

def test_memory():
    memory = ChatMemory("test_session")
    
    memory.add_message("user", "Tell me about Sigiriya")
    memory.add_message("assistant", "Sigiriya is an ancient rock fortress...")
    
    recent = memory.get_recent_messages(2)
    print(f"Recent messages: {len(recent)}")
    
    last_user = memory.get_last_user_query()
    print(f"Last user query: {last_user}")
    
    summary = memory.get_conversation_summary()
    print(f"Summary: {summary[:100]}...")

if __name__ == "__main__":
    test_memory()