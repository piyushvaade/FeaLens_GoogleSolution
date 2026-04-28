"""
workflow.py

Orchestrates the explicit "Run Fairness Analysis" workflow.
Plugs into tools.py for data fetching and metric calculation,
and uses agent.py (Mistral wrapper) for the final reasoning and report generation.
"""

from typing import Dict, Any, List
import json
import pandas as pd

# Import existing ecosystem tools
from tools import (
    read_and_parse_csv,
    calculate_fairness_metrics,
    fetch_dataset_metadata
)
from agent import MistralAgentWrapper

def detect_sensitive_attributes(df: pd.DataFrame) -> List[str]:
    """
    Step 1: Automatically identify potential sensitive columns based on common keywords
    across hiring, loan, and medical domains.
    """
    sensitive_keywords = ['gender', 'sex', 'race', 'ethnicity', 'age', 'income', 'location', 'priority', 'disability']
    detected = []
    for col in df.columns:
        if any(keyword in str(col).lower() for keyword in sensitive_keywords):
            detected.append(col)
    return detected

def analyze_dataset_imbalance(df: pd.DataFrame, sensitive_col: str) -> Dict[str, Any]:
    """
    Step 2: Check for underrepresented groups and skewed distributions.
    """
    counts = df[sensitive_col].value_counts()
    total = len(df)
    
    # Structure: {group_name: {"count": X, "percentage": Y}}
    distribution = {str(k): {"count": int(v), "percentage": float(v/total)} for k, v in counts.items()}
    
    # Identify minority groups (e.g., representation under 15%)
    underrepresented = [str(k) for k, v in distribution.items() if v["percentage"] < 0.15]
    
    return {
        "distribution": distribution,
        "underrepresented_groups": underrepresented,
        "total_records": total
    }

def run_fairness_analysis(df: pd.DataFrame, dataset_id: str, target_col: str, sensitive_col: str = None) -> Dict[str, Any]:
    """
    Executes the complete explicit fairness analysis workflow.
    """
    # Initialize the final report structure
    report = {
        "dataset_id": dataset_id,
        "target_column": target_col,
        "sensitive_column": sensitive_col,
        "imbalance_analysis": {},
        "raw_metrics": {},
        "final_report": {}
    }

    if df is None or df.empty:
         return {"error": "Failed to load dataset for analysis."}

    # Step 1: Detect sensitive attributes if not explicitly provided by the user
    if not sensitive_col:
        detected = detect_sensitive_attributes(df)
        if not detected:
            return {"error": "No sensitive attributes detected. Please specify one manually."}
        sensitive_col = detected[0]
        report["sensitive_column"] = sensitive_col

    # Step 2: Dataset imbalance analysis
    imbalance = analyze_dataset_imbalance(df, sensitive_col)
    report["imbalance_analysis"] = imbalance

    # Step 3: Fairness metrics extraction using tools.py
    # We convert the target column to binary for statistical metric computation
    y = df[target_col]
    if y.dtype == 'object':
        positive_class = y.mode()[0] # Assume the most frequent class is the positive outcome for the baseline
        y_binary = (y == positive_class).astype(int).tolist()
    else:
        y_binary = (y > y.min()).astype(int).tolist()

    sensitive_features = df[sensitive_col].tolist()
    
    # Calculate raw math via tools.py
    metrics = calculate_fairness_metrics(
        y_true=y_binary, 
        y_pred=y_binary, # Passing true labels twice to measure historical dataset bias
        sensitive_features=sensitive_features
    )
    report["raw_metrics"] = metrics

    # Step 4, 5 & 6: Mistral Reasoning and Final Report Generation
    # We send the raw metrics to Mistral without hardcoding business rules.
    # Mistral acts as the interpreter to identify unfairness and recommend fixes.
    
    mistral_prompt = f"""
    You are the Fairness Reporting Engine for Unbiased AI Decision.
    Your task is to analyze the raw data metrics provided below and generate a final, human-readable fairness report.
    
    CONTEXT:
    - Target Decision Variable: {target_col}
    - Sensitive Attribute Analyzed: {sensitive_col}
    - Group Representation Data: {json.dumps(imbalance)}
    - Calculated Fairness Metrics: {json.dumps(metrics)}
    
    INSTRUCTIONS:
    1. Explain the fairness results objectively.
    2. Identify if the process (Hiring, Loan, or Medical) is unfair based on the context.
    3. Determine the overall bias level.
    4. Provide actionable recommendations.
    
    Do NOT hallucinate data. Ground your report strictly in the numbers provided.
    
    OUTPUT FORMAT (Strict JSON):
    {{
        "bias_level": "Low|Medium|High",
        "affected_groups": ["group1", "group2"],
        "risk_severity": "Brief description of the risk severity",
        "explanation": "Detailed summary of the detected issues",
        "recommendations": ["Actionable fix 1", "Actionable fix 2"]
    }}
    """
    
    # Delegate reasoning to Mistral wrapper from agent.py
    mistral_response = MistralAgentWrapper.call_mistral(
        system_prompt=mistral_prompt,
        user_query="Generate the final structured fairness report."
    )
    
    # Parse the JSON response returned by Mistral
    try:
        final_report = json.loads(mistral_response)
        report["final_report"] = final_report
    except json.JSONDecodeError:
        report["final_report"] = {"error": "Mistral failed to return valid JSON format."}

    return report
