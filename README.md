# Contract Playbook Builder

A web application that automatically generates professional contract playbooks from any template agreement. Upload a PDF, Word document, or Excel file, and receive a comprehensive negotiation playbook following industry best practices.

## What is a Contract Playbook?

A contract playbook is a strategic guide that documents your organization's negotiation positions, risk tolerance, and standard terms for contract negotiations. It helps legal teams, procurement professionals, and business stakeholders:

- **Negotiate consistently** across all deals
- **Save time** by providing pre-approved language and positions
- **Reduce risk** by identifying deal-breakers and acceptable alternatives
- **Empower non-lawyers** to handle routine negotiations
- **Preserve institutional knowledge** about preferred terms

## Features

- **Multi-format Upload**: Supports PDF, Word (.docx), and Excel (.xlsx) files
- **AI-Powered Analysis**: Uses GPT-4 to analyze clauses and generate guidance
- **Professional Output**: Creates Excel playbooks matching industry standards
- **Clause-by-Clause Breakdown**: Detailed analysis of every contract section
- **Negotiation Guidance**: Preferred positions, fallbacks, and deal-breakers
- **Risk Classification**: Color-coded risk levels (Red/Yellow/Green)
- **Sample Language**: Ready-to-use alternative clause wording

---

## Prerequisites

Before you begin, make sure you have the following installed on your computer:

### 1. Python 3.9 or higher

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
Download and run the installer from https://www.python.org/downloads/

### 2. pip (Python package manager)

pip usually comes with Python. Check with:
```bash
pip3 --version
```

### 3. OpenAI API Key

You'll need an OpenAI API key for the AI-powered analysis:

1. Go to https://platform.openai.com/signup
2. Create an account or sign in
3. Navigate to https://platform.openai.com/api-keys
4. Click "Create new secret key"
5. Copy the key (it starts with `sk-`)
6. **Keep this key private** - don't share it or commit it to git

---

## Installation

### Step 1: Clone the Repository

Open your terminal (Mac: Terminal app, Windows: Command Prompt or PowerShell):

```bash
# Navigate to where you want the project
cd ~/Desktop

# Clone the repository
git clone https://github.com/Tucuxi-Inc/ContractPlaybookBuilder.git

# Enter the project directory
cd ContractPlaybookBuilder
```

**If you don't have git**, you can download the ZIP file from GitHub and extract it.

### Step 2: Create a Virtual Environment

A virtual environment keeps this project's dependencies separate from other Python projects:

```bash
# Create the virtual environment
python3 -m venv venv

# Activate it (Mac/Linux)
source venv/bin/activate

# Activate it (Windows)
venv\Scripts\activate
```

**You'll know it's activated when you see `(venv)` at the start of your terminal prompt.**

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

This may take a few minutes as it downloads all required packages.

### Step 4: Set Your OpenAI API Key

**Mac/Linux:**
```bash
export OPENAI_API_KEY="sk-your-api-key-here"
```

**Windows (Command Prompt):**
```cmd
set OPENAI_API_KEY=sk-your-api-key-here
```

**Windows (PowerShell):**
```powershell
$env:OPENAI_API_KEY="sk-your-api-key-here"
```

**To make this permanent**, add the export line to your shell profile:
- Mac: Add to `~/.zshrc` or `~/.bash_profile`
- Windows: Set as a system environment variable

---

## Running the Application

### Start the Server

Make sure your virtual environment is activated (you see `(venv)` in your prompt), then:

```bash
python app.py
```

You should see output like:
```
 * Running on http://127.0.0.1:8005
 * Press CTRL+C to stop
```

### Access the Web Interface

Open your web browser and go to:

```
http://localhost:8005
```

You'll see the Contract Playbook Builder interface.

---

## How to Use

### Step 1: Upload Your Agreement

1. Click the **"Choose File"** button or drag and drop your file
2. Supported formats: PDF, Word (.docx), Excel (.xlsx)
3. Maximum file size: 50 MB

### Step 2: Configure Options (Optional)

- **Agreement Type**: Select the type of agreement (e.g., SaaS, Services, NDA)
- **Your Role**: Choose whether you're the Customer or Provider
- **Risk Tolerance**: Set your organization's risk appetite

### Step 3: Generate Playbook

1. Click **"Generate Playbook"**
2. Wait for processing (typically 1-5 minutes depending on document length)
3. A progress indicator will show the current status

### Step 4: Download Your Playbook

