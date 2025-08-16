# Copyright (c) 2025 Microsoft Corporation.
# Licensed under the MIT License

"""
This file contains the handler for Zenti high-risk payment processing queries.
It provides expert guidance on merchant accounts, compliance, and payment solutions.
"""

import asyncio
from core.baseHandler import NLWebHandler
from core.llm import ask_llm
from core.prompts import PromptRunner
from misc.logger.logging_config_helper import get_configured_logger
from core.utils.utils import log
import json

logger = get_configured_logger("zenti_payment_handler")

class ZentiPaymentHandler:
    """Handler for high-risk payment processing queries."""

    def __init__(self, params, handler):
        """Initialize the handler with query parameters."""
        self.params = params
        self.handler = handler
        self.query_type = params.get("query_type", "general")
        self.business_vertical = params.get("business_vertical")
        self.specific_concern = params.get("specific_concern")
        self.urgency = params.get("urgency")
        self.current_status = params.get("current_status")
        logger.info(f"ZentiPaymentHandler initialized with params: {params}")

    async def do(self):
        """Process the payment-related query and provide expert guidance."""
        try:
            logger.info(f"Processing payment query of type: {self.query_type}")

            # Get response based on query type
            response = await self._get_response()

            # Send response to user
            message = {
                "message_type": "nlws",
                "answer": response["answer"],
                "items": []  # No items needed for consulting responses
            }
            await self.handler.send_message(message)

        except Exception as e:
            logger.exception(f"Error in ZentiPaymentHandler: {e}")
            error_msg = {
                "message_type": "nlws",
                "answer": "I encountered an error while processing your payment-related query. Please try again or contact our support team.",
                "items": []
            }
            await self.handler.send_message(error_msg)

    async def _get_response(self):
        """Get appropriate response based on query type."""
        # Base prompt for all query types
        base_prompt = f"""
        The user has a question about high-risk payment processing: {self.handler.query}
        Query type: {self.query_type}
        Business vertical: {self.business_vertical if self.business_vertical else 'Not specified'}
        Specific concern: {self.specific_concern if self.specific_concern else 'Not specified'}
        Urgency: {self.urgency if self.urgency else 'Not specified'}
        Current status: {self.current_status if self.current_status else 'Not specified'}

        Provide a detailed, professional response that:
        1. Directly addresses their specific concern
        2. Provides accurate information about high-risk payment processing
        3. Explains any relevant terms or concepts
        4. Offers actionable next steps or recommendations
        5. Maintains a helpful and consultative tone

        Response should be formatted in markdown and include:
        - Clear explanation of the topic
        - Relevant details and considerations
        - Next steps or recommendations
        - Any important disclaimers or notes
        """

        # Add query-specific context based on type
        if self.query_type == "approval":
            base_prompt += "\nFocus on merchant account approval process, requirements, and timeline."
        elif self.query_type == "fees":
            base_prompt += "\nExplain fee structures, pricing models, and factors affecting rates."
        elif self.query_type == "compliance":
            base_prompt += "\nDetail compliance requirements, regulations, and best practices."
        elif self.query_type == "chargebacks":
            base_prompt += "\nProvide chargeback prevention strategies and dispute management tips."
        elif self.query_type == "reserves":
            base_prompt += "\nExplain rolling reserves, their purpose, and how they work."
        elif self.query_type == "termination":
            base_prompt += "\nAddress account termination issues, MATCH list implications, and recovery options."
        elif self.query_type == "alternatives":
            base_prompt += "\nSuggest alternative payment solutions and backup processing options."

        # Get response from LLM
        response = await ask_llm(
            base_prompt,
            {
                "answer": "detailed response in markdown format",
                "next_steps": "list of recommended actions",
                "disclaimer": "any important disclaimers or notes"
            },
            level="high",  # Use high-quality model for detailed responses
            query_params=self.handler.query_params
        )

        # Format final response
        final_answer = f"{response['answer']}\n\n"
        if response.get('next_steps'):
            final_answer += "\n### Next Steps\n" + response['next_steps']
        if response.get('disclaimer'):
            final_answer += "\n\n*Note: " + response['disclaimer'] + "*"

        return {"answer": final_answer}
