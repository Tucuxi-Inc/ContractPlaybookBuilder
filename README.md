# Contract Playbook Builder

A web application that automatically generates professional contract playbooks from any template agreement. Upload a PDF, Word document, or Excel file, and receive a comprehensive negotiation playbook following industry best practices.

**Powered by Claude AI** - Uses Anthropic's Claude for intelligent contract analysis.

---

## Table of Contents

- [What is a Contract Playbook?](#what-is-a-contract-playbook)
- [Features](#features)
- [Quick Start](#quick-start)
- [Detailed Setup Guide](#detailed-setup-guide)
- [Configuration](#configuration)
- [How to Use](#how-to-use)
- [Understanding Your Playbook](#understanding-your-playbook)
- [Troubleshooting](#troubleshooting)
- [Project Structure](#project-structure)

---

## What is a Contract Playbook?

A contract playbook is a strategic guide that documents your organization's negotiation positions, risk tolerance, and standard terms for contract negotiations. It helps legal teams, procurement professionals, and business stakeholders:

- **Negotiate consistently** across all deals
- **Save time** by providing pre-approved language and positions
- **Reduce risk** by identifying deal-breakers and acceptable alternatives
- **Empower non-lawyers** to handle routine negotiations
- **Preserve institutional knowledge** about preferred terms

---

## Features

- **Multi-format Upload**: Supports PDF, Word (.docx), and Excel (.xlsx) files
- **Claude AI Analysis**: Uses Anthropic's Claude for deep contract understanding
- **Topic-Based Organization**: Separate sheets for each contract area (Indemnification, Liability, IP, etc.)
- **Professional Output**: Excel playbooks matching industry standards
- **Dual Perspective**: Analysis from both customer and provider viewpoints
- **Actionable Guidance**: Ready-to-use fallback language and hard limits
- **Quick Reference**: Executive summary with deal-breakers and approval requirements

---

## Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/Tucuxi-Inc/ContractPlaybookBuilder.git
cd ContractPlaybookBuilder

# 2. Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure your API key (choose one method)

# Option A: Create .env file (recommended)
cp .env.example .env
# Edit .env and add your Anthropic API key

# Option B: Export environment variable
export ANTHROPIC_API_KEY="your-api-key-here"

# 5. Run the application
python app.py

# 6. Open http://localhost:3005 in your browser
```

---

## Detailed Setup Guide

### Prerequisites

- **Python 3.9+** - [Download Python](https://www.python.org/downloads/)
- **Anthropic API Key** - [Get one here](https://console.anthropic.com/)

### Step 1: Get the Code

```bash
git clone https://github.com/Tucuxi-Inc/ContractPlaybookBuilder.git
cd ContractPlaybookBuilder
```

Or download the ZIP from GitHub and extract it.

### Step 2: Set Up Python Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate      # Mac/Linux
venv\Scripts\activate         # Windows CMD
.\venv\Scripts\Activate.ps1   # Windows PowerShell

# Install dependencies
pip install -r requirements.txt
```

### Step 3: Configure API Key

**Option A: Using .env file (Recommended)**

```bash
# Copy the example file
cp .env.example .env

# Edit .env with your favorite editor
nano .env   # or: code .env, vim .env, etc.
```

Add your Anthropic API key:
```
ANTHROPIC_API_KEY=sk-ant-api03-your-key-here
```

**Option B: Environment Variable**

```bash
# Mac/Linux
export ANTHROPIC_API_KEY="sk-ant-api03-your-key-here"

# Windows CMD
set ANTHROPIC_API_KEY=sk-ant-api03-your-key-here

# Windows PowerShell
$env:ANTHROPIC_API_KEY="sk-ant-api03-your-key-here"
```

### Step 4: Run the Application

```bash
python app.py
```

You should see:
```
============================================================
Contract Playbook Builder
============================================================
Starting server on http://localhost:3005
AI Provider: Anthropic Claude (claude-sonnet-4-20250514)
============================================================
```

Open **http://localhost:3005** in your browser.

---

## Configuration

All configuration can be done via the `.env` file or environment variables.

| Variable | Default | Description |
|----------|---------|-------------|
| `ANTHROPIC_API_KEY` | (required) | Your Anthropic API key |
| `ANTHROPIC_MODEL` | claude-sonnet-4-20250514 | Claude model to use |
| `PORT` | 3005 | Server port |
| `MAX_FILE_SIZE` | 50 | Max upload size in MB |
| `FLASK_DEBUG` | 0 | Set to 1 for debug mode |

### Alternative: OpenAI

If you prefer OpenAI, set these instead:
```
OPENAI_API_KEY=sk-your-openai-key
OPENAI_MODEL=gpt-4o
```

The app will automatically use OpenAI if no Anthropic key is configured.

---

## How to Use

### 1. Upload Your Agreement

- Click **"Choose File"** or drag and drop
- Supported: PDF, Word (.docx), Excel (.xlsx)
- Max size: 50 MB

### 2. Configure Options

- **Agreement Type**: SaaS, MSA, NDA, etc. (helps AI understand context)
- **Your Role**: Customer or Provider (tailors the analysis)
- **Risk Tolerance**: Low, Moderate, or High

### 3. Generate & Download

- Click **"Generate Playbook"**
- Wait 2-5 minutes (progress shown)
- Download the Excel file when complete

---

## Understanding Your Playbook

The generated Excel workbook contains multiple sheets organized by topic:

### Overview Sheet
- Agreement title, parties, governing law
- Key principles and executive summary
- How to use the playbook

### Topic Sheets (Definitions, Indemnification, Liability, etc.)

Each topic sheet contains:

| Column | Description |
|--------|-------------|
| **Section** | Reference to original agreement section |
| **Issue** | Specific contractual issue |
| **Current Language** | Exact text from the agreement |
| **Purpose/Rationale** | Why this clause matters |
| **Customer Concerns** | What buyers worry about |
| **Customer Edits to Watch** | Edits customers typically request |
| **Provider Position** | What vendors need to protect |
| **Acceptable Modifications** | Negotiable changes |
| **Fallback Language** | Ready-to-use alternative text |
| **Do Not Accept** | Hard limits requiring approval |

### Quick Reference Sheet
- Hard limits by topic
- Items requiring executive approval

---

## Troubleshooting

### "API key not configured"

Make sure your `.env` file exists and contains:
```
ANTHROPIC_API_KEY=sk-ant-api03-your-key-here
```

Or export the environment variable before running.

### "Port already in use"

```bash
# Use a different port
PORT=3006 python app.py
```

### "ModuleNotFoundError"

```bash
# Make sure venv is activated and dependencies installed
source venv/bin/activate
pip install -r requirements.txt
```

### Large files timing out

- Files over 50 pages may take 5-10 minutes
- Ensure stable internet connection
- Check terminal for error messages

### PDF not parsing correctly

- Must be text-based (not scanned images)
- Use OCR software for scanned documents
- Remove password protection

---

## Project Structure

```
ContractPlaybookBuilder/
├── app.py                    # Flask application
├── config.py                 # Configuration (loads .env)
├── requirements.txt          # Python dependencies
├── .env.example              # Example environment file
├── .env                      # Your local config (not in git)
├── README.md                 # This file
├── templates/
│   └── index.html            # Web interface
├── static/
│   ├── css/style.css
│   └── js/main.js
├── utils/
│   ├── document_parser.py    # PDF/Word/Excel extraction
│   ├── playbook_generator.py # Claude AI analysis
│   └── excel_writer.py       # Excel output generation
├── uploads/                  # Temporary uploads (auto-cleaned)
└── output/                   # Generated playbooks
```

---

## API Costs

Typical cost per playbook using Claude:
- Short contracts (1-10 pages): ~$0.05-0.15
- Medium contracts (10-30 pages): ~$0.15-0.40
- Long contracts (30-100 pages): ~$0.40-1.00

---

## Security Notes

- **API Keys**: Stored in `.env` which is gitignored - never committed
- **Uploaded Files**: Temporarily stored, auto-deleted after processing
- **Local Only**: Runs on localhost by default
- **Data Privacy**: Contract text is sent to Anthropic's API for analysis

---

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

---

## License

MIT License - See LICENSE file for details.

---

## Support

For issues or questions:
- Open an issue on [GitHub](https://github.com/Tucuxi-Inc/ContractPlaybookBuilder/issues)
