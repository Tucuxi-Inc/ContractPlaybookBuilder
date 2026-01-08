# CLAUDE.md - Contract Playbook Builder

## Project Overview

A web application that allows users to upload any type of template agreement (PDF, Word, Excel) and automatically generates a professional contract playbook in Excel format. The playbook follows industry best practices with clause-by-clause analysis, negotiation guidance, and risk classification.

## Quick Start

```bash
# Navigate to project directory
cd /Users/kevinkeller/Desktop/Contract_Playbook_Builder

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set your OpenAI API key (required for AI-powered analysis)
export OPENAI_API_KEY="your-api-key-here"

# Run the application
python app.py

# Access the web interface
open http://localhost:8005
```

## Key Files

| File | Purpose |
|------|---------|
| `app.py` | Main Flask application entry point |
| `config.py` | Configuration settings (port, API keys, etc.) |
| `requirements.txt` | Python dependencies |
| `templates/` | HTML templates for web interface |
| `static/` | CSS, JavaScript, and assets |
| `utils/document_parser.py` | Parses uploaded agreements |
| `utils/playbook_generator.py` | AI-powered playbook generation |
| `utils/excel_writer.py` | Creates Excel output |

## Architecture

```
User uploads agreement (PDF/DOCX/XLSX)
    ↓
Document Parser extracts text and structure
    ↓
AI Analyzer identifies clauses, issues, risks
    ↓
Playbook Generator creates structured analysis
    ↓
Excel Writer outputs professional playbook
    ↓
User downloads completed playbook
```

## Playbook Output Structure

Generated playbooks include:
- **Overview Sheet**: Agreement summary, key dates, parties
- **Clause Analysis Sheet**: Section-by-section breakdown with:
  - Issue identification
  - Section/clause references
  - Business context explanation
  - Customer perspective and concerns
  - Provider/vendor perspective
  - Preferred position with sample language
  - Fallback positions (acceptable alternatives)
  - Positions to avoid (deal breakers)
  - Risk classification (Red/Yellow/Green)
  - Approval authority guidance
- **Definitions Sheet**: Key terms and their meanings
- **Quick Reference Sheet**: Summary of critical issues

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENAI_API_KEY` | Yes | OpenAI API key for GPT-4 analysis |
| `PORT` | No | Server port (default: 8005) |
| `MAX_FILE_SIZE` | No | Max upload size in MB (default: 50) |

## Common Commands

```bash
# Run development server
python app.py

# Run with debug mode
FLASK_DEBUG=1 python app.py

# Run tests
pytest tests/

# Check code style
flake8 .
```

## Troubleshooting

**Port 8005 already in use:**
```bash
lsof -i :8005  # Find process using port
kill -9 <PID>  # Kill the process
```

**Import errors:**
```bash
pip install -r requirements.txt  # Reinstall dependencies
```

**API key errors:**
```bash
echo $OPENAI_API_KEY  # Verify key is set
```

## Do Not Modify

- `BackgroundDocs/` - Reference materials (not in git)
- Core utility functions without understanding dependencies

## Safe to Adjust

- `config.py` - Application settings
- `templates/` - UI customization
- `static/` - Styling and frontend assets

## Remote Repository

https://github.com/Tucuxi-Inc/ContractPlaybookBuilder
