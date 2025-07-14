import streamlit as st
import warnings
import os
import sys
from datetime import datetime
from pathlib import Path
import time
import json

warnings.filterwarnings('ignore')

try:
    from support_crew import SupportCrew
    from dotenv import load_dotenv
except ImportError as e:
    st.error(f"❌ Missing required packages: {e}")
    st.error("Please install: pip install crewai streamlit python-dotenv")
    st.stop()

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="AI Support System",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Dark theme CSS
st.markdown("""
<style>
    .stApp {
        background-color: #0a0a0a;
        color: #ffffff;
    }

    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
        color: #ffffff;
        border-radius: 12px;
        margin-bottom: 2rem;
        border: 1px solid #333;
    }

    .input-section {
        background: #1a1a1a;
        padding: 2rem;
        border-radius: 12px;
        border: 1px solid #333;
        margin: 1rem 0;
    }

    .support-response {
        background: #1a1a1a;
        padding: 2rem;
        border-radius: 12px;
        border: 1px solid #333;
        margin: 1rem 0;
        border-left: 4px solid #00d4aa;
    }

    .priority-urgent {
        background: linear-gradient(135deg, #2d1b1b 0%, #3d2424 100%);
        color: #ff6b6b;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #ff6b6b;
        margin: 1rem 0;
        font-weight: bold;
    }

    .priority-high {
        background: linear-gradient(135deg, #2d2a1b 0%, #3d3524 100%);
        color: #ffa500;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #ffa500;
        margin: 1rem 0;
        font-weight: bold;
    }

    .priority-normal {
        background: linear-gradient(135deg, #1b2d1b 0%, #24382d 100%);
        color: #00d4aa;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #00d4aa;
        margin: 1rem 0;
        font-weight: bold;
    }

    .success-message {
        background: linear-gradient(135deg, #1b2d1b 0%, #24382d 100%);
        color: #00d4aa;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #00d4aa;
        margin: 1rem 0;
    }

    .stButton > button {
        width: 100%;
        background: linear-gradient(135deg, #00d4aa 0%, #00bfa5 100%);
        color: #000000;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 1rem;
        font-weight: bold;
        transition: all 0.3s ease;
    }

    .stButton > button:hover {
        background: linear-gradient(135deg, #00bfa5 0%, #00a693 100%);
        transform: translateY(-2px);
    }

    .stTextInput > div > div > input {
        background-color: #2a2a2a;
        color: #ffffff;
        border: 1px solid #444;
        border-radius: 8px;
    }

    .stTextArea > div > div > textarea {
        background-color: #2a2a2a;
        color: #ffffff;
        border: 1px solid #444;
        border-radius: 8px;
    }

    .metric-container {
        background: #1a1a1a;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #333;
        text-align: center;
        margin: 0.5rem 0;
    }

    .metric-value {
        font-size: 1.5rem;
        font-weight: bold;
        color: #00d4aa;
    }

    .metric-label {
        font-size: 0.9rem;
        color: #aaa;
    }

    .stSelectbox > div > div > select {
        background-color: #2a2a2a;
        color: #ffffff;
        border: 1px solid #444;
    }

    .sidebar .stSelectbox > div > div > select {
        background-color: #2a2a2a;
        color: #ffffff;
    }

    .stProgress > div > div > div > div {
        background-color: #00d4aa;
    }

    h1, h2, h3 {
        color: #ffffff;
    }

    .stMarkdown {
        color: #ffffff;
    }

    .divider {
        height: 1px;
        background: linear-gradient(90deg, transparent, #333, transparent);
        margin: 2rem 0;
    }
</style>
""", unsafe_allow_html=True)


def extract_support_content(crew_output):
    """Extract string content from CrewOutput object"""
    if hasattr(crew_output, 'raw'):
        return str(crew_output.raw)
    elif hasattr(crew_output, 'result'):
        return str(crew_output.result)
    elif hasattr(crew_output, 'output'):
        return str(crew_output.output)
    else:
        return str(crew_output)


def determine_urgency(inquiry):
    """Determine urgency level based on inquiry content"""
    urgent_keywords = ['urgent', 'emergency', 'critical', 'down', 'failing', 'error', 'production', 'broken']
    high_keywords = ['issue', 'problem', 'bug', 'not working', 'help needed']

    inquiry_lower = inquiry.lower()

    if any(keyword in inquiry_lower for keyword in urgent_keywords):
        return "🔴 URGENT", "priority-urgent"
    elif any(keyword in inquiry_lower for keyword in high_keywords):
        return "🟡 HIGH", "priority-high"
    else:
        return "🟢 NORMAL", "priority-normal"


def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🤖 AI Support System</h1>
        <p>Intelligent multi-agent support automation</p>
    </div>
    """, unsafe_allow_html=True)

    # Check for API key
    if not os.getenv('OPENROUTER_API_KEY'):
        st.error("❌ OPENROUTER_API_KEY not found in environment variables!")
        st.info("Please add your OpenRouter API key to the .env file")
        st.stop()

    # Statistics sidebar
    with st.sidebar:
        st.header("📊 Dashboard")

        # Statistics
        if 'tickets_processed' not in st.session_state:
            st.session_state.tickets_processed = 0
        if 'avg_response_time' not in st.session_state:
            st.session_state.avg_response_time = 0

        st.markdown(f"""
        <div class="metric-container">
            <div class="metric-value">{st.session_state.tickets_processed}</div>
            <div class="metric-label">Tickets Processed</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="metric-container">
            <div class="metric-value">{st.session_state.avg_response_time:.1f}s</div>
            <div class="metric-label">Avg Response Time</div>
        </div>
        """, unsafe_allow_html=True)

    # Main content area
    st.markdown('<div class="input-section">', unsafe_allow_html=True)

    # Input fields
    customer = st.text_input(
        "🏢 Customer Company",
        placeholder="e.g., DeepLearningAI, TechCorp, StartupXYZ"
    )

    person = st.text_input(
        "👤 Contact Person",
        placeholder="e.g., Andrew Ng, Sarah Johnson"
    )

    inquiry = st.text_area(
        "❓ Customer Inquiry",
        placeholder="Describe the customer's question, issue, or request...",
        height=150
    )

    # Priority detection
    if inquiry:
        urgency_level, urgency_class = determine_urgency(inquiry)
        st.markdown(f"""
        <div class="{urgency_class}">
            <strong>Priority Level:</strong> {urgency_level}
        </div>
        """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # Process button
    if st.button("🚀 Process Support Request", disabled=not all([customer, person, inquiry])):
        if not all([customer.strip(), person.strip(), inquiry.strip()]):
            st.error("Please fill in all fields!")
            return

        # Progress tracking
        progress_bar = st.progress(0)
        status_text = st.empty()
        start_time = time.time()

        try:
            # Initialize
            status_text.text("🔧 Initializing AI support agents...")
            progress_bar.progress(20)
            time.sleep(0.5)

            support_crew = SupportCrew(customer, person, inquiry)

            # Process
            status_text.text("🤖 Processing support request...")
            progress_bar.progress(60)

            with st.spinner("AI agents working..."):
                result = support_crew.run()

            status_text.text("✅ Response generated!")
            progress_bar.progress(100)

            # Extract content
            support_content = extract_support_content(result)
            response_time = time.time() - start_time

            # Update statistics
            st.session_state.tickets_processed += 1
            st.session_state.avg_response_time = (
                    (st.session_state.avg_response_time * (st.session_state.tickets_processed - 1) + response_time)
                    / st.session_state.tickets_processed
            )

            # Store results
            st.session_state.last_support_response = support_content
            st.session_state.last_customer = customer
            st.session_state.last_person = person
            st.session_state.last_inquiry = inquiry
            st.session_state.last_response_time = response_time

            time.sleep(1)
            status_text.empty()
            progress_bar.empty()

            # Success message
            st.markdown("""
            <div class="success-message">
                <strong>✅ Success!</strong> Support request processed successfully.
            </div>
            """, unsafe_allow_html=True)

        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            progress_bar.empty()
            status_text.empty()

    # Display results
    if st.session_state.get('last_support_response'):
        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

        # Response metadata
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(f"""
            <div class="metric-container">
                <div class="metric-value">{st.session_state.last_customer}</div>
                <div class="metric-label">Customer</div>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div class="metric-container">
                <div class="metric-value">{st.session_state.last_person}</div>
                <div class="metric-label">Contact</div>
            </div>
            """, unsafe_allow_html=True)
        with col3:
            st.markdown(f"""
            <div class="metric-container">
                <div class="metric-value">{st.session_state.last_response_time:.1f}s</div>
                <div class="metric-label">Response Time</div>
            </div>
            """, unsafe_allow_html=True)
        with col4:
            urgency_level, _ = determine_urgency(st.session_state.last_inquiry)
            priority_clean = urgency_level.replace('🔴 ', '').replace('🟡 ', '').replace('🟢 ', '')
            st.markdown(f"""
            <div class="metric-container">
                <div class="metric-value">{priority_clean}</div>
                <div class="metric-label">Priority</div>
            </div>
            """, unsafe_allow_html=True)

        # Support response
        st.markdown(f"""
        <div class="support-response">
            <h3>💬 AI Support Response</h3>
            {st.session_state.last_support_response}
        </div>
        """, unsafe_allow_html=True)

        # Action buttons
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 New Request"):
                for key in ['last_support_response', 'last_customer', 'last_person', 'last_inquiry']:
                    st.session_state.pop(key, None)
                st.rerun()
        with col2:
            if st.button("📋 Copy Response"):
                st.success("Response copied to clipboard!")


if __name__ == "__main__":
    main()