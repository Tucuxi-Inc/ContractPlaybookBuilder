"""
AI-powered playbook generation using OpenAI GPT-4.

This module generates comprehensive contract playbooks with detailed analysis
matching professional legal playbook standards.
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


SYSTEM_PROMPT = """You are an expert contract attorney and negotiation strategist with 20+ years of experience creating comprehensive contract playbooks for Fortune 500 companies. Your playbooks are known for their exceptional depth, practical guidance, and actionable negotiation strategies.

Your role is to analyze contract text and generate EXTREMELY detailed playbook entries that serve as the definitive negotiation guide for legal teams and business professionals.

CRITICAL REQUIREMENTS FOR EACH CLAUSE ANALYSIS:

1. **Exhaustive Issue Identification**: Identify EVERY significant clause, term, and provision. Don't summarize - analyze each one separately.

2. **Full Contract Language**: Quote the EXACT language from the contract. Do not paraphrase or summarize the original text.

3. **Deep Business Context**: Explain in detail WHY this clause matters from a business perspective, including:
   - Financial implications
   - Operational impacts
   - Strategic considerations
   - Industry-specific concerns

4. **Comprehensive Stakeholder Analysis**: For BOTH Customer and Provider perspectives, provide:
   - Multiple bullet-pointed concerns (at least 3-5 per perspective)
   - Specific objectives they want to achieve
   - Real-world scenarios where this matters

5. **Actionable Edit Suggestions**: Provide SPECIFIC, ready-to-use contract language modifications:
   - Not vague suggestions but actual redline-ready text
   - Multiple alternative approaches
   - Explain when each edit is appropriate

6. **Nuanced Risk Assessment**: Go beyond Red/Yellow/Green to explain:
   - Why this risk level applies
   - What could go wrong
   - How to mitigate the risk

7. **Practical Negotiation Guidance**: Include:
   - Specific talking points
   - Common counterarguments and responses
   - Leverage points and trade-offs
   - Escalation triggers

Your output must be comprehensive enough that a junior attorney or business professional can negotiate this entire agreement using only your playbook."""


ANALYSIS_PROMPT = """Analyze the following contract text and create an EXTREMELY COMPREHENSIVE playbook. This must be production-ready for actual contract negotiations.

CONTRACT TEXT:
{contract_text}

USER CONTEXT:
- Agreement Type: {agreement_type}
- User's Role: {user_role} (analyzing from this perspective but providing both sides)
- Risk Tolerance: {risk_tolerance}

CRITICAL REQUIREMENTS FOR THOROUGHNESS:

1. **VOLUME**: For a typical 10-page agreement, generate 50-100+ distinct entries. Each section should have MULTIPLE items.

2. **GRANULARITY**: Break down EVERY section into its component parts:
   - Section 8.2(a) first part → one item
   - Section 8.2(a) second part → another item
   - Section 8.2(b) → another item
   - Missing clause that should be added → mark as "new" in subpart

3. **SUGGESTED ADDITIONS**: Include items for clauses that SHOULD exist but DON'T. Mark these with subpart="new".
   - Example: If no data deletion clause exists, add an entry suggesting one

4. **FULL COVERAGE**: Every numbered section, subsection, and paragraph needs analysis. Do not skip any.

Provide your analysis in the following JSON format:

