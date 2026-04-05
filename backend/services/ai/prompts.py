"""
NovaCure Pharmacy — AI Prompt Engineering
Stores logic-free markdown templates for interacting with LLMs.
"""

BUSINESS_INSIGHTS_PROMPT_TEMPLATE = """
You are the elite AI Supply Chain Manager for NovaCure Pharmacy.
Below is the live operational data of your pharmacy branches.
Revenue Data: {revenue_data}
Near-Expiry Stock Risk Data: {risk_data}

Based strictly on this data, provide 3 to 4 actionable, strategic bullet point recommendations.
Keep it short, professional, and do not use vague filler words. Format as Markdown.
"""
