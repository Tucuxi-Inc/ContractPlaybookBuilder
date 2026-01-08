# Local AI Guide: Using Ollama for Contract Analysis

This guide explains how to modify the Contract Playbook Builder to use **Ollama** and local AI models instead of OpenAI's API. This allows you to:

- Process contracts **completely offline**
- Maintain **full data privacy** (no data leaves your machine)
- Avoid **API costs** (free after initial setup)
- Work without an **internet connection**

---

## Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Step 1: Install Ollama](#step-1-install-ollama)
- [Step 2: Download a Model](#step-2-download-a-model)
- [Step 3: Modify the Application](#step-3-modify-the-application)
- [Step 4: Test the Integration](#step-4-test-the-integration)
- [Model Recommendations](#model-recommendations)
- [Performance Considerations](#performance-considerations)
- [Coding Co-Pilot Instructions](#coding-co-pilot-instructions)

---

## Overview

The Contract Playbook Builder currently uses OpenAI's GPT-4o model via their API. To use local models instead, you'll need to:

1. Install **Ollama** (a local LLM runner)
2. Download a capable model (we recommend **Llama 3.1** or **Mistral**)
3. Modify `utils/playbook_generator.py` to use Ollama's API instead of OpenAI's

**Difficulty Level**: Intermediate (requires editing Python code)

**Time Required**: 30-60 minutes (plus model download time)

---

## Prerequisites

Before starting, ensure you have:

- The Contract Playbook Builder installed and working
- At least **8GB RAM** (16GB+ recommended for larger models)
- At least **10GB free disk space** for model storage
- A relatively modern CPU (or GPU for faster inference)

---

## Step 1: Install Ollama

### Mac

```bash
# Using Homebrew
brew install ollama

# Or download directly from https://ollama.ai/download
```

### Windows

1. Download the installer from https://ollama.ai/download
2. Run the installer
3. Ollama will run as a background service

### Linux

```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

### Verify Installation

```bash
ollama --version
```

You should see a version number like `ollama version 0.1.x`.

### Start Ollama Service

```bash
# Start the Ollama service (runs on http://localhost:11434)
ollama serve
```

On Mac/Windows, Ollama typically starts automatically. On Linux, you may need to run `ollama serve` in a separate terminal.

---

## Step 2: Download a Model

Ollama needs to download a language model before you can use it. Open a new terminal and run:

### Recommended: Llama 3.1 8B (Best balance of quality and speed)

```bash
ollama pull llama3.1:8b
```

### Alternative: Mistral 7B (Faster, slightly less capable)

```bash
ollama pull mistral:7b
```

### Alternative: Llama 3.1 70B (Highest quality, requires 48GB+ RAM)

```bash
ollama pull llama3.1:70b
```

**Download times**: 8B models are ~4-5GB and take 5-15 minutes depending on your connection.

### Verify the Model Works

```bash
ollama run llama3.1:8b "Hello, can you help me analyze a contract?"
```

You should see a response from the model.

---

## Step 3: Modify the Application

You need to modify `utils/playbook_generator.py` to use Ollama instead of OpenAI.

### Option A: Manual Modification

Replace the contents of `utils/playbook_generator.py` with the code in the next section.

### Option B: Use a Coding Co-Pilot

See [Coding Co-Pilot Instructions](#coding-co-pilot-instructions) below for prompts you can give to Claude Code, GitHub Copilot, or other AI coding assistants.

---

### Modified playbook_generator.py for Ollama

Create a backup of the original file first:

```bash
cp utils/playbook_generator.py utils/playbook_generator_openai.py
```

Then replace `utils/playbook_generator.py` with this code:

```python
"""
AI-powered playbook generation using Ollama (local models).
"""
import json
import os
import requests
import config


# Ollama API endpoint (default local installation)
OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "llama3.1:8b")


def check_ollama_available():
    """Check if Ollama is running and accessible."""
    try:
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False


def generate_with_ollama(prompt: str, system_prompt: str = "") -> str:
    """
    Generate text using Ollama's API.

    Args:
        prompt: The user prompt
        system_prompt: Optional system prompt for context

    Returns:
        The generated text response
    """
    if not check_ollama_available():
        raise ConnectionError(
            f"Ollama is not running. Please start it with 'ollama serve' "
            f"or check that it's accessible at {OLLAMA_BASE_URL}"
        )

    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "system": system_prompt,
        "stream": False,
        "options": {
            "temperature": 0.3,
            "num_predict": 16000,
        }
    }

    response = requests.post(
        f"{OLLAMA_BASE_URL}/api/generate",
        json=payload,
        timeout=600  # 10 minute timeout for long documents
    )

    if response.status_code != 200:
        raise Exception(f"Ollama API error: {response.status_code} - {response.text}")

    result = response.json()
    return result.get("response", "")


SYSTEM_PROMPT = """You are an expert contract attorney and negotiation strategist specializing in creating comprehensive contract playbooks. Your role is to analyze contract text and generate detailed playbook entries that help legal teams and business professionals negotiate effectively.

For each clause or section you analyze, provide:
1. Clear issue identification
2. Business context explaining why this matters
3. Balanced perspective (both customer/buyer and provider/vendor viewpoints)
4. Specific negotiation guidance with sample language
5. Risk classification (Red = deal-breaker, Yellow = needs approval, Green = acceptable)

Your output should be practical, actionable, and usable by both experienced attorneys and business professionals with limited legal training.

IMPORTANT: You must respond with valid JSON only. No additional text or explanations outside the JSON structure."""


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

Be thorough and analyze ALL significant clauses in the contract. Focus on practical, actionable guidance. Ensure the JSON is valid and complete. Respond with ONLY the JSON, no other text."""


def analyze_contract(
    contract_text: str,
    agreement_type: str = "General Agreement",
    user_role: str = "Customer",
    risk_tolerance: str = "Moderate"
) -> dict:
    """
    Analyze contract text and generate playbook content using Ollama.

    Args:
        contract_text: The extracted text from the uploaded agreement
        agreement_type: Type of agreement (SaaS, Services, NDA, etc.)
        user_role: Whether user is Customer/Buyer or Provider/Vendor
        risk_tolerance: Low, Moderate, or High risk tolerance

    Returns:
        dict containing the full playbook analysis
    """
    # Truncate very long contracts to fit within context limits
    # Local models typically have smaller context windows
    max_chars = 30000  # Smaller limit for local models
    if len(contract_text) > max_chars:
        contract_text = contract_text[:max_chars] + "\n\n[Document truncated due to length...]"

    prompt = ANALYSIS_PROMPT.format(
        contract_text=contract_text,
        agreement_type=agreement_type,
        user_role=user_role,
        risk_tolerance=risk_tolerance
    )

    result_text = generate_with_ollama(prompt, SYSTEM_PROMPT)

    try:
        playbook_data = json.loads(result_text)
    except json.JSONDecodeError as e:
        # Try to extract JSON from the response
        import re
        json_match = re.search(r'\{[\s\S]*\}', result_text)
        if json_match:
            try:
                playbook_data = json.loads(json_match.group())
            except json.JSONDecodeError:
                raise ValueError(f"Failed to parse AI response as JSON: {e}\nResponse was: {result_text[:500]}...")
        else:
            raise ValueError(f"Failed to parse AI response as JSON: {e}\nResponse was: {result_text[:500]}...")

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
    if len(contract_text) < 20000:
        if progress_callback:
            progress_callback(50, "Analyzing contract with local AI...")
        result = analyze_contract(contract_text, agreement_type, user_role, risk_tolerance)
        if progress_callback:
            progress_callback(100, "Analysis complete")
        return result

    # For longer documents, chunk and combine
    # Split into chunks of roughly 15k characters (smaller for local models)
    chunk_size = 15000
    chunks = []
    for i in range(0, len(contract_text), chunk_size):
        chunks.append(contract_text[i:i + chunk_size])

    all_clauses = []
    all_definitions = []
    agreement_summary = None

    for idx, chunk in enumerate(chunks):
        if progress_callback:
            progress = int((idx + 1) / len(chunks) * 80)
            progress_callback(progress, f"Analyzing section {idx + 1} of {len(chunks)} with local AI...")

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
```

---

### Update config.py

Add Ollama configuration to `config.py`:

```python
# Ollama settings (for local AI)
OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "llama3.1:8b")
```

---

## Step 4: Test the Integration

1. Make sure Ollama is running:
   ```bash
   ollama serve
   ```

2. Start the application:
   ```bash
   python app.py
   ```

3. Upload a short test document and generate a playbook.

**Note**: Local models are slower than OpenAI's API. Expect:
- 8B models: 2-5 minutes for a 10-page document
- 70B models: 5-15 minutes for a 10-page document

---

## Model Recommendations

| Model | Size | RAM Required | Speed | Quality | Best For |
|-------|------|--------------|-------|---------|----------|
| `llama3.1:8b` | 4.7GB | 8GB | Fast | Good | Most users, daily use |
| `mistral:7b` | 4.1GB | 8GB | Fastest | Good | Quick analysis, older hardware |
| `llama3.1:70b` | 40GB | 48GB+ | Slow | Excellent | Maximum quality, powerful hardware |
| `mixtral:8x7b` | 26GB | 32GB | Medium | Very Good | Balance of quality and speed |
| `codellama:34b` | 19GB | 24GB | Medium | Good | Technical contracts |

### GPU Acceleration

If you have an NVIDIA GPU with sufficient VRAM, Ollama will automatically use it for faster inference:

- 8B models: 6GB+ VRAM
- 70B models: 40GB+ VRAM (or use CPU offloading)

---

## Performance Considerations

### Improving Speed

1. **Use a smaller model** for faster processing
2. **Enable GPU acceleration** if you have a compatible GPU
3. **Reduce chunk size** in the code for more frequent progress updates
4. **Use SSD storage** for faster model loading

### Improving Quality

1. **Use a larger model** (70B vs 8B)
2. **Adjust temperature** in the code (lower = more consistent, higher = more creative)
3. **Increase context window** if your model supports it

### Memory Issues

If you're running out of RAM:

```bash
# Use a quantized (smaller) version of the model
ollama pull llama3.1:8b-q4_0
```

Quantized models use less memory but may have slightly lower quality.

---

## Coding Co-Pilot Instructions

Use these prompts with Claude Code, GitHub Copilot, Cursor, or other AI coding assistants to help make the modifications.

### Prompt for Claude Code / Cursor

```
I want to modify the Contract Playbook Builder to use Ollama instead of OpenAI.

Current setup:
- The app uses OpenAI's API in utils/playbook_generator.py
- It calls client.chat.completions.create() with model "gpt-4o"
- The OpenAI client is initialized with the OPENAI_API_KEY env variable

Desired changes:
1. Replace OpenAI API calls with Ollama API calls (http://localhost:11434/api/generate)
2. Add configuration for OLLAMA_MODEL (default: llama3.1:8b) and OLLAMA_BASE_URL
3. Keep the same prompt structure and JSON output format
4. Add a check to verify Ollama is running before processing
5. Reduce the max character limit from 100000 to 30000 (local models have smaller context)
6. Reduce chunk size from 40000 to 15000 for the chunked analysis

The Ollama API format is:
POST http://localhost:11434/api/generate
{
    "model": "llama3.1:8b",
    "prompt": "user prompt here",
    "system": "system prompt here",
    "stream": false,
    "options": {
        "temperature": 0.3,
        "num_predict": 16000
    }
}

Response format:
{
    "response": "the generated text"
}

Please modify utils/playbook_generator.py to use Ollama instead of OpenAI, keeping all the existing functionality for contract analysis and JSON parsing.
```

### Prompt for GitHub Copilot

Add this comment at the top of `playbook_generator.py` and let Copilot generate the code:

```python
# TODO: Replace OpenAI API with Ollama API
# Ollama endpoint: http://localhost:11434/api/generate
# Model: llama3.1:8b (configurable via OLLAMA_MODEL env var)
# Keep same prompt structure, reduce context limits for local models
# Add connection check before processing
```

### Prompt for General AI Assistants

```
I need to modify a Python Flask application to use Ollama (local LLM) instead of OpenAI.

The current code uses:
- openai Python package
- client.chat.completions.create() method
- GPT-4o model

I want to change it to:
- Use requests library to call Ollama's REST API
- Endpoint: POST http://localhost:11434/api/generate
- Model: llama3.1:8b (or configurable)
- Keep the same prompts and JSON output format

Key differences:
- Ollama uses a different API format (see their docs)
- Local models have smaller context windows (use 30k chars max instead of 100k)
- Need to check if Ollama is running before processing
- Response time will be slower, so increase timeouts

Can you help me rewrite the get_openai_client() and analyze_contract() functions to use Ollama instead?
```

---

## Switching Between OpenAI and Ollama

If you want to easily switch between providers, you can create a configuration option:

```python
# In config.py
AI_PROVIDER = os.environ.get("AI_PROVIDER", "openai")  # "openai" or "ollama"
```

Then in `playbook_generator.py`:

```python
import config

if config.AI_PROVIDER == "ollama":
    from utils.playbook_generator_ollama import analyze_contract, analyze_contract_chunked
else:
    from utils.playbook_generator_openai import analyze_contract, analyze_contract_chunked
```

This lets you switch providers with:
```bash
AI_PROVIDER=ollama python app.py
```

---

## Troubleshooting

### "Ollama is not running"

```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# If not, start it
ollama serve
```

### "Model not found"

```bash
# List available models
ollama list

# Pull the model if missing
ollama pull llama3.1:8b
```

### "Out of memory"

- Try a smaller model: `ollama pull llama3.1:8b-q4_0`
- Close other applications
- Reduce the chunk size in the code

### "JSON parsing errors"

Local models sometimes produce malformed JSON. The code includes fallback parsing, but if issues persist:
- Try a different model (Mistral tends to follow JSON formats well)
- Reduce the complexity of your document
- Check the raw output in the terminal for debugging

---

## Additional Resources

- [Ollama Documentation](https://ollama.ai/docs)
- [Ollama Model Library](https://ollama.ai/library)
- [LLM Benchmarks](https://huggingface.co/spaces/lmsys/chatbot-arena-leaderboard)

---

## Support

For issues specific to this local AI integration:
- Open an issue on GitHub with the "local-ai" label
- Include your model, hardware specs, and error messages