{{
    "agreement_summary": {{
        "title": "Full agreement title",
        "agreement_type": "Type of agreement (SaaS, MSA, NDA, etc.)",
        "parties": "Detailed description of the parties and their roles",
        "purpose": "Comprehensive description of what this agreement governs",
        "key_dates": "All dates, terms, renewal periods mentioned",
        "governing_law": "Jurisdiction and governing law if specified",
        "overall_risk_level": "High/Medium/Low with explanation",
        "critical_issues_count": number,
        "executive_summary": "2-3 paragraph summary of the key negotiation points and overall assessment"
    }},
    "clauses": [
        {{
            "section_reference": "Exact section number (e.g., '2.1', '3.4(a)', 'Schedule A')",
            "subpart": "Subsection if applicable (e.g., '(a)', '(ii)', 'first part', 'second part', or 'new' for suggested additions)",
            "clause_title": "Descriptive name of the specific issue being addressed",
            "original_language": "EXACT text from the contract for this specific subpart. Quote the FULL relevant language, not a summary. For 'new' items, provide the suggested new language to add.",
            "customer_issues": [
                "• First specific concern customers have with this clause",
                "• Second concern - be detailed and practical",
                "• Third concern - include real-world scenarios",
                "• Fourth concern if applicable",
                "• Fifth concern if applicable"
            ],
            "customer_edits_to_consider": [
                "• Specific edit #1: '[Exact suggested contract language to add, modify, or delete]' - Explanation of when to use this edit",
                "• Specific edit #2: '[Alternative language option]' - Explanation of the different approach",
                "• Specific edit #3: If the clause is acceptable as-is, suggest protections to add elsewhere"
            ],
            "provider_issues": [
                "• First specific concern providers/vendors have",
                "• Second concern from the provider perspective",
                "• Third concern - why they want it this way",
                "• Fourth concern if applicable"
            ],
            "provider_edits_to_consider": [
                "• Specific edit #1: '[Exact language providers would want]' - Why this protects their interests",
                "• Specific edit #2: '[Alternative approach]' - Trade-offs involved"
            ],
            "preferred_position": {{
                "description": "Detailed description of the ideal outcome for the {user_role}",
                "sample_language": "Complete, ready-to-use contract language for the preferred position. This should be full sentences/paragraphs that could be inserted directly into the contract."
            }},
            "fallback_positions": [
                {{
                    "position_number": 1,
                    "description": "First fallback - what to accept if preferred fails",
                    "sample_language": "Complete fallback language ready for use",
                    "conditions": "Specific circumstances when this fallback is appropriate",
                    "trade_offs": "What you're giving up with this fallback"
                }},
                {{
                    "position_number": 2,
                    "description": "Second fallback - further compromise",
                    "sample_language": "Language for this fallback position",
                    "conditions": "When to use this",
                    "trade_offs": "What you're giving up"
                }}
            ],
            "positions_to_avoid": [
                {{
                    "description": "Specific position that should never be accepted",
                    "reason": "Detailed explanation of why this is problematic - include specific risks and consequences",
                    "red_flag_language": "Specific phrases or terms that indicate this bad position"
                }}
            ],
            "risk_level": "Red/Yellow/Green",
            "risk_explanation": "Detailed explanation of why this risk level was assigned. What could go wrong? What's the potential exposure?",
            "approval_required": "None/Legal/Manager/Executive/Board - with explanation of why this level",
            "negotiation_tips": [
                "• Specific tip #1 for negotiating this clause",
                "• Tip #2 - include talking points",
                "• Tip #3 - common counterarguments and how to respond",
                "• Tip #4 - leverage points or trade-offs to consider"
            ],
            "related_clauses": "Other sections in the agreement that interact with or affect this clause"
        }}
    ],
    "definitions": [
        {{
            "term": "Defined term exactly as it appears",
            "definition": "Full definition from the contract",
            "importance": "Why this definition matters and how it affects other provisions",
            "customer_considerations": "How customers should think about this definition",
            "provider_considerations": "How providers typically use this definition",
            "suggested_modifications": "Any changes to consider for this definition"
        }}
    ],
    "quick_reference": {{
        "deal_breakers": [
            "Specific clause/issue that is a deal breaker with brief explanation"
        ],
        "high_priority_items": [
            "Items requiring executive or legal approval"
        ],
        "standard_acceptable_terms": [
            "Terms that are generally acceptable as-is"
        ],
        "common_negotiation_points": [
            "Clauses that are typically negotiated in this type of agreement"
        ],
        "recommended_order_of_negotiation": [
            "Suggested sequence for addressing issues based on importance and dependencies"
        ]
    }},
    "negotiation_strategy": {{
        "opening_position": "Recommended approach for starting negotiations",
        "key_leverage_points": ["Points where {user_role} has negotiating leverage"],
        "potential_trade_offs": ["Issues that could be traded against each other"],
        "walk_away_triggers": ["Specific terms that should trigger walking away from the deal"],
        "timing_considerations": "Any time-sensitive aspects to consider"
    }}
}}

