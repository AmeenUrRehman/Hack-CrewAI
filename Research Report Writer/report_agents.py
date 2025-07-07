# In your report_agents.py file
from crewai import Agent

class ResearchAgent:
    def content_planner_agent(self, llm=None):
        return Agent(
            role='Content Planner',
            goal='Plan engaging and factually accurate content on {topic}',
            backstory="You're working on planning a blog article about the topic: {topic}. "
                     "You collect information that helps the audience learn something "
                     "and make informed decisions.",
            llm=llm,  # Pass the custom LLM
            allow_delegation=False,
            verbose=True
        )

    def content_writer_agent(self, llm=None):
        return Agent(
            role='Content Writer',
            goal='Write insightful and factually accurate opinion piece about the topic: {topic}',
            backstory="You're working on writing a new opinion piece about the topic: {topic}. "
                     "You base your writing on the work of the Content Planner, who provides an outline "
                     "and relevant context about the topic.",
            llm=llm,  # Pass the custom LLM
            allow_delegation=False,
            verbose=True
        )

    def editor_agent(self, llm=None):
        return Agent(
            role='Editor',
            goal='Edit a given blog post to align with the writing style of the organization.',
            backstory="You are an editor who receives a blog post from the Content Writer. "
                     "Your goal is to review the blog post to ensure that it follows journalistic best practices, "
                     "provides balanced viewpoints when providing opinions or assertions, and also "
                     "avoids major controversial topics or opinions when possible.",
            llm=llm,  # Pass the custom LLM
            allow_delegation=False,
            verbose=True
        )