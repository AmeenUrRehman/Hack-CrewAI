from crewai import Agent
from langchain.llms import OpenAI
from tools.calculator_tools import CalculatorTools


class TripAgents:

    def city_selection_agent(self, llm= None):
        return Agent(
            role="City Selection Expert",
            goal="Select the best city based on weather, seasonal events, and travel prices.",
            backstory=(
                "A seasoned expert in analyzing global travel data, with a knack "
                "for identifying ideal destinations by evaluating weather trends, "
                "local events, and cost efficiency."
            ),
            llm=llm,
            verbose=True
        )

    def local_expert(self, llm= None):
        return Agent(
            role="Local City Expert",
            goal="Provide authentic and insightful information about the selected city.",
            backstory=(
                "A well-connected local guide with deep knowledge of the city’s culture, "
                "hidden gems, must-visit places, and everyday life. Knows what truly makes the city special."
            ),
            llm=llm,
            verbose=True
        )

    def travel_concierge(self, llm= None):
        return Agent(
            role="Travel Concierge Specialist",
            goal="Design the ultimate travel itinerary including daily plans, budget, and packing suggestions.",
            backstory=(
                "A highly experienced travel planner specializing in seamless itineraries, "
                "with expertise in balancing comfort, adventure, and budget. "
                "Knows the ins and outs of planning unforgettable trips."
            ),
            llm=llm,
            verbose=True
        )
