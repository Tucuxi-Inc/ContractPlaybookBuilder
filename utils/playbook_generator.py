"""
AI-powered playbook generation using multiple LLM providers.

This module generates comprehensive contract playbooks with detailed analysis
matching professional legal playbook standards, organized by contract topic.

Supported providers: Anthropic Claude, OpenAI GPT, Google Gemini.
"""
import json
import re
from anthropic import Anthropic
from openai import OpenAI
from google import genai
import config


def get_anthropic_client():
    """Get Anthropic client with API key from config."""
    api_key = config.ANTHROPIC_API_KEY
    if not api_key:
        raise ValueError(
            "Anthropic API key not found. Please set the ANTHROPIC_API_KEY environment variable."
        )
    return Anthropic(api_key=api_key)


def get_openai_client():
    """Get OpenAI client with API key from config."""
    api_key = config.OPENAI_API_KEY
    if not api_key:
        raise ValueError(
            "OpenAI API key not found. Please set the OPENAI_API_KEY environment variable."
        )
    return OpenAI(api_key=api_key)


def get_google_client():
    """Get Google GenAI client with API key from config."""
    api_key = config.GOOGLE_API_KEY
    if not api_key:
        raise ValueError(
            "Google API key not found. Please set the GOOGLE_API_KEY environment variable."
        )
    return genai.Client(api_key=api_key)


# Contract topic categories for organizing the playbook
CONTRACT_TOPICS = [
    "Definitions",
    "Solution/Services",
    "Licenses & Restrictions",
    "Proprietary Rights/IP",
    "Financial Terms",
    "Confidentiality",
    "Data Security & Privacy",
    "Warranties",
    "Indemnification",
    "Limitation of Liability",
    "Term & Termination",
    "General Provisions",
    "Exhibits & Schedules"
]


SYSTEM_PROMPT = """You are an expert contract attorney with 25+ years of experience creating comprehensive contract playbooks for Fortune 500 companies. You analyze contracts with extraordinary depth and practical insight.

Your analysis must be:
1. THOROUGH - Every significant clause gets detailed treatment
2. PRACTICAL - Real negotiation guidance, not academic analysis
3. BALANCED - Both customer and provider perspectives
4. ACTIONABLE - Ready-to-use fallback language and hard limits

For each clause you analyze, provide:
- The exact contract language (quoted)
- Why this clause exists and matters (business context)
- What customers typically want to change
- What providers need to protect
- Specific acceptable modifications
- Ready-to-use fallback language
- Clear "do not accept" boundaries"""


TOPICS_TO_ANALYZE = [
    ("Definitions", "definitions, defined terms, and interpretation provisions"),
    ("Solution/Services", "the solution, services, platform, software, or product being provided"),
    ("Licenses & Restrictions", "license grants, usage rights, restrictions, and permitted uses"),
    ("Proprietary Rights/IP", "intellectual property, ownership, proprietary rights, and IP assignments"),
    ("Financial Terms", "fees, payment terms, pricing, invoicing, and financial obligations"),
    ("Confidentiality", "confidentiality, non-disclosure, and information protection"),
    ("Data Security & Privacy", "data protection, security, privacy, data processing, and compliance"),
    ("Warranties", "representations, warranties, disclaimers, and guarantees"),
    ("Indemnification", "indemnification, defense, and hold harmless provisions"),
    ("Limitation of Liability", "liability caps, exclusions, consequential damages, and limitations"),
    ("Term & Termination", "term, renewal, termination rights, and effects of termination"),
    ("General Provisions", "miscellaneous provisions like assignment, notices, force majeure, amendments"),
    ("Exhibits & Schedules", "exhibits, schedules, appendices, and attachments")
]


def _build_overview_prompt(contract_text, agreement_type, user_role, risk_tolerance):
    """Build the overview analysis prompt."""
    return f"""Analyze this contract and provide a comprehensive overview.

CONTRACT TEXT:
{contract_text[:50000]}

CONTEXT:
- Agreement Type: {agreement_type}
- Analyzing from: {user_role} perspective
- Risk Tolerance: {risk_tolerance}

Provide your analysis as JSON with this structure:
{{
    "title": "Full title of the agreement",
    "parties": "Description of the parties",
    "effective_date": "If specified",
    "governing_law": "Jurisdiction if specified",
    "key_principles": [
        "Key principle 1 about this agreement",
        "Key principle 2",
        "Key principle 3",
        "Key principle 4"
    ],
    "executive_summary": "2-3 paragraph overview of the agreement and key negotiation considerations",
    "sections_found": ["List of major sections/topics found in the contract"]
}}"""


