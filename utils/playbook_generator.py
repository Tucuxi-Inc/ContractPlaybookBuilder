"""
AI-powered playbook generation using OpenAI GPT-4.
"""
import json
import os
from openai import OpenAI
import config


def get_openai_client():
    """Get OpenAI client with API key from config."""
    api_key = config.OPENAI_API_KEY
    if not api_key:
        raise ValueError(
            "OpenAI API key not found. Please set the OPENAI_API_KEY environment variable."
        )
    return OpenAI(api_key=api_key)


SYSTEM_PROMPT = """You are an expert contract attorney and negotiation strategist specializing in creating comprehensive contract playbooks. Your role is to analyze contract text and generate detailed playbook entries that help legal teams and business professionals negotiate effectively.

For each clause or section you analyze, provide:
1. Clear issue identification
2. Business context explaining why this matters
3. Balanced perspective (both customer/buyer and provider/vendor viewpoints)
4. Specific negotiation guidance with sample language
5. Risk classification (Red = deal-breaker, Yellow = needs approval, Green = acceptable)

Your output should be practical, actionable, and usable by both experienced attorneys and business professionals with limited legal training."""


ANALYSIS_PROMPT = """Analyze the following contract text and create a comprehensive playbook.

CONTRACT TEXT:
{contract_text}

USER CONTEXT:
- Agreement Type: {agreement_type}
- User's Role: {user_role}
- Risk Tolerance: {risk_tolerance}

Please analyze this contract and generate a detailed playbook. For EACH significant clause or section, provide the following in valid JSON format:

{{
    "agreement_summary": {{
        "title": "Agreement title or type",
        "parties": "Description of the parties involved",
        "purpose": "Brief description of the agreement's purpose",
        "key_dates": "Any key dates or terms mentioned",
        "overall_risk_level": "High/Medium/Low",
        "critical_issues_count": number
    }},
    "clauses": [
        {{
            "section_reference": "Section number or identifier",
            "clause_title": "Name of the clause/issue",
            "original_language": "Exact or summarized text from the agreement",
            "issue_description": "What this clause addresses",
            "business_context": "Why this matters from a business perspective",
            "customer_perspective": {{
                "concerns": "What a customer/buyer would worry about",
                "objectives": "What a customer wants to achieve"
            }},
            "provider_perspective": {{
                "concerns": "What a provider/vendor would worry about",
                "objectives": "What a provider wants to achieve"
            }},
            "preferred_position": {{
                "description": "The ideal negotiation outcome",
                "sample_language": "Suggested contract language"
            }},
            "fallback_positions": [
                {{
                    "description": "First acceptable alternative",
                    "sample_language": "Alternative language",
                    "conditions": "When to use this fallback"
                }}
            ],
            "positions_to_avoid": [
                {{
                    "description": "What NOT to accept",
                    "reason": "Why this is problematic"
                }}
            ],
            "risk_level": "Red/Yellow/Green",
            "risk_explanation": "Why this risk level was assigned",
            "approval_required": "Who needs to approve deviations (Legal, Executive, Procurement, None)",
            "negotiation_tips": "Practical advice for negotiating this clause"
        }}
    ],
    "definitions": [
        {{
            "term": "Key term from the agreement",
            "definition": "What it means",
            "importance": "Why this definition matters"
        }}
    ],
    "quick_reference": {{
        "deal_breakers": ["List of absolute deal-breaker issues"],
        "high_priority_items": ["Items requiring special attention"],
        "standard_acceptable_terms": ["Terms that are generally acceptable as-is"],
        "common_negotiation_points": ["Typical areas of negotiation"]
    }}
}}

Be thorough and analyze ALL significant clauses in the contract. Focus on practical, actionable guidance. Ensure the JSON is valid and complete."""


