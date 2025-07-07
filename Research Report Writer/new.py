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
    from crewai import Crew
    from report_crew import ReportCrew
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib.colors import HexColor
except ImportError as e:
    st.error(f"❌ Missing required packages: {e}")
    st.error("Please install: pip install reportlab streamlit crewai")
    st.stop()

# Page configuration
st.set_page_config(
    page_title="Research Report Generator",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .report-container {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #667eea;
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
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 5px;
        padding: 0.5rem 1rem;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)


class StreamlitReportGenerator:
    def __init__(self):
        self.output_dir = Path("reports")
        self.output_dir.mkdir(exist_ok=True)

    def create_pdf_report(self, content, topic):
        """Generate PDF report with professional formatting"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"research_report_{topic.replace(' ', '_')}_{timestamp}.pdf"
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
                textColor=HexColor('#2E86AB'),
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
            story.append(Paragraph("Research Report", title_style))
            story.append(Paragraph(f"Topic: {topic}", subtitle_style))
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

    def get_pdf_download_link(self, pdf_path, filename):
        """Generate download link for PDF"""
        try:
            with open(pdf_path, "rb") as f:
                pdf_data = f.read()
            b64_pdf = base64.b64encode(pdf_data).decode()
            return f'<a href="data:application/pdf;base64,{b64_pdf}" download="{filename}" class="download-link">📄 Download PDF Report</a>'
        except Exception as e:
            st.error(f"Error creating download link: {str(e)}")
            return None


def extract_report_content(crew_output):
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
    generator = StreamlitReportGenerator()

    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🔬 Research Report Generator</h1>
        <p>Generate comprehensive research reports with AI-powered analysis</p>
    </div>
    """, unsafe_allow_html=True)

    # Sidebar for settings and info
    with st.sidebar:
        st.header("⚙️ Settings")

        # Topic input
        topic = st.text_input(
            "📝 Research Topic",
            placeholder="Enter your research topic here...",
            help="Provide a clear, specific topic for research"
        )

        # Options
        st.subheader("📋 Options")
        auto_pdf = st.checkbox("🔄 Auto-generate PDF", value=True)
        show_progress = st.checkbox("👁️ Show detailed progress", value=True)

        # Info section
        st.markdown("---")
        st.subheader("ℹ️ About")
        st.markdown("""
        This tool uses AI agents to:
        - 🔍 Research your topic
        - 📊 Analyze findings
        - 📝 Generate comprehensive reports
        - 📄 Create professional PDFs
        """)

        # Statistics
        if st.session_state.get('reports_generated', 0) > 0:
            st.metric("Reports Generated", st.session_state.reports_generated)

    # Main content area
    col1, col2 = st.columns([2, 1])

    with col1:
        # Generate button
        if st.button("🚀 Generate Research Report", disabled=not topic):
            if not topic.strip():
                st.error("Please enter a research topic!")
                return

            # Initialize progress tracking
            progress_bar = st.progress(0)
            status_text = st.empty()

            try:
                # Step 1: Initialize
                if show_progress:
                    status_text.text("🔧 Initializing research crew...")
                    progress_bar.progress(20)
                    time.sleep(0.5)

                report_crew = ReportCrew(topic)

                # Step 2: Generate report
                if show_progress:
                    status_text.text("🔍 Conducting research and analysis...")
                    progress_bar.progress(50)

                with st.spinner("Generating research report..."):
                    result = report_crew.run()

                if show_progress:
                    status_text.text("✅ Research completed!")
                    progress_bar.progress(80)

                # Extract string content from CrewOutput
                report_content = extract_report_content(result)

                # Store in session state
                st.session_state.last_report = report_content
                st.session_state.last_topic = topic
                st.session_state.reports_generated = st.session_state.get('reports_generated', 0) + 1

                # Step 3: Generate PDF if requested
                pdf_path = None
                if auto_pdf:
                    if show_progress:
                        status_text.text("📄 Generating PDF...")
                        progress_bar.progress(90)

                    pdf_path = generator.create_pdf_report(report_content, topic)
                    st.session_state.last_pdf_path = pdf_path

                if show_progress:
                    status_text.text("🎉 Report generation completed!")
                    progress_bar.progress(100)
                    time.sleep(1)
                    status_text.empty()
                    progress_bar.empty()

                # Success message
                st.markdown("""
                <div class="success-message">
                    <strong>✅ Success!</strong> Your research report has been generated successfully.
                </div>
                """, unsafe_allow_html=True)

            except Exception as e:
                st.error(f"❌ Error generating report: {str(e)}")
                progress_bar.empty()
                status_text.empty()

    with col2:
        # Quick actions
        st.subheader("🎯 Quick Actions")

        if st.session_state.get('last_report'):
            if st.button("📄 Generate PDF"):
                with st.spinner("Creating PDF..."):
                    pdf_path = generator.create_pdf_report(
                        st.session_state.last_report,
                        st.session_state.last_topic
                    )
                    if pdf_path:
                        st.session_state.last_pdf_path = pdf_path
                        st.success("PDF generated successfully!")

            if st.button("🔄 Clear Results"):
                for key in ['last_report', 'last_topic', 'last_pdf_path']:
                    st.session_state.pop(key, None)
                st.rerun()

        # Sample topics
        st.subheader("💡 Sample Topics")
        sample_topics = [
            "Artificial Intelligence in Healthcare",
            "Climate Change Impact on Agriculture",
            "Blockchain Technology Applications",
            "Remote Work Productivity Trends",
            "Renewable Energy Market Analysis"
        ]

        for sample_topic in sample_topics:
            if st.button(f"📌 {sample_topic}", key=f"sample_{sample_topic}"):
                st.session_state.sample_topic = sample_topic
                st.rerun()

    # Display results
    if st.session_state.get('last_report'):
        st.markdown("---")
        st.subheader("📊 Generated Research Report")

        # Report metadata
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📝 Topic", st.session_state.last_topic)
        with col2:
            st.metric("📅 Generated", datetime.now().strftime("%Y-%m-%d"))
        with col3:
            # Fixed: Now st.session_state.last_report is guaranteed to be a string
            st.metric("📏 Length", f"{len(st.session_state.last_report.split())} words")

        # Report content
        st.markdown("""
        <div class="report-container">
        """, unsafe_allow_html=True)

        st.markdown(st.session_state.last_report)

        st.markdown("</div>", unsafe_allow_html=True)

        # PDF download link
        if st.session_state.get('last_pdf_path'):
            st.markdown("---")
            st.subheader("📄 Download Options")

            # Create download button
            with open(st.session_state.last_pdf_path, "rb") as pdf_file:
                pdf_bytes = pdf_file.read()

            st.download_button(
                label="📄 Download PDF Report",
                data=pdf_bytes,
                file_name=f"research_report_{st.session_state.last_topic.replace(' ', '_')}.pdf",
                mime="application/pdf",
                use_container_width=True
            )

            st.info(f"📁 PDF saved locally at: {st.session_state.last_pdf_path}")

    # Handle sample topic selection
    if st.session_state.get('sample_topic'):
        st.session_state.sample_topic = None

    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 1rem;">
        <p>🔬 Research Report Generator | Powered by CrewAI & Streamlit</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()