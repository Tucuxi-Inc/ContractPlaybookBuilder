# Contract Playbook Builder

A web application that automatically generates professional contract playbooks from any template agreement. Upload a PDF, Word document, or Excel file, and receive a comprehensive negotiation playbook following industry best practices.

---

## Table of Contents

- [What is a Contract Playbook?](#what-is-a-contract-playbook)
- [Features](#features)
- [How It Works](#how-it-works)
- [Supported File Formats](#supported-file-formats)
- [Quick Start (TL;DR)](#quick-start-tldr)
- [Detailed Installation Guide](#detailed-installation-guide)
- [Running the Application](#running-the-application)
- [How to Use](#how-to-use)
- [Understanding Your Playbook](#understanding-your-playbook)
- [Using Local AI Models (Ollama)](#using-local-ai-models-ollama)
- [Troubleshooting](#troubleshooting)
- [Project Structure](#project-structure)
- [Security Notes](#security-notes)

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
- **AI-Powered Analysis**: Uses GPT-4o to analyze clauses and generate guidance
- **Professional Output**: Creates Excel playbooks matching industry standards
- **Clause-by-Clause Breakdown**: Detailed analysis of every contract section
- **Negotiation Guidance**: Preferred positions, fallbacks, and deal-breakers
- **Risk Classification**: Color-coded risk levels (Red/Yellow/Green)
- **Sample Language**: Ready-to-use alternative clause wording
- **Dual Perspective**: Analysis from both customer and provider viewpoints

---

## How It Works

The Contract Playbook Builder uses a multi-step AI-powered pipeline to transform your agreements into actionable playbooks:

### 1. Document Upload & Parsing

When you upload a document, the application:
- **PDF files**: Extracts text using PyPDF2, handling multi-page documents
- **Word files (.docx)**: Parses paragraphs and tables using python-docx
- **Excel files (.xlsx)**: Extracts cell contents using openpyxl

### 2. AI Analysis

The extracted text is sent to OpenAI's GPT-4o model with a specialized legal analysis prompt. The AI:
- Identifies each significant clause or section
- Analyzes the business and legal implications
- Determines risk levels based on standard contract practices
- Generates negotiation strategies from both party perspectives
- Creates sample alternative language for each clause

For longer documents (50,000+ characters), the system automatically:
- Splits the document into manageable chunks
- Analyzes each chunk separately
- Combines results into a unified playbook

### 3. Playbook Generation

The AI's analysis is transformed into a structured Excel workbook with:
- Overview sheet with agreement summary
- Detailed clause-by-clause analysis
- Definitions and key terms
- Quick reference checklist

### Processing Time

| Document Size | Approximate Time |
|---------------|------------------|
| 1-10 pages | 30-60 seconds |
| 10-30 pages | 1-3 minutes |
| 30-100 pages | 3-7 minutes |
| 100+ pages | 7-15 minutes |

---

## Supported File Formats

| Format | Extension | Notes |
|--------|-----------|-------|
| **PDF** | `.pdf` | Must be text-based (not scanned images). Searchable PDFs work best. |
| **Word** | `.docx` | Modern Word format only. Legacy `.doc` files must be converted. |
| **Excel** | `.xlsx` | Useful for contracts already in spreadsheet format. |

**Maximum file size**: 50 MB

**Tips for best results**:
- Ensure PDFs are text-searchable, not scanned images
- Remove password protection before uploading
- For scanned documents, use OCR software first

---

## Quick Start (TL;DR)

For experienced developers, here's the fast track:

```bash
# Clone and setup
git clone https://github.com/Tucuxi-Inc/ContractPlaybookBuilder.git
cd ContractPlaybookBuilder
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Set your OpenAI API key
export OPENAI_API_KEY="sk-your-key-here"  # Windows: set OPENAI_API_KEY=sk-your-key-here

# Run the app
python app.py

# Open http://localhost:3005 in your browser
```

---

## Detailed Installation Guide

New to development? Follow these step-by-step instructions.

### Prerequisites

Before you begin, make sure you have the following installed on your computer:

#### 1. Python 3.9 or higher

**Check if Python is installed:**
```bash
python3 --version
```

If you see a version number like `Python 3.9.x` or higher, you're good. If not:

**Install Python on Mac:**
```bash
# Using Homebrew (recommended)
brew install python3

# Or download from https://www.python.org/downloads/
```

**Install Python on Windows:**
1. Go to https://www.python.org/downloads/
2. Download the latest Python installer
3. **Important**: Check "Add Python to PATH" during installation
4. Run the installer

#### 2. Git (optional but recommended)

Git allows you to easily download and update the code.

**Check if Git is installed:**
```bash
git --version
```

**Install Git:**
- Mac: `brew install git` or download from https://git-scm.com/
- Windows: Download from https://git-scm.com/download/win

#### 3. OpenAI API Key

You'll need an OpenAI API key for the AI-powered analysis:

1. Go to https://platform.openai.com/signup
2. Create an account or sign in
3. Navigate to https://platform.openai.com/api-keys
4. Click "Create new secret key"
5. Copy the key (it starts with `sk-`)
6. **Keep this key private** - don't share it or commit it to git

**Note**: OpenAI charges for API usage. Typical cost per playbook is $0.10-$0.50 depending on document length.

---

### Step 1: Download the Code

**Option A: Using Git (Recommended)**

Open your terminal:
- **Mac**: Press `Cmd + Space`, type "Terminal", press Enter
- **Windows**: Press `Win + R`, type "cmd", press Enter (or search for "Command Prompt")

```bash
# Navigate to your Desktop (or wherever you want the project)
cd ~/Desktop

# Clone the repository
git clone https://github.com/Tucuxi-Inc/ContractPlaybookBuilder.git

# Enter the project directory
cd ContractPlaybookBuilder
```

**Option B: Download ZIP (No Git Required)**

1. Go to https://github.com/Tucuxi-Inc/ContractPlaybookBuilder
2. Click the green "Code" button
3. Click "Download ZIP"
4. Extract the ZIP file to your Desktop
5. Open terminal and navigate to the folder:
   ```bash
   cd ~/Desktop/ContractPlaybookBuilder-main
   ```

### Step 2: Create a Virtual Environment

A virtual environment keeps this project's dependencies separate from other Python projects:

```bash
# Create the virtual environment
python3 -m venv venv
```

**Activate it:**

```bash
# Mac/Linux
source venv/bin/activate

# Windows (Command Prompt)
venv\Scripts\activate

# Windows (PowerShell)
.\venv\Scripts\Activate.ps1
```

**You'll know it's activated when you see `(venv)` at the start of your terminal prompt.**

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

This downloads all required Python packages. It may take 1-2 minutes.

### Step 4: Set Your OpenAI API Key

**Mac/Linux (temporary - lasts until terminal closes):**
```bash
export OPENAI_API_KEY="sk-your-api-key-here"
```

**Mac/Linux (permanent - add to shell profile):**
```bash
echo 'export OPENAI_API_KEY="sk-your-api-key-here"' >> ~/.zshrc
source ~/.zshrc
```

**Windows Command Prompt (temporary):**
```cmd
set OPENAI_API_KEY=sk-your-api-key-here
```

**Windows PowerShell (temporary):**
```powershell
$env:OPENAI_API_KEY="sk-your-api-key-here"
```

**Windows (permanent):**
1. Search for "Environment Variables" in Start menu
2. Click "Edit the system environment variables"
3. Click "Environment Variables" button
4. Under "User variables", click "New"
5. Variable name: `OPENAI_API_KEY`
6. Variable value: `sk-your-api-key-here`
7. Click OK

---

## Running the Application

### Start the Server

Make sure your virtual environment is activated (you see `(venv)` in your prompt), then:

```bash
python app.py
```

You should see:
```
============================================================
Contract Playbook Builder
============================================================
Starting server on http://localhost:3005
OpenAI API Key: Configured
============================================================
```

### Access the Web Interface

Open your web browser (Chrome, Firefox, Safari, Edge) and go to:

```
http://localhost:3005
```

You'll see the Contract Playbook Builder interface ready to use.

### Stopping the Application

Press `Ctrl+C` in the terminal where the app is running.

To deactivate the virtual environment when you're done:
```bash
deactivate
```

---

## How to Use

### Step 1: Upload Your Agreement

1. Click the **"Choose File"** button or drag and drop your file
2. Supported formats: PDF, Word (.docx), Excel (.xlsx)
3. Maximum file size: 50 MB

### Step 2: Configure Options

- **Agreement Type**: Select the type (SaaS, Services, NDA, Employment, etc.)
  - This helps the AI understand industry-specific concerns
- **Your Role**: Choose Customer/Buyer or Provider/Vendor
  - The playbook will be tailored to your perspective
- **Risk Tolerance**: Low, Moderate, or High
  - Affects how aggressively positions are recommended

### Step 3: Generate Playbook

1. Click **"Generate Playbook"**
2. Wait for processing (progress indicator shows current status)
3. Processing stages:
   - Parsing document...
   - Analyzing contract with AI...
   - Generating Excel playbook...

### Step 4: Download Your Playbook

Once complete:
1. Click **"Download Playbook"**
2. The Excel file downloads to your computer
3. Open in Excel, Google Sheets, or any spreadsheet app

---

## Understanding Your Playbook

The generated Excel workbook contains multiple sheets:

### Overview Sheet
- Agreement title and type
- Parties involved
- Key dates and terms
- Overall risk assessment
- Count of critical issues

### Clause Analysis Sheet

| Column | Description |
|--------|-------------|
| **Section** | Reference to the original agreement section |
| **Issue** | The specific contractual issue addressed |
| **Context** | Business explanation of why this matters |
| **Current Language** | Text from the original agreement |
| **Customer Concerns** | What a buyer would worry about |
| **Provider Concerns** | What a vendor would worry about |
| **Preferred Position** | Your ideal negotiation outcome with sample language |
| **Fallback Positions** | Acceptable alternatives if preferred fails |
| **Don't Accept** | Deal-breaker positions to avoid |
| **Risk Level** | Red (high), Yellow (medium), Green (low) |
| **Approval Required** | Who needs to approve deviations |
| **Negotiation Tips** | Practical advice for this clause |

### Definitions Sheet
- Key terms from the agreement
- Plain-language explanations
- Why each definition matters

### Quick Reference Sheet
- Deal-breakers (must-have terms)
- High priority items
- Standard acceptable terms
- Common negotiation points

---

## Using Local AI Models (Ollama)

Don't have an OpenAI account? Want to process documents completely locally for privacy?

You can modify this application to use **Ollama** with local models like Llama, Mistral, or CodeLlama.

**See the detailed guide**: [LOCAL_AI_GUIDE.md](./LOCAL_AI_GUIDE.md)

This guide includes:
- Step-by-step Ollama installation
- Model recommendations for contract analysis
- Code modifications needed
- Instructions for coding co-pilots (Claude Code, GitHub Copilot, etc.)

---

## Troubleshooting

### "Port 3005 already in use"

Another application is using that port. Either:

1. **Find and stop the other application**, or
2. **Use a different port**:
   ```bash
   PORT=3006 python app.py
   ```
   Then access http://localhost:3006

### "ModuleNotFoundError: No module named 'xxx'"

Your virtual environment might not be activated or dependencies aren't installed:

```bash
# Make sure venv is activated (you should see (venv) in prompt)
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate     # Windows

# Reinstall dependencies
pip install -r requirements.txt
```

### "OpenAI API key not found"

Make sure you've set the environment variable:

```bash
# Check if it's set (Mac/Linux)
echo $OPENAI_API_KEY

# Check if it's set (Windows CMD)
echo %OPENAI_API_KEY%

# If empty, set it again
export OPENAI_API_KEY="sk-your-key-here"
```

### "Rate limit exceeded" or API errors

- The OpenAI API has usage limits. Wait a few minutes and try again.
- Check your OpenAI account dashboard for billing/quota issues.
- Ensure your API key is active and has available credits.

### "500 Internal Server Error" when processing

Check the terminal where the app is running for error details. Common causes:
- Invalid or expired OpenAI API key
- Network connectivity issues
- Document parsing failures (try a different file format)

### Large files taking too long

- Files over 100 pages may take 10+ minutes to process
- The AI processes text in chunks for very long documents
- Ensure you have a stable internet connection

### File not parsing correctly

- Make sure the file isn't password-protected
- **PDF**: Must be text-based, not a scanned image
  - Use OCR software to convert scanned PDFs first
- **Word**: Save as .docx (not legacy .doc format)
- **Excel**: Ensure data is in standard cells, not embedded objects
- Try opening and re-saving the file in its native application

### Application won't start

1. Verify Python version: `python3 --version` (need 3.9+)
2. Verify you're in the project directory: `ls app.py` should show the file
3. Verify virtual environment: you should see `(venv)` in your prompt
4. Try reinstalling: `pip install -r requirements.txt --force-reinstall`

---

## Updating the Application

To get the latest version:

```bash
# Make sure you're in the project directory
cd ~/Desktop/ContractPlaybookBuilder

# Pull the latest changes (if using Git)
git pull origin main

# Activate virtual environment
source venv/bin/activate  # Windows: venv\Scripts\activate

# Update dependencies
pip install -r requirements.txt --upgrade

# Restart the application
python app.py
```

---

## Project Structure

```
ContractPlaybookBuilder/
├── app.py                    # Main Flask application entry point
├── config.py                 # Configuration settings (port, API keys, etc.)
├── requirements.txt          # Python package dependencies
├── README.md                 # This documentation file
├── LOCAL_AI_GUIDE.md         # Guide for using Ollama/local models
├── CLAUDE.md                 # Development notes for AI assistants
├── .gitignore                # Files excluded from git
├── templates/                # HTML templates
│   └── index.html            # Main web interface
├── static/                   # Static assets
│   ├── css/
│   │   └── style.css         # Application styling
│   └── js/
│       └── main.js           # Frontend JavaScript
├── utils/                    # Core utility modules
│   ├── document_parser.py    # Extracts text from PDF/Word/Excel
│   ├── playbook_generator.py # AI-powered contract analysis
│   └── excel_writer.py       # Creates formatted Excel output
├── uploads/                  # Temporary upload storage (auto-created)
└── output/                   # Generated playbooks (auto-created)
```

---

## Configuration Options

You can customize the application using environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `PORT` | 3005 | Server port number |
| `OPENAI_API_KEY` | (required) | Your OpenAI API key |
| `OPENAI_MODEL` | gpt-4o | OpenAI model to use |
| `MAX_FILE_SIZE` | 50 | Maximum upload size in MB |
| `FLASK_DEBUG` | 0 | Set to 1 for debug mode |

Example:
```bash
PORT=8080 OPENAI_MODEL=gpt-4-turbo python app.py
```

---

## Security Notes

- **API Keys**: Never commit your OpenAI API key to git. It's in `.gitignore`.
- **Uploaded Files**: Temporarily stored during processing, then automatically deleted
- **Local Only**: By default, the app only runs on your local machine (localhost)
- **Data Privacy**: Your agreements are sent to OpenAI for analysis. Review OpenAI's data policies if processing sensitive documents.
- **No Telemetry**: This application does not collect or transmit any analytics

For maximum privacy, see [LOCAL_AI_GUIDE.md](./LOCAL_AI_GUIDE.md) to process documents entirely on your machine.

---

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

---

## License

MIT License - See LICENSE file for details.

---

## Acknowledgments

Built with:
- [Flask](https://flask.palletsprojects.com/) - Python web framework
- [OpenAI GPT-4](https://openai.com/) - AI-powered analysis
- [OpenPyXL](https://openpyxl.readthedocs.io/) - Excel file generation
- [PyPDF2](https://pypdf2.readthedocs.io/) - PDF text extraction
- [python-docx](https://python-docx.readthedocs.io/) - Word document parsing

---

## Support

For issues, questions, or feature requests:
- Open an issue on GitHub: https://github.com/Tucuxi-Inc/ContractPlaybookBuilder/issues