def analyze_contract(
    contract_text: str,
    agreement_type: str = "General Agreement",
    user_role: str = "Customer",
    risk_tolerance: str = "Moderate"
) -> dict:
    """
    Analyze contract text and generate playbook content.

    Args:
        contract_text: The extracted text from the uploaded agreement
        agreement_type: Type of agreement (SaaS, Services, NDA, etc.)
        user_role: Whether user is Customer/Buyer or Provider/Vendor
        risk_tolerance: Low, Moderate, or High risk tolerance

    Returns:
        dict containing the full playbook analysis
    """
    client = get_openai_client()

    # Truncate very long contracts to fit within context limits
    max_chars = 100000  # Approximately 25k tokens
    if len(contract_text) > max_chars:
        contract_text = contract_text[:max_chars] + "\n\n[Document truncated due to length...]"

    prompt = ANALYSIS_PROMPT.format(
        contract_text=contract_text,
        agreement_type=agreement_type,
        user_role=user_role,
        risk_tolerance=risk_tolerance
    )

    response = client.chat.completions.create(
        model=config.OPENAI_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,  # Lower temperature for more consistent output
        max_tokens=16000,
        response_format={"type": "json_object"}
    )

    result_text = response.choices[0].message.content

    try:
        playbook_data = json.loads(result_text)
    except json.JSONDecodeError as e:
        # Try to extract JSON from the response
        import re
        json_match = re.search(r'\{[\s\S]*\}', result_text)
        if json_match:
            playbook_data = json.loads(json_match.group())
        else:
            raise ValueError(f"Failed to parse AI response as JSON: {e}")

    return playbook_data


def analyze_contract_chunked(
    contract_text: str,
    agreement_type: str = "General Agreement",
    user_role: str = "Customer",
    risk_tolerance: str = "Moderate",
    progress_callback=None
) -> dict:
    """
    Analyze a long contract by processing it in chunks.

    For very long documents, this splits the analysis into multiple API calls
    and combines the results.
    """
    # For shorter documents, use single analysis
    if len(contract_text) < 50000:
        if progress_callback:
            progress_callback(50, "Analyzing contract...")
        result = analyze_contract(contract_text, agreement_type, user_role, risk_tolerance)
        if progress_callback:
            progress_callback(100, "Analysis complete")
        return result

    # For longer documents, chunk and combine
    client = get_openai_client()

    # Split into chunks of roughly 40k characters
    chunk_size = 40000
    chunks = []
    for i in range(0, len(contract_text), chunk_size):
        chunks.append(contract_text[i:i + chunk_size])

    all_clauses = []
    all_definitions = []
    agreement_summary = None

    for idx, chunk in enumerate(chunks):
        if progress_callback:
            progress = int((idx + 1) / len(chunks) * 80)
            progress_callback(progress, f"Analyzing section {idx + 1} of {len(chunks)}...")

        chunk_result = analyze_contract(
            chunk,
            agreement_type,
            user_role,
            risk_tolerance
        )

        if "clauses" in chunk_result:
            all_clauses.extend(chunk_result["clauses"])

        if "definitions" in chunk_result:
            all_definitions.extend(chunk_result["definitions"])

        if not agreement_summary and "agreement_summary" in chunk_result:
            agreement_summary = chunk_result["agreement_summary"]

    # Combine results
    if progress_callback:
        progress_callback(90, "Combining analysis...")

    # Remove duplicate definitions
    seen_terms = set()
    unique_definitions = []
    for defn in all_definitions:
        term = defn.get("term", "").lower()
        if term not in seen_terms:
            seen_terms.add(term)
            unique_definitions.append(defn)

    # Generate quick reference from combined clauses
    deal_breakers = []
    high_priority = []
    standard_terms = []

    for clause in all_clauses:
        risk = clause.get("risk_level", "").lower()
        title = clause.get("clause_title", "")
        if risk == "red":
            deal_breakers.append(title)
        elif risk == "yellow":
            high_priority.append(title)
        else:
            standard_terms.append(title)

    combined_result = {
        "agreement_summary": agreement_summary or {
            "title": "Contract Analysis",
            "parties": "Not specified",
            "purpose": "Contract playbook analysis",
            "key_dates": "Not specified",
            "overall_risk_level": "Medium",
            "critical_issues_count": len(deal_breakers)
        },
        "clauses": all_clauses,
        "definitions": unique_definitions,
        "quick_reference": {
            "deal_breakers": deal_breakers[:10],  # Top 10
            "high_priority_items": high_priority[:10],
            "standard_acceptable_terms": standard_terms[:10],
            "common_negotiation_points": [c.get("clause_title", "") for c in all_clauses[:5]]
        }
    }

    if progress_callback:
        progress_callback(100, "Analysis complete")

    return combined_result