IMPORTANT GUIDELINES:
1. QUOTE the actual contract language - do not summarize or paraphrase
2. Provide MULTIPLE bullet points for each issues section (minimum 3-5)
3. Include SPECIFIC, ready-to-use contract language in all edit suggestions
4. Be THOROUGH - analyze every significant provision
5. Make it ACTIONABLE - a negotiator should be able to use this directly
6. Consider BOTH parties' perspectives comprehensively
7. Include PRACTICAL negotiation tactics, not just legal analysis

The output must be valid JSON. Be extremely thorough - this playbook should be comprehensive enough to serve as the sole reference document for negotiating this agreement."""


def analyze_contract(
    contract_text: str,
    agreement_type: str = "General Agreement",
    user_role: str = "Customer",
    risk_tolerance: str = "Moderate"
) -> dict:
    """
    Analyze contract text and generate comprehensive playbook content.

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
    # Always use chunked approach for better progress tracking
    # Smaller chunks = more frequent progress updates
    chunk_size = 15000  # ~15k chars per chunk for granular progress

    # For very short documents, use single analysis
    if len(contract_text) < chunk_size:
        if progress_callback:
            progress_callback(20, "Analyzing contract with AI...")
        result = analyze_contract(contract_text, agreement_type, user_role, risk_tolerance)
        if progress_callback:
            progress_callback(100, "Analysis complete")
        return result

    # For longer documents, chunk and combine
    chunks = []
    for i in range(0, len(contract_text), chunk_size):
        chunks.append(contract_text[i:i + chunk_size])

    all_clauses = []
    all_definitions = []
    agreement_summary = None
    negotiation_strategy = None

    # Status messages that rotate to show activity
    status_messages = [
        "Analyzing agreement structure...",
        "Reviewing contract provisions...",
        "Evaluating key terms...",
        "Generating negotiation guidance...",
        "Processing document sections...",
        "Identifying risk areas...",
        "Building playbook entries...",
        "Analyzing contractual obligations...",
    ]

    for idx, chunk in enumerate(chunks):
        if progress_callback:
            progress = int((idx + 1) / len(chunks) * 80)
            # Rotate through status messages
            message = status_messages[idx % len(status_messages)]
            progress_callback(progress, message)

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

        if not negotiation_strategy and "negotiation_strategy" in chunk_result:
            negotiation_strategy = chunk_result["negotiation_strategy"]

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
        section = clause.get("section_reference", "")
        item = f"{title} (Section {section})" if section else title

        if risk == "red":
            deal_breakers.append(item)
        elif risk == "yellow":
            high_priority.append(item)
        else:
            standard_terms.append(item)

    combined_result = {
        "agreement_summary": agreement_summary or {
            "title": "Contract Analysis",
            "agreement_type": agreement_type,
            "parties": "Not specified",
            "purpose": "Contract playbook analysis",
            "key_dates": "Not specified",
            "governing_law": "Not specified",
            "overall_risk_level": "Medium",
            "critical_issues_count": len(deal_breakers),
            "executive_summary": "Analysis completed. Review the clause-by-clause breakdown for detailed guidance."
        },
        "clauses": all_clauses,
        "definitions": unique_definitions,
        "quick_reference": {
            "deal_breakers": deal_breakers[:15],
            "high_priority_items": high_priority[:15],
            "standard_acceptable_terms": standard_terms[:15],
            "common_negotiation_points": [c.get("clause_title", "") for c in all_clauses[:10] if c.get("risk_level", "").lower() in ["red", "yellow"]],
            "recommended_order_of_negotiation": [c.get("clause_title", "") for c in sorted(all_clauses, key=lambda x: 0 if x.get("risk_level", "").lower() == "red" else 1 if x.get("risk_level", "").lower() == "yellow" else 2)[:10]]
        },
        "negotiation_strategy": negotiation_strategy or {
            "opening_position": "Start with highest-risk items to gauge counterparty flexibility",
            "key_leverage_points": ["Review clause analysis for specific leverage points"],
            "potential_trade_offs": ["See individual clause analyses for trade-off opportunities"],
            "walk_away_triggers": deal_breakers[:5] if deal_breakers else ["No critical deal breakers identified"],
            "timing_considerations": "Standard negotiation timeline applies"
        }
    }

    if progress_callback:
        progress_callback(100, "Analysis complete")

    return combined_result
