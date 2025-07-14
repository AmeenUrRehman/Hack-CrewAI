from crewai import Task
from textwrap import dedent


class SupportTasks:

    def inquiry_resolution(self, agent, tools=None):
        return Task(
            description=(
                "{customer} just reached out with a super important ask:\n"
                "{inquiry}\n\n"
                "{person} from {customer} is the one that reached out. "
                "Make sure to use everything you know to provide the best support possible. "
                "You must strive to provide a complete and accurate response to the customer's inquiry."
            ),
            expected_output=(
                "A detailed, informative response to the customer's inquiry that addresses "
                "all aspects of their question.\n"
                "The response should include references to everything you used to find the answer, "
                "including external data or solutions. "
                "Ensure the answer is complete, leaving no questions unanswered, and maintain a helpful and friendly "
                "tone throughout."
            ),
            agent=agent,
        )

    def quality_assurance_review(self, agent):
        return Task(
            description=(
                "Review the response drafted by the Senior Support Representative for {customer}'s inquiry. "
                "Ensure that the answer is comprehensive, accurate, and adheres to the "
                "high-quality standards expected for customer support.\n"
                "Verify that all parts of the customer's inquiry have been addressed "
                "thoroughly, with a helpful and friendly tone.\n"
                "Check for references and sources used to find the information, "
                "ensuring the response is well-supported and leaves no questions unanswered."
            ),
            expected_output=(
                "A final, detailed, and informative response ready to be sent to the customer.\n"
                "This response should fully address the customer's inquiry, incorporating all "
                "relevant feedback and improvements.\n"
                "Don't be too formal, we are a chill and cool company "
                "but maintain a professional and friendly tone throughout."
            ),
            agent=agent,
        )

    def technical_escalation_analysis(self, agent, tools=None):
        return Task(
            description=dedent(f"""
                Analyze the technical aspects of the customer inquiry from {{customer}}.
                Determine if this is a complex technical issue that requires specialized knowledge.

                If it's a technical escalation:
                - Provide detailed technical analysis and solutions
                - Include code examples, configuration steps, or API documentation references
                - Suggest best practices and optimization recommendations
                - Identify potential integration issues or compatibility concerns

                If it's not a technical escalation:
                - Provide brief technical context to support the main response
                - Suggest any technical considerations the support team should be aware of

                {{self.__tip_section()}}

                Customer: {{customer}}
                Person: {{person}}
                Inquiry: {{inquiry}}
            """),
            expected_output=(
                "Technical analysis report including:\n"
                "- Assessment of technical complexity level\n"
                "- Detailed technical solutions with code examples if applicable\n"
                "- Best practices and recommendations\n"
                "- Any additional technical considerations or warnings"
            ),
            agent=agent,
        )

    def customer_success_followup(self, agent):
        return Task(
            description=dedent(f"""
                As a Customer Success Manager, review the resolved inquiry from {{customer}} 
                and create a comprehensive follow-up plan.

                Your analysis should include:
                - Assessment of the customer's current usage and satisfaction level
                - Identification of potential upsell or expansion opportunities
                - Proactive recommendations for improving their experience
                - Suggestions for additional features or services that could benefit them
                - Timeline for follow-up communications

                {{self.__tip_section()}}

                Customer: {{customer}}
                Person: {{person}}
                Original Inquiry: {{inquiry}}
            """),
            expected_output=(
                "Customer success follow-up plan including:\n"
                "- Current customer health assessment\n"
                "- Proactive recommendations and next steps\n"
                "- Potential opportunities for account growth\n"
                "- Scheduled follow-up timeline and communication plan\n"
                "- Any red flags or concerns that need immediate attention"
            ),
            agent=agent,
        )

    def sentiment_analysis_and_routing(self, agent):
        return Task(
            description=dedent(f"""
                Analyze the sentiment and urgency of the customer inquiry from {{customer}}.
                Determine the appropriate routing and priority level for this request.

                Consider:
                - Emotional tone and sentiment of the inquiry
                - Urgency indicators and business impact
                - Customer tier and relationship history
                - Complexity level and required expertise
                - Appropriate escalation path if needed

                {{self.__tip_section()}}

                Customer: {{customer}}
                Person: {{person}}
                Inquiry: {{inquiry}}
            """),
            expected_output=(
                "Sentiment analysis report including:\n"
                "- Sentiment score and emotional tone assessment\n"
                "- Urgency level and priority ranking\n"
                "- Recommended routing and escalation path\n"
                "- Suggested response timeline and approach\n"
                "- Any special handling instructions or considerations"
            ),
            agent=agent,
        )

    def __tip_section(self):
        return "If you do your BEST WORK, I'll tip you $100!"