Once complete:
1. Click **"Download Playbook"**
2. The Excel file will download to your computer
3. Open it in Excel, Google Sheets, or any spreadsheet application

---

## Understanding Your Playbook

The generated playbook contains multiple sheets:

### Overview Sheet
- Agreement summary
- Key parties and dates
- High-level risk assessment

### Clause Analysis Sheet

| Column | Description |
|--------|-------------|
| **Section** | Reference to the original agreement section |
| **Issue** | The specific contractual issue addressed |
| **Context** | Business explanation of why this matters |
| **Current Language** | Text from the original agreement |
| **Preferred Position** | Your ideal negotiation outcome |
| **Fallback Positions** | Acceptable alternatives if preferred fails |
| **Don't Accept** | Deal-breaker positions to avoid |
| **Risk Level** | Red (high), Yellow (medium), Green (low) |
| **Approval Required** | Who needs to approve deviations |

### Definitions Sheet
- Key terms from the agreement
- Plain-language explanations

### Quick Reference Sheet
- Summary of critical issues
- At-a-glance negotiation checklist

---

## Troubleshooting

### "Port 8005 already in use"

Another application is using that port. Either:

1. **Stop the other application**, or
2. **Use a different port**:
   ```bash
   PORT=8006 python app.py
   ```
   Then access http://localhost:8006

### "ModuleNotFoundError: No module named 'xxx'"

Your virtual environment might not be activated or dependencies aren't installed:

```bash
# Make sure venv is activated
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate     # Windows

# Reinstall dependencies
pip install -r requirements.txt
```

### "OpenAI API key not found"

Make sure you've set the environment variable:

```bash
# Check if it's set
echo $OPENAI_API_KEY  # Mac/Linux
echo %OPENAI_API_KEY% # Windows CMD

# If empty, set it again
export OPENAI_API_KEY="sk-your-key-here"
```

### "Rate limit exceeded" or API errors

- The OpenAI API has usage limits. Wait a few minutes and try again.
- Check your OpenAI account for billing issues.

### Large files taking too long

- Files over 100 pages may take 10+ minutes to process
- Consider splitting very large agreements into sections
- Ensure you have a stable internet connection

### File not parsing correctly

- Make sure the file isn't password-protected
- PDF: Ensure it's text-based, not a scanned image
- Word: Save as .docx (not .doc)
- Try opening and re-saving the file

---

## Stopping the Application

Press `Ctrl+C` in the terminal where the app is running.

To deactivate the virtual environment:
```bash
deactivate
```

---

## Updating the Application

To get the latest version:

```bash
# Make sure you're in the project directory
cd ~/Desktop/ContractPlaybookBuilder

# Pull the latest changes
git pull origin main

# Activate virtual environment
source venv/bin/activate

# Update dependencies
pip install -r requirements.txt

# Restart the application
python app.py
```

---

## Project Structure

```
ContractPlaybookBuilder/
├── app.py                 # Main application entry point
├── config.py              # Configuration settings
├── requirements.txt       # Python dependencies
├── README.md              # This file
├── CLAUDE.md              # Development notes
├── .gitignore             # Files excluded from git
├── templates/             # HTML templates
│   └── index.html         # Main web interface
├── static/                # Static assets
│   ├── css/
│   │   └── style.css      # Application styling
│   └── js/
│       └── main.js        # Frontend JavaScript
├── utils/                 # Utility modules
│   ├── document_parser.py # Extracts text from documents
│   ├── playbook_generator.py  # AI-powered analysis
│   └── excel_writer.py    # Creates Excel output
├── uploads/               # Temporary upload storage
└── output/                # Generated playbooks
```

---

## Security Notes

- **API Keys**: Never commit your OpenAI API key to git
- **Uploaded Files**: Temporarily stored, then deleted after processing
- **Local Only**: By default, the app only runs on your local machine
- **No Data Collection**: Your agreements are not stored or transmitted anywhere except to OpenAI for analysis

---

## Support

For issues or questions:
- Open an issue on GitHub: https://github.com/Tucuxi-Inc/ContractPlaybookBuilder/issues

---

## License

[Add your license here]

---

## Acknowledgments

Built with:
- [Flask](https://flask.palletsprojects.com/) - Web framework
- [OpenAI GPT-4](https://openai.com/) - AI analysis
- [OpenPyXL](https://openpyxl.readthedocs.io/) - Excel file generation
- [PyPDF2](https://pypdf2.readthedocs.io/) - PDF parsing
- [python-docx](https://python-docx.readthedocs.io/) - Word document parsing
