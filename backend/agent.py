"""
agent.py

Agent orchestration layer for the Unbiased AI Decision multi-agent system.
Coordinates the Supervisor Agent, Worker Agents, and the Mistral AI API integration.
Ensures strict routing, data grounding, and hallucination prevention.
"""

import os
import json
from typing import Dict, Any
from dotenv import load_dotenv
from mistralai.client import Mistral

load_dotenv()

from prompt import (
    SUPERVISOR_SYSTEM_PROMPT,
    HIRING_AGENT_PROMPT,
    LOAN_AGENT_PROMPT,
    MEDICAL_AGENT_PROMPT,
    FINAL_RESPONSE_VALIDATION_PROMPT
)
from tools import display_csv_as_table

# Initialize Mistral Client
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
if not MISTRAL_API_KEY:
    print("WARNING: MISTRAL_API_KEY not found in .env")
client = Mistral(api_key=MISTRAL_API_KEY)

class MistralAgentWrapper:
    """Lightweight wrapper to interact with the Mistral API for reasoning tasks."""
    
    @staticmethod
    def call_mistral(system_prompt: str, user_query: str, temperature: float = 0.1) -> str:
        """
        Sends the prompt and query to Mistral. 
        Temperature is kept intentionally low (0.1) to enforce deterministic, grounded answers 
        and severely limit creative hallucinations.
        """
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_query}
        ]
        try:
            response = client.chat.complete(
                model="mistral-large-latest",
                messages=messages,
                temperature=temperature
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Mistral API Error: {str(e)}")
            return '{"error": "Mistral API failure", "reasoning": "Fallback due to API error", "route": "UNKNOWN"}'

class WorkerAgent:
    """Generic worker agent that fetches data context and consults Mistral AI."""
    
    def __init__(self, domain_prompt: str):
        self.system_prompt = domain_prompt

    def process_query(self, user_query: str, dataset_id: str) -> str:
        """
        Executes the worker workflow:
        1. Fetch relevant data structure to ground the prompt.
        2. Send query and data context to Mistral AI.
        3. Return structured response.
        """
        # Fetch context from our tools layer (defined in tools.py)
        data_context = display_csv_as_table(dataset_id, limit=10)
        
        # Inject context into the prompt safely
        formatted_prompt = self.system_prompt.replace("{data_context}", f"DATASET CONTEXT:\n{data_context}")
        
        # Delegate reasoning entirely to Mistral LLM
        return MistralAgentWrapper.call_mistral(formatted_prompt, user_query)

class SupervisorAgent:
    """Coordinates routing, delegation, and final validation of the system."""
    
    def __init__(self):
        # Register the specialized domain workers
        self.workers = {
            "HIRING": WorkerAgent(HIRING_AGENT_PROMPT),
            "LOAN": WorkerAgent(LOAN_AGENT_PROMPT),
            "MEDICAL": WorkerAgent(MEDICAL_AGENT_PROMPT)
        }

    def route_query(self, user_query: str, dataset_id: str) -> str:
        """
        Identifies the correct domain using Mistral AI based on query and dataset headers.
        """
        # Provide a minimal glimpse of the data to assist routing
        data_context = display_csv_as_table(dataset_id, limit=3)
        formatted_supervisor_prompt = SUPERVISOR_SYSTEM_PROMPT.replace(
            "{data_context}", f"DATASET HEADERS/SAMPLE:\n{data_context}"
        )
        
        routing_response = MistralAgentWrapper.call_mistral(formatted_supervisor_prompt, user_query)
        
        try:
            # Parse the JSON response requested in the prompt
            routing_data = json.loads(routing_response)
            domain = routing_data.get("route", "UNKNOWN").upper()
        except json.JSONDecodeError:
            domain = "UNKNOWN"
            
        return domain

    def validate_response(self, draft_output: str, dataset_id: str) -> str:
        """
        Acts as the final guardrail. Validates the draft response against 
        the source data to prune unverified claims and ensure absolute fairness.
        """
        data_context = display_csv_as_table(dataset_id, limit=15)
        
        formatted_validation_prompt = FINAL_RESPONSE_VALIDATION_PROMPT.replace(
            "{draft_output}", draft_output
        ).replace(
            "{data_context}", data_context
        )
        
        # Call Mistral again strictly for review and compliance enforcement
        return MistralAgentWrapper.call_mistral(
            formatted_validation_prompt, 
            "Review and finalize this draft. You must strictly follow the data grounding constraints."
        )

    def run_workflow(self, user_query: str, dataset_id: str) -> str:
        """
        Executes the complete, end-to-end multi-agent orchestration pipeline.
        """
        # Step 1 & 2: Supervisor receives query and identifies domain
        domain = self.route_query(user_query, dataset_id)
        
        # Step 3: Route query to correct worker agent
        worker = self.workers.get(domain)
        
        if not worker:
            return "Error: Could not confidently determine the fairness domain (Hiring, Loan, or Medical) for this request."
            
        # Step 4, 5, & 6: Worker fetches data, queries Mistral, and returns draft
        draft_response = worker.process_query(user_query, dataset_id)
        
        # Step 7: Supervisor strictly validates the draft response
        final_response = self.validate_response(draft_response, dataset_id)
        
        # Step 8: Final safe, unbiased response sent to user
        return final_response

# -----------------------------------------------------------------------------
# Entry Point Example
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    # Example instantiation
    orchestrator = SupervisorAgent()
    # response = orchestrator.run_workflow("Are female candidates being rejected more often?", "dataset_uuid_123")
    # print(response)