def _build_topic_prompt(contract_text, topic_name, topic_description, agreement_type, user_role, risk_tolerance):
    """Build the topic analysis prompt."""
    return f"""Analyze this contract focusing specifically on {topic_description}.

CONTRACT TEXT:
{contract_text[:80000]}

CONTEXT:
- Agreement Type: {agreement_type}
- Analyzing from: {user_role} perspective
- Risk Tolerance: {risk_tolerance}

For each relevant clause or provision related to {topic_name}, provide detailed analysis.

Return JSON with this structure:
{{
    "topic": "{topic_name}",
    "clauses": [
        {{
            "section": "Section number (e.g., '2.1', 'III', 'Schedule A')",
            "subsection": "Subsection if applicable",
            "issue": "Brief title describing the specific issue",
            "current_language": "EXACT quoted text from the contract",
            "purpose_rationale": "Why this clause exists and its business purpose",
            "customer_concerns": "• Bullet point 1\\n• Bullet point 2\\n• Bullet point 3",
            "customer_edits_to_watch": "• Edit 1\\n• Edit 2\\n• Edit 3",
            "provider_position": "The provider's perspective and what they need to protect",
            "acceptable_modifications": "• Modification 1\\n• Modification 2",
            "fallback_language": "Ready-to-use alternative contract language",
            "do_not_accept": "• Hard limit 1\\n• Hard limit 2",
            "notes": "Additional considerations or context"
        }}
    ],
    "hard_limits": [
        {{
            "issue": "Brief description",
            "limit": "What requires executive approval"
        }}
    ]
}}

Be thorough - analyze EVERY clause related to {topic_name}. Include both explicit provisions AND important omissions that should be addressed."""


def _extract_json(text):
    """Extract JSON object from LLM response text."""
    json_match = re.search(r'\{[\s\S]*\}', text)
    if json_match:
        return json.loads(json_match.group())
    return None


# =============================================================================
# Anthropic Claude implementation
# =============================================================================

def analyze_contract_with_claude(contract_text, agreement_type, user_role, risk_tolerance, progress_callback=None):
    """Analyze contract using Anthropic Claude API."""
    client = get_anthropic_client()

    if progress_callback:
        progress_callback(5, "Preparing contract analysis...")

    overview_prompt = _build_overview_prompt(contract_text, agreement_type, user_role, risk_tolerance)

    if progress_callback:
        progress_callback(10, "Analyzing agreement structure...")

    overview_response = client.messages.create(
        model=config.ANTHROPIC_MODEL,
        max_tokens=4096,
        messages=[{"role": "user", "content": overview_prompt}],
        system=SYSTEM_PROMPT
    )

    try:
        overview = _extract_json(overview_response.content[0].text) or {
            "title": agreement_type, "key_principles": [], "executive_summary": ""
        }
    except (json.JSONDecodeError, IndexError):
        overview = {"title": agreement_type, "key_principles": [], "executive_summary": ""}

    all_topics = {}
    quick_reference = []

    for idx, (topic_name, topic_description) in enumerate(TOPICS_TO_ANALYZE):
        if progress_callback:
            progress = 15 + int((idx / len(TOPICS_TO_ANALYZE)) * 70)
            progress_callback(progress, f"Analyzing {topic_name}...")

        topic_prompt = _build_topic_prompt(
            contract_text, topic_name, topic_description, agreement_type, user_role, risk_tolerance
        )

        try:
            topic_response = client.messages.create(
                model=config.ANTHROPIC_MODEL,
                max_tokens=8192,
                messages=[{"role": "user", "content": topic_prompt}],
                system=SYSTEM_PROMPT
            )
            topic_data = _extract_json(topic_response.content[0].text)
            if topic_data:
                if topic_data.get("clauses"):
                    all_topics[topic_name] = topic_data["clauses"]
                if topic_data.get("hard_limits"):
                    quick_reference.extend(topic_data["hard_limits"])
        except Exception as e:
            print(f"Error analyzing {topic_name}: {e}")
            continue

    if progress_callback:
        progress_callback(90, "Compiling playbook...")

    return _build_playbook(overview, all_topics, quick_reference, agreement_type, user_role)


# =============================================================================
# OpenAI GPT implementation
# =============================================================================

def analyze_contract_with_openai(contract_text, agreement_type, user_role, risk_tolerance, progress_callback=None):
    """Analyze contract using OpenAI API."""
    client = get_openai_client()

    if progress_callback:
        progress_callback(5, "Preparing contract analysis...")

    overview_prompt = _build_overview_prompt(contract_text, agreement_type, user_role, risk_tolerance)

    if progress_callback:
        progress_callback(10, "Analyzing agreement structure...")

    overview_response = client.chat.completions.create(
        model=config.OPENAI_MODEL,
        max_tokens=4096,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": overview_prompt}
        ]
    )

    try:
        overview = _extract_json(overview_response.choices[0].message.content) or {
            "title": agreement_type, "key_principles": [], "executive_summary": ""
        }
    except (json.JSONDecodeError, IndexError):
        overview = {"title": agreement_type, "key_principles": [], "executive_summary": ""}

    all_topics = {}
    quick_reference = []

    for idx, (topic_name, topic_description) in enumerate(TOPICS_TO_ANALYZE):
        if progress_callback:
            progress = 15 + int((idx / len(TOPICS_TO_ANALYZE)) * 70)
            progress_callback(progress, f"Analyzing {topic_name}...")

        topic_prompt = _build_topic_prompt(
            contract_text, topic_name, topic_description, agreement_type, user_role, risk_tolerance
        )

        try:
            topic_response = client.chat.completions.create(
                model=config.OPENAI_MODEL,
                max_tokens=8192,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": topic_prompt}
                ]
            )
            topic_data = _extract_json(topic_response.choices[0].message.content)
            if topic_data:
                if topic_data.get("clauses"):
                    all_topics[topic_name] = topic_data["clauses"]
                if topic_data.get("hard_limits"):
                    quick_reference.extend(topic_data["hard_limits"])
        except Exception as e:
            print(f"Error analyzing {topic_name}: {e}")
            continue

    if progress_callback:
        progress_callback(90, "Compiling playbook...")

    return _build_playbook(overview, all_topics, quick_reference, agreement_type, user_role)


# =============================================================================
# Google Gemini implementation
# =============================================================================

def analyze_contract_with_google(contract_text, agreement_type, user_role, risk_tolerance, progress_callback=None):
    """Analyze contract using Google Gemini API."""
    client = get_google_client()

    if progress_callback:
        progress_callback(5, "Preparing contract analysis...")

    overview_prompt = _build_overview_prompt(contract_text, agreement_type, user_role, risk_tolerance)

    if progress_callback:
        progress_callback(10, "Analyzing agreement structure...")

    overview_response = client.models.generate_content(
        model=config.GOOGLE_MODEL,
        contents=overview_prompt,
        config=genai.types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            max_output_tokens=4096
        )
    )

    try:
        overview = _extract_json(overview_response.text) or {
            "title": agreement_type, "key_principles": [], "executive_summary": ""
        }
    except (json.JSONDecodeError, IndexError):
        overview = {"title": agreement_type, "key_principles": [], "executive_summary": ""}

    all_topics = {}
    quick_reference = []

    for idx, (topic_name, topic_description) in enumerate(TOPICS_TO_ANALYZE):
        if progress_callback:
            progress = 15 + int((idx / len(TOPICS_TO_ANALYZE)) * 70)
            progress_callback(progress, f"Analyzing {topic_name}...")

        topic_prompt = _build_topic_prompt(
            contract_text, topic_name, topic_description, agreement_type, user_role, risk_tolerance
        )

        try:
            topic_response = client.models.generate_content(
                model=config.GOOGLE_MODEL,
                contents=topic_prompt,
                config=genai.types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT,
                    max_output_tokens=8192
                )
            )
            topic_data = _extract_json(topic_response.text)
            if topic_data:
                if topic_data.get("clauses"):
                    all_topics[topic_name] = topic_data["clauses"]
                if topic_data.get("hard_limits"):
                    quick_reference.extend(topic_data["hard_limits"])
        except Exception as e:
            print(f"Error analyzing {topic_name}: {e}")
            continue

    if progress_callback:
        progress_callback(90, "Compiling playbook...")

    return _build_playbook(overview, all_topics, quick_reference, agreement_type, user_role)


# =============================================================================
# Shared helpers
# =============================================================================

def _build_playbook(overview, all_topics, quick_reference, agreement_type, user_role):
    """Build the final playbook dict from analyzed data."""
    return {
        "overview": {
            "title": overview.get("title", agreement_type),
            "agreement_type": agreement_type,
            "perspective": user_role,
            "parties": overview.get("parties", ""),
            "effective_date": overview.get("effective_date", ""),
            "governing_law": overview.get("governing_law", ""),
            "key_principles": overview.get("key_principles", []),
            "executive_summary": overview.get("executive_summary", ""),
            "how_to_use": [
                "Navigate to the relevant section tab based on the clause being negotiated",
                "Review the 'Purpose/Rationale' to understand why the clause exists",
                "Check 'Customer Concerns' or 'Provider Position' based on your role",
                "Use 'Acceptable Modifications' for standard negotiation moves",
                "Reference 'Fallback Language' when proposing alternatives",
                "Never accept terms listed in 'Do Not Accept' without executive approval"
            ]
        },
        "topics": all_topics,
        "quick_reference": quick_reference
    }


def analyze_contract_chunked(
    contract_text: str,
    agreement_type: str = "General Agreement",
    user_role: str = "Customer",
    risk_tolerance: str = "Moderate",
    progress_callback=None
) -> dict:
    """
    Main entry point - routes to the correct provider based on config.AI_PROVIDER.
    """
    provider = config.AI_PROVIDER

    if provider == "openai":
        return analyze_contract_with_openai(
            contract_text=contract_text,
            agreement_type=agreement_type,
            user_role=user_role,
            risk_tolerance=risk_tolerance,
            progress_callback=progress_callback
        )
    elif provider == "google":
        return analyze_contract_with_google(
            contract_text=contract_text,
            agreement_type=agreement_type,
            user_role=user_role,
            risk_tolerance=risk_tolerance,
            progress_callback=progress_callback
        )
    else:
        # Default to Anthropic
        return analyze_contract_with_claude(
            contract_text=contract_text,
            agreement_type=agreement_type,
            user_role=user_role,
            risk_tolerance=risk_tolerance,
            progress_callback=progress_callback
        )
