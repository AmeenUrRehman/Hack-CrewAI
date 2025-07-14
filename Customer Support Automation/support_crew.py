from crewai import Crew, LLM
from support_agent import SupportAgents
from support_tasks import SupportTasks
import os
from dotenv import load_dotenv


# Load environment variables FIRST
load_dotenv()

# Then get the API key
OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')


class SupportCrew:
    def __init__(self, customer, person, inquiry, tools=None):
        self.customer = customer
        self.person = person
        self.inquiry = inquiry

    def run(self):

        agents = SupportAgents()
        tasks = SupportTasks()

        # Create LLM first
        llm = LLM(
            model="openrouter/deepseek/deepseek-r1-0528:free",
            base_url="https://openrouter.ai/api/v1",
            api_key=OPENROUTER_API_KEY
        )

        # Create agents with custom LLM
        support_agent = agents.senior_support_representative(llm=llm)
        quality_assurance_agent = agents.support_quality_assurance_specialist(llm=llm)
        technical_specialist = agents.technical_escalation_specialist(llm=llm)
        success_manager = agents.customer_success_manager(llm=llm)

        # Create tasks
        inquiry_task = tasks.inquiry_resolution(
            support_agent,
        )

        quality_review_task = tasks.quality_assurance_review(
            quality_assurance_agent
        )

        technical_analysis_task = tasks.technical_escalation_analysis(
            technical_specialist,
        )

        success_followup_task = tasks.customer_success_followup(
            success_manager
        )

        # Assemble crew
        crew = Crew(
            agents=[support_agent, quality_assurance_agent, technical_specialist, success_manager],
            tasks=[inquiry_task, technical_analysis_task, quality_review_task, success_followup_task],
            verbose=True
        )

        # Prepare inputs
        inputs = {
            "customer": self.customer,
            "person": self.person,
            "inquiry": self.inquiry
        }

        result = crew.kickoff(inputs=inputs)
        return result


# Example usage and testing
if __name__ == "__main__":
    # Example customer support scenarios

    # Scenario 1: Basic setup question
    support_crew_1 = SupportCrew(
        customer="DeepLearningAI",
        person="Andrew Ng",
        inquiry="I need help with setting up a Crew and kicking it off, specifically how can I add memory to my crew? Can you provide guidance?"
    )

    # Scenario 2: Technical integration issue
    support_crew_2 = SupportCrew(
        customer="TechCorp",
        person="Sarah Johnson",
        inquiry="Our API integration is failing with 429 rate limit errors. We're using the Python SDK and getting timeouts. This is affecting our production system and we need urgent help."
    )

    # Scenario 3: Billing and account question
    support_crew_3 = SupportCrew(
        customer="StartupXYZ",
        person="Mike Chen",
        inquiry="We're interested in upgrading our plan but want to understand the pricing structure better. Also, can we get usage analytics for our current consumption?"
    )

    print("Customer Support Automation System Ready!")
    print("Available scenarios:")
    print("1. Basic setup question")
    print("2. Technical integration issue")
    print("3. Billing and account question")

    # Uncomment to run a specific scenario
    # result = support_crew_1.run()
    # print(result)