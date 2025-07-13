import streamlit as st
import warnings
import os
import sys
from datetime import datetime
from pathlib import Path
import time
import base64

warnings.filterwarnings('ignore')

try:
    from crewai import Crew, LLM
    from trip_agents import TripAgents
    from trip_tasks import TripTasks
    from dotenv import load_dotenv
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib.colors import HexColor
except ImportError as e:
    st.error(f"❌ Missing required packages: {e}")
    st.error("Please install: pip install crewai streamlit python-dotenv reportlab")
    st.stop()

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="AI Trip Planner",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(90deg, #FF6B6B 0%, #4ECDC4 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .trip-container {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #FF6B6B;
        margin: 1rem 0;
    }
    .success-message {
        background: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 5px;
        border-left: 4px solid #28a745;
        margin: 1rem 0;
    }
    .info-box {
        background: #e3f2fd;
        padding: 1rem;
        border-radius: 5px;
        border-left: 4px solid #2196f3;
        margin: 1rem 0;
    }
    .stButton > button {
        width: 100%;
        background: linear-gradient(90deg, #FF6B6B 0%, #4ECDC4 100%);
        color: white;
        border: none;
        border-radius: 5px;
        padding: 0.5rem 1rem;
        font-weight: bold;
    }
    .input-section {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)


class TripCrew:
    def __init__(self, origin, cities, date_range, interests):
        self.origin = origin
        self.cities = cities
        self.date_range = date_range
        self.interests = interests

    def run(self):
        # Get the API key
        OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')

        if not OPENROUTER_API_KEY:
            raise ValueError("OPENROUTER_API_KEY not found in environment variables")

        agents = TripAgents()
        tasks = TripTasks()

        # Create LLM instance
        llm = LLM(
            model="openrouter/deepseek/deepseek-r1-0528:free",
            base_url="https://openrouter.ai/api/v1",
            api_key=OPENROUTER_API_KEY
        )

        # Create agents with custom LLM
        city_selector_agent = agents.city_selection_agent(llm=llm)
        local_expert_agent = agents.local_expert(llm=llm)
        travel_concierge_agent = agents.travel_concierge(llm=llm)

        # Create tasks
        identify_task = tasks.identify_task(
            city_selector_agent, self.origin, self.cities,
            self.interests, self.date_range
        )
        gather_task = tasks.gather_task(
            local_expert_agent, self.origin, self.interests, self.date_range
        )
        plan_task = tasks.plan_task(
            travel_concierge_agent, self.origin, self.interests, self.date_range
        )

        # Assemble crew
        crew = Crew(
            agents=[city_selector_agent, local_expert_agent, travel_concierge_agent],
            tasks=[identify_task, gather_task, plan_task],
            verbose=True
        )

        result = crew.kickoff()

        return result


class StreamlitTripPlanner:
    def __init__(self):
        self.output_dir = Path("trip_plans")
        self.output_dir.mkdir(exist_ok=True)

    def create_pdf_plan(self, content, origin, cities, date_range):
        """Generate PDF trip plan with professional formatting"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"trip_plan_{origin.replace(' ', '_')}_to_{cities.replace(' ', '_')}_{timestamp}.pdf"
            filepath = self.output_dir / filename

            # Create PDF document
            doc = SimpleDocTemplate(
                str(filepath),
                pagesize=A4,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=18
            )

            # Define styles
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                textColor=HexColor('#FF6B6B'),
                spaceAfter=30,
                alignment=1
            )

            subtitle_style = ParagraphStyle(
                'CustomSubtitle',
                parent=styles['Normal'],
                fontSize=12,
                textColor=HexColor('#666666'),
                spaceAfter=20,
                alignment=1
            )

            body_style = ParagraphStyle(
                'CustomBody',
                parent=styles['Normal'],
                fontSize=11,
                leading=14,
                spaceAfter=12,
                textColor=HexColor('#333333')
            )

            # Build PDF content
            story = []
            story.append(Paragraph("✈️ Your AI-Generated Trip Plan", title_style))
            story.append(Paragraph(f"From: {origin} | To: {cities}", subtitle_style))
            story.append(Paragraph(f"Travel Dates: {date_range}", subtitle_style))
            story.append(Paragraph(f"Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", subtitle_style))
            story.append(Spacer(1, 0.5 * inch))

            # Content
            paragraphs = content.split('\n\n')
            for para in paragraphs:
                if para.strip():
                    story.append(Paragraph(para.strip(), body_style))
                    story.append(Spacer(1, 0.1 * inch))

            # Build PDF
            doc.build(story)
            return str(filepath)

        except Exception as e:
            st.error(f"Error creating PDF: {str(e)}")
            return None


def extract_trip_content(crew_output):
    """Extract string content from CrewOutput object"""
    if hasattr(crew_output, 'raw'):
        return str(crew_output.raw)
    elif hasattr(crew_output, 'result'):
        return str(crew_output.result)
    elif hasattr(crew_output, 'output'):
        return str(crew_output.output)
    else:
        return str(crew_output)


def main():
    planner = StreamlitTripPlanner()

    # Header
    st.markdown("""
    <div class="main-header">
        <h1>✈️ AI Trip Planner</h1>
        <p>Your personal AI travel assistant powered by CrewAI</p>
    </div>
    """, unsafe_allow_html=True)

    # Check for API key
    if not os.getenv('OPENROUTER_API_KEY'):
        st.error("❌ OPENROUTER_API_KEY not found in environment variables!")
        st.info("Please add your OpenRouter API key to the .env file")
        st.stop()

    # Sidebar for settings and info
    with st.sidebar:
        st.header("⚙️ Settings")

        # Options
        st.subheader("📋 Options")
        auto_pdf = st.checkbox("🔄 Auto-generate PDF", value=True)
        show_progress = st.checkbox("👁️ Show detailed progress", value=True)

        # Info section
        st.markdown("---")
        st.subheader("ℹ️ How it works")
        st.markdown("""
        Our AI agents work together to:
        - 🏙️ **City Selector**: Analyzes and recommends the best cities
        - 🗺️ **Local Expert**: Provides insider knowledge and tips
        - 🎯 **Travel Concierge**: Creates your personalized itinerary
        """)

        # Statistics
        if st.session_state.get('trips_planned', 0) > 0:
            st.metric("🗺️ Trips Planned", st.session_state.trips_planned)

    # Main content area
    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown('<div class="input-section">', unsafe_allow_html=True)
        st.subheader("🎯 Plan Your Perfect Trip")

        # Input fields
        origin = st.text_input(
            "🏠 Where will you be traveling from?",
            placeholder="e.g., New York, NY",
            help="Enter your departure city or location"
        )

        cities = st.text_input(
            "🏙️ What cities are you considering?",
            placeholder="e.g., Paris, Rome, Barcelona",
            help="Enter multiple cities separated by commas"
        )

        date_range = st.text_input(
            "📅 What is your preferred date range?",
            placeholder="e.g., March 15-25, 2024 or 10 days in April",
            help="Enter your travel dates or duration"
        )

        interests = st.text_area(
            "🎨 What are your main interests and hobbies?",
            placeholder="e.g., photography, museums, local cuisine, nightlife, hiking",
            help="Tell us what you enjoy doing while traveling",
            height=100
        )

        st.markdown('</div>', unsafe_allow_html=True)

        # Generate button
        if st.button("🚀 Generate My Trip Plan", disabled=not all([origin, cities, date_range, interests])):
            if not all([origin.strip(), cities.strip(), date_range.strip(), interests.strip()]):
                st.error("Please fill in all the fields!")
                return

            # Initialize progress tracking
            progress_bar = st.progress(0)
            status_text = st.empty()

            try:
                # Step 1: Initialize
                if show_progress:
                    status_text.text("🔧 Initializing AI travel agents...")
                    progress_bar.progress(20)
                    time.sleep(0.5)

                trip_crew = TripCrew(origin, cities, date_range, interests)

                # Step 2: Generate trip plan
                if show_progress:
                    status_text.text("🤖 AI agents are planning your trip...")
                    progress_bar.progress(50)

                with st.spinner("Our AI agents are working on your perfect trip..."):
                    result = trip_crew.run()

                if show_progress:
                    status_text.text("✅ Trip planning completed!")
                    progress_bar.progress(80)

                # Extract string content from CrewOutput
                trip_content = extract_trip_content(result)

                # Store in session state
                st.session_state.last_trip = trip_content
                st.session_state.last_origin = origin
                st.session_state.last_cities = cities
                st.session_state.last_date_range = date_range
                st.session_state.last_interests = interests
                st.session_state.trips_planned = st.session_state.get('trips_planned', 0) + 1

                # Step 3: Generate PDF if requested
                pdf_path = None
                if auto_pdf:
                    if show_progress:
                        status_text.text("📄 Generating PDF trip plan...")
                        progress_bar.progress(90)

                    pdf_path = planner.create_pdf_plan(trip_content, origin, cities, date_range)
                    st.session_state.last_pdf_path = pdf_path

                if show_progress:
                    status_text.text("🎉 Your trip plan is ready!")
                    progress_bar.progress(100)
                    time.sleep(1)
                    status_text.empty()
                    progress_bar.empty()

                # Success message
                st.markdown("""
                <div class="success-message">
                    <strong>✅ Success!</strong> Your personalized trip plan has been generated successfully.
                </div>
                """, unsafe_allow_html=True)

            except Exception as e:
                st.error(f"❌ Error generating trip plan: {str(e)}")
                progress_bar.empty()
                status_text.empty()

    with col2:
        # Quick actions
        st.subheader("🎯 Quick Actions")

        if st.session_state.get('last_trip'):
            if st.button("📄 Generate PDF"):
                with st.spinner("Creating PDF..."):
                    pdf_path = planner.create_pdf_plan(
                        st.session_state.last_trip,
                        st.session_state.last_origin,
                        st.session_state.last_cities,
                        st.session_state.last_date_range
                    )
                    if pdf_path:
                        st.session_state.last_pdf_path = pdf_path
                        st.success("PDF generated successfully!")

            if st.button("🔄 Plan New Trip"):
                for key in ['last_trip', 'last_origin', 'last_cities', 'last_date_range', 'last_interests',
                            'last_pdf_path']:
                    st.session_state.pop(key, None)
                st.rerun()

        # Popular destinations
        st.subheader("🌍 Popular Destinations")
        popular_trips = [
            {"origin": "New York", "cities": "Paris, London, Amsterdam", "interests": "museums, culture, history"},
            {"origin": "Los Angeles", "cities": "Tokyo, Seoul, Bangkok", "interests": "food, nightlife, shopping"},
            {"origin": "Chicago", "cities": "Rome, Florence, Venice", "interests": "art, architecture, cuisine"},
            {"origin": "Miami", "cities": "Barcelona, Madrid, Lisbon", "interests": "beaches, culture, music"},
        ]

        for i, trip in enumerate(popular_trips):
            if st.button(f"📍 {trip['origin']} → {trip['cities']}", key=f"popular_{i}"):
                st.session_state.sample_trip = trip
                st.rerun()

    # Display results
    if st.session_state.get('last_trip'):
        st.markdown("---")
        st.subheader("🗺️ Your Personalized Trip Plan")

        # Trip metadata
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("🏠 From", st.session_state.last_origin)
        with col2:
            st.metric("🏙️ To", st.session_state.last_cities)
        with col3:
            st.metric("📅 When", st.session_state.last_date_range)
        with col4:
            st.metric("📏 Length", f"{len(st.session_state.last_trip.split())} words")

        # Trip content
        st.markdown("""
        <div class="trip-container">
        """, unsafe_allow_html=True)

        st.markdown(st.session_state.last_trip)

        st.markdown("</div>", unsafe_allow_html=True)

        # PDF download link
        if st.session_state.get('last_pdf_path'):
            st.markdown("---")
            st.subheader("📄 Download Your Trip Plan")

            # Create download button
            with open(st.session_state.last_pdf_path, "rb") as pdf_file:
                pdf_bytes = pdf_file.read()

            st.download_button(
                label="📄 Download PDF Trip Plan",
                data=pdf_bytes,
                file_name=f"trip_plan_{st.session_state.last_origin}_{st.session_state.last_cities}.pdf",
                mime="application/pdf",
                use_container_width=True
            )

            st.info(f"📁 PDF saved locally at: {st.session_state.last_pdf_path}")

    # Handle sample trip selection
    if st.session_state.get('sample_trip'):
        trip = st.session_state.sample_trip
        st.session_state.sample_trip = None
        st.rerun()

    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 1rem;">
        <p>✈️ AI Trip Planner | Powered by CrewAI & OpenRouter</p>
        <p>🤖 Your personal travel agents working 24/7 to plan your perfect trip</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()