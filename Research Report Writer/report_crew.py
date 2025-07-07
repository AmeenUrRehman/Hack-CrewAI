from crewai import Crew, LLM
from report_tasks import ReportTasks
from report_agents import ResearchAgent
import os
from dotenv import load_dotenv

# Load environment variables FIRST
load_dotenv()

# Then get the API key
OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')

class ReportCrew:
    def __init__(self, topic):
        self.topic = topic

    def run(self):
        agents = ResearchAgent()
        tasks = ReportTasks()

        # Create LLM first
        llm = LLM(
            model="openrouter/deepseek/deepseek-r1-0528:free",
            base_url="https://openrouter.ai/api/v1",
            api_key=OPENROUTER_API_KEY
        )

        # Define agents with the custom LLM
        planner = agents.content_planner_agent(llm=llm)
        writer = agents.content_writer_agent(llm=llm)
        editor = agents.editor_agent(llm=llm)

        # Define tasks
        plan = tasks.planner_task(planner, self.topic)
        write = tasks.writer_task(writer, self.topic)
        edit = tasks.editor_task(editor, self.topic)

        # Create and run Crew
        crew = Crew(
            agents=[planner, writer, editor],
            tasks=[plan, write, edit],
            verbose=True
        )

        result = crew.kickoff(inputs={"topic": self.topic})
        return result