from crewai import Task
from textwrap import dedent
from datetime import date


class TripTasks:

    def identify_task(self, agent, origin, cities, interests, range):
        return Task(
            description=dedent(f"""
                Analyze and select the best city for the trip based 
                on specific criteria such as weather patterns, seasonal
                events, and travel costs. This task involves comparing
                multiple cities while considering current weather conditions,
                upcoming events, and overall expenses.

                Your final answer must include a detailed report on the chosen city,
                covering actual flight costs, the weather forecast, key attractions,
                and any other insights that justify the choice.

                {self.__tip_section()}

                Traveling from: {origin}  
                City Options: {cities}  
                Trip Date: {range}  
                Traveler Interests: {interests}
            """),
            agent=agent,
            expected_output="Detailed report on the chosen city including flight costs, weather forecast, and attractions"
        )

    def gather_task(self, agent, origin, interests, range):
        return Task(
            description=dedent(f"""
                As a local expert, create an in-depth guide for a traveler who wants
                to have THE BEST experience in your city!

                Gather information on must-see attractions, local customs, special events,
                and daily activity recommendations. Highlight places only locals would know,
                hidden gems, and cultural hotspots. Also, include a weather forecast and
                a high-level cost estimate.

                The final output should be a rich, practical city guide filled with cultural
                insights and personalized travel tips to enhance the experience.

                {self.__tip_section()}

                Trip Date: {range}  
                Traveling from: {origin}  
                Traveler Interests: {interests}
            """),
            agent=agent,
            expected_output="Comprehensive city guide including hidden gems, cultural hotspots, and practical travel tips"
        )

    def plan_task(self, agent, origin, interests, range):
        return Task(
            description=dedent(f"""
                Expand the city guide into a full 7-day travel itinerary, including
                per-day plans, weather forecasts, restaurant suggestions, packing advice,
                and a detailed budget.

                You MUST recommend actual places to visit, real hotels to stay at, and 
                specific restaurants to dine in. Justify each recommendation—what makes it
                special, and why it’s worth including.

                Your final answer must be a complete markdown-formatted travel plan that
                includes a daily schedule, expected weather, clothing suggestions, and a
                budget breakdown—ensuring THE BEST TRIP EVER!

                {self.__tip_section()}

                Trip Date: {range}  
                Traveling from: {origin}  
                Traveler Interests: {interests}
            """),
            agent=agent,
            expected_output="Complete expanded travel plan with daily schedule, weather conditions, packing suggestions, and budget breakdown"
        )

    def __tip_section(self):
        return "If you do your BEST WORK, I'll tip you $100!"
