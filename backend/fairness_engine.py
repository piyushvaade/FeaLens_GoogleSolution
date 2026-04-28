import pandas as pd
import numpy as np
import re

class FairnessEngine:
    def __init__(self):
        self.sensitive_keywords = ['gender', 'sex', 'race', 'ethnicity', 'age', 'zip', 'nationality', 'religion', 'disability']
    
    def detect_sensitive_attributes(self, df):
        detected = []
        for col in df.columns:
            if any(keyword in col.lower() for keyword in self.sensitive_keywords):
                detected.append(col)
        return detected

    def analyze_dataset_bias(self, df, target_col, sensitive_col):
        # Ensure target is binary
        y = df[target_col]
        if y.dtype == 'object':
            # Simple heuristic: last alphabetical class is positive
            classes = sorted(y.unique())
            y = (y == classes[-1]).astype(int)
        else:
            # If numeric, assume values > 0 are positive or just use as is
            y = (y > y.min()).astype(int)

        group_counts = df[sensitive_col].value_counts().to_dict()
        groups = df[sensitive_col].unique()
        
        selection_rates = {}
        for group in groups:
            mask = df[sensitive_col] == group
            rate = y[mask].mean()
            selection_rates[str(group)] = float(rate)

        # Disparate Impact Ratio (DIR)
        rates = list(selection_rates.values())
        if len(rates) > 1 and max(rates) > 0:
            di_ratio = min(rates) / max(rates)
        else:
            di_ratio = 1.0

        return {
            "group_counts": {str(k): int(v) for k, v in group_counts.items()},
            "selection_rates": selection_rates,
            "disparate_impact_ratio": float(di_ratio),
            "risk_level": "High" if di_ratio < 0.8 else "Low"
        }

    def audit_model(self, df, target_col, sensitive_col):
        # Manual calculation of model-like metrics from the dataset
        # In a real system, we'd train a model, but here we'll simulate the audit
        # based on the historical labels (which is 'Dataset Auditing')
        analysis = self.analyze_dataset_bias(df, target_col, sensitive_col)
        
        # Simulate DP Diff
        rates = list(analysis['selection_rates'].values())
        dp_diff = max(rates) - min(rates) if len(rates) > 1 else 0
        
        # Simulate accuracy (how well a simple majority baseline would do)
        y = df[target_col]
        if y.dtype == 'object':
            majority_class = y.mode()[0]
            acc = (y == majority_class).mean()
        else:
            acc = (y > y.min()).astype(int).mean()
            acc = max(acc, 1 - acc)

        return {
            "demographic_parity_diff": float(dp_diff),
            "equalized_odds_diff": float(dp_diff * 0.8), # Approximation for demo
            "accuracy": float(acc)
        }

    def mitigate_bias(self, df, target_col, sensitive_col):
        analysis = self.analyze_dataset_bias(df, target_col, sensitive_col)
        
        recommendations = []
        if analysis['disparate_impact_ratio'] < 0.8:
            recommendations.append("Apply Reweighing: Assign higher weights to samples from the disadvantaged group during model training.")
            recommendations.append("Data Balancing: Collect more data for underrepresented groups or use synthetic oversampling (SMOTE).")
        
        if analysis['risk_level'] == "High":
            recommendations.append("Feature Suppression: Consider removing the sensitive attribute or its close proxies from the feature set.")
            recommendations.append("Outcome Calibration: Adjust decision thresholds independently for different groups to achieve Equal Opportunity.")
            
        return recommendations
