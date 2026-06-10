import streamlit as st
import requests
import json
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Tourism Chatbot V1 - RAG Assistant",
    page_icon="🏝️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        animation: fadeIn 0.3s ease-in;
    }
    .user-message {
        background-color: #e3f2fd;
        border-left: 4px solid #2196f3;
    }
    .bot-message {
        background-color: #f5f5f5;
        border-left: 4px solid #4caf50;
    }
    .source-card {
        background-color: #fff3e0;
        padding: 0.5rem;
        border-radius: 5px;
        margin: 0.5rem 0;
        font-size: 0.8rem;
        border-left: 3px solid #ff9800;
    }
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .stButton button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.5rem 2rem;
        border-radius: 25px;
    }
    .sidebar-header {
        text-align: center;
        padding: 1rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
        color: white;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "messages_v1" not in st.session_state:
    st.session_state.messages_v1 = []
if "session_id_v1" not in st.session_state:
    st.session_state.session_id_v1 = None

# API configuration
API_URL = "http://localhost:8000/api/v1"

def send_message(message):
    """Send message to V1 API"""
    try:
        response = requests.post(
            f"{API_URL}/chat",
            json={"message": message, "top_k": 5},
            timeout=30
        )
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"API Error: {response.status_code}"}
    except requests.exceptions.ConnectionError:
        return {"error": "Cannot connect to server. Make sure the backend is running on port 8000"}
    except Exception as e:
        return {"error": str(e)}

# Sidebar
with st.sidebar:
    st.markdown('<div class="sidebar-header">', unsafe_allow_html=True)
    st.image("https://cdn-icons-png.flaticon.com/512/1995/1995572.png", width=80)
    st.title("🏝️ Tourism Assistant V1")
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("### 📊 Version Info")
    st.info("""
    **Version 1 - RAG Chatbot**
    - ✅ Knowledge-based responses
    - ✅ Vector search
    - ✅ Gemini/OpenAI integration
    - ❌ No conversation memory
    - ❌ No external APIs
    """)
    
    st.markdown("### 📋 How to Use")
    st.markdown("""
    1. Ask about Sri Lankan tourism
    2. Get information from database
    3. View sources of information
    
    **Example questions:**
    - Tell me about Sigiriya
    - Best hotels in Ella
    - Restaurants in Kandy
    """)
    
    st.markdown("### 🔧 Status")
    if st.button("🔄 Check Connection"):
        try:
            response = requests.get(f"{API_URL}/health", timeout=5)
            if response.status_code == 200:
                st.success("✅ Connected to backend")
            else:
                st.error("❌ Backend not responding")
        except:
            st.error("❌ Cannot connect to backend")
    
    if st.button("🗑️ Clear Conversation"):
        st.session_state.messages_v1 = []
        st.rerun()

# Main header
st.markdown('<div class="main-header">', unsafe_allow_html=True)
st.title("🏝️ Sri Lanka Tourism Assistant")
st.caption("Your AI-powered travel companion - Powered by RAG")
st.markdown('</div>', unsafe_allow_html=True)

# Chat interface
chat_container = st.container()

with chat_container:
    # Display chat history
    for message in st.session_state.messages_v1:
        if message["role"] == "user":
            st.markdown(f"""
            <div class="chat-message user-message">
                <b>👤 You</b><br>
                {message["content"]}
            </div>
            """, unsafe_allow_html=True)
        else:
            # Bot message with sources
            st.markdown(f"""
            <div class="chat-message bot-message">
                <b>🤖 Assistant</b><br>
                {message["content"]}
            </div>
            """, unsafe_allow_html=True)
            
            # Show sources if available
            if message.get("sources"):
                with st.expander("📚 View Sources"):
                    for i, source in enumerate(message["sources"], 1):
                        st.markdown(f"""
                        <div class="source-card">
                            <b>Source {i}:</b> {source.get('category', 'Unknown')}<br>
                            <small>{source.get('content', '')[:150]}...</small><br>
                            <small>Relevance: {source.get('relevance', 0):.2f}</small>
                        </div>
                        """, unsafe_allow_html=True)
    
    # Input area
    st.markdown("---")
    col1, col2 = st.columns([5, 1])
    
    with col1:
        user_input = st.text_input(
            "Type your message here...",
            key="user_input_v1",
            placeholder="Ask me about Sri Lankan tourism..."
        )
    
    with col2:
        send_button = st.button("📤 Send", type="primary", use_container_width=True)
    
    # Process input
    if send_button and user_input:
        # Add user message
        st.session_state.messages_v1.append({"role": "user", "content": user_input})
        
        # Show loading
        with st.spinner("Thinking..."):
            response = send_message(user_input)
        
        if "error" in response:
            error_msg = response["error"]
            st.session_state.messages_v1.append({"role": "assistant", "content": f"❌ {error_msg}"})
        else:
            # Add bot response
            st.session_state.messages_v1.append({
                "role": "assistant",
                "content": response["answer"],
                "sources": response.get("sources", []),
                "confidence": response.get("confidence", 0)
            })
        
        st.rerun()

# Footer
st.markdown("---")
st.markdown(
    "<center><small>Version 1.0 - RAG-based Tourism Assistant | Data from Sri Lanka Tourism Database</small></center>",
    unsafe_allow_html=True
)