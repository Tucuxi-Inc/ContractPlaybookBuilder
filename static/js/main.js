/**
 * Contract Playbook Builder - Frontend JavaScript
 */

// DOM Elements
const setupSection = document.getElementById('setup-section');
const uploadSection = document.getElementById('upload-section');
const progressSection = document.getElementById('progress-section');
const resultSection = document.getElementById('result-section');
const errorSection = document.getElementById('error-section');
const uploadForm = document.getElementById('upload-form');
const fileInput = document.getElementById('file-input');
const dropZone = document.getElementById('drop-zone');
const fileInfo = document.getElementById('file-info');
const generateBtn = document.getElementById('generate-btn');
const downloadBtn = document.getElementById('download-btn');
const progressText = document.getElementById('progress-text');
const progressSubstatus = document.getElementById('progress-substatus');
const progressReassurance = document.getElementById('progress-reassurance');
const errorMessage = document.getElementById('error-message');

// Setup elements
const settingsBtn = document.getElementById('settings-btn');
const setupProvider = document.getElementById('setup-provider');
const setupModel = document.getElementById('setup-model');
const setupApiKey = document.getElementById('setup-api-key');
const setupSaveBtn = document.getElementById('setup-save-btn');
const setupError = document.getElementById('setup-error');
const setupSuccess = document.getElementById('setup-success');
const setupKeyHint = document.getElementById('setup-key-hint');

// State
let currentJobId = null;
let statusPollInterval = null;
let reassuranceInterval = null;
let reassuranceIndex = 0;
let providersData = {};
let apiKeyConfigured = false;

// Key hint URLs per provider
const providerKeyHints = {
    anthropic: 'Get your key at <a href="https://console.anthropic.com/" target="_blank">console.anthropic.com</a>',
    openai: 'Get your key at <a href="https://platform.openai.com/api-keys" target="_blank">platform.openai.com</a>',
    google: 'Get your key at <a href="https://aistudio.google.com/apikey" target="_blank">aistudio.google.com</a>'
};

// Reassurance messages that rotate while processing
const reassuranceMessages = [
    "Your playbook is being generated...",
    "AI is reviewing the document...",
    "Still processing — this takes a few minutes...",
    "Building your negotiation guide...",
    "Analyzing document structure...",
    "Processing — thank you for your patience...",
    "Creating comprehensive guidance...",
    "Almost there — finalizing analysis...",
];

// =============================================================================
// Setup / Configuration
// =============================================================================

async function loadConfig() {
    try {
        const response = await fetch('/api/config');
        const data = await response.json();

        providersData = data.providers;

        // Populate provider dropdown
        setupProvider.innerHTML = '<option value="">-- Select Provider --</option>';
        for (const [pid, pinfo] of Object.entries(data.providers)) {
            const option = document.createElement('option');
            option.value = pid;
            option.textContent = pinfo.name;
            setupProvider.appendChild(option);
        }

        // If a provider is already configured, pre-select it
        if (data.provider && data.has_key) {
            apiKeyConfigured = true;
            setupProvider.value = data.provider;
            updateModelDropdown(data.provider);
            if (data.model) {
                setupModel.value = data.model;
            }
            setupApiKey.placeholder = 'API key is configured (enter new key to change)';
        } else {
            apiKeyConfigured = false;
        }

        return data;
    } catch (error) {
        console.error('Failed to load config:', error);
        return null;
    }
}

function updateModelDropdown(provider) {
    setupModel.innerHTML = '';
    if (!provider || !providersData[provider]) {
        setupModel.innerHTML = '<option value="">-- Select Provider First --</option>';
        setupModel.disabled = true;
        setupKeyHint.innerHTML = '';
        return;
    }

    const models = providersData[provider].models;
    models.forEach(m => {
        const option = document.createElement('option');
        option.value = m.id;
        option.textContent = m.name;
        setupModel.appendChild(option);
    });
    setupModel.disabled = false;
    setupKeyHint.innerHTML = providerKeyHints[provider] || '';
    validateSetupForm();
}

function validateSetupForm() {
    const hasProvider = setupProvider.value !== '';
    const hasKey = setupApiKey.value.trim() !== '';
    // Allow saving if provider selected and either key entered or key was already configured
    const keyConfigured = setupApiKey.placeholder.includes('configured');
    setupSaveBtn.disabled = !(hasProvider && (hasKey || keyConfigured));
}

setupProvider.addEventListener('change', () => {
    updateModelDropdown(setupProvider.value);
    validateSetupForm();
});

setupApiKey.addEventListener('input', validateSetupForm);

setupSaveBtn.addEventListener('click', async () => {
    setupError.classList.add('hidden');
    setupSuccess.classList.add('hidden');

    const provider = setupProvider.value;
    const model = setupModel.value;
    const apiKey = setupApiKey.value.trim();

    if (!provider) {
        setupError.textContent = 'Please select a provider.';
        setupError.classList.remove('hidden');
        return;
    }

    // If key field is empty but was already configured, user may just be changing model
    if (!apiKey && !setupApiKey.placeholder.includes('configured')) {
        setupError.textContent = 'Please enter your API key.';
        setupError.classList.remove('hidden');
        return;
    }

    setupSaveBtn.disabled = true;
    setupSaveBtn.textContent = 'Saving...';

    try {
        const body = { provider, model };
        if (apiKey) {
            body.api_key = apiKey;
        }

        const response = await fetch('/api/config', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body)
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || 'Failed to save configuration');
        }

        apiKeyConfigured = true;
        setupSuccess.textContent = `Saved! Using ${providersData[provider]?.name || provider} (${model})`;
        setupSuccess.classList.remove('hidden');
        setupApiKey.value = '';
        setupApiKey.placeholder = 'API key is configured (enter new key to change)';

        // Transition to upload section after a brief delay
        setTimeout(() => {
            showSection('upload');
        }, 800);

    } catch (error) {
        setupError.textContent = error.message;
        setupError.classList.remove('hidden');
    } finally {
        setupSaveBtn.disabled = false;
        setupSaveBtn.textContent = 'Save & Continue';
        validateSetupForm();
    }
});

settingsBtn.addEventListener('click', async () => {
    await loadConfig();
    showSection('setup');
});

// =============================================================================
// File Upload Handling
// =============================================================================

fileInput.addEventListener('change', handleFileSelect);

dropZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropZone.classList.add('dragover');
});

dropZone.addEventListener('dragleave', () => {
    dropZone.classList.remove('dragover');
});

dropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropZone.classList.remove('dragover');

    const files = e.dataTransfer.files;
    if (files.length > 0) {
        fileInput.files = files;
        handleFileSelect();
    }
});

function handleFileSelect() {
    const file = fileInput.files[0];
    if (file) {
        const fileName = file.name;
        const fileSize = formatFileSize(file.size);

        fileInfo.querySelector('.file-name').textContent = `${fileName} (${fileSize})`;
        fileInfo.classList.remove('hidden');
        dropZone.style.display = 'none';
    }
}

function removeFile() {
    fileInput.value = '';
    fileInfo.classList.add('hidden');
    dropZone.style.display = 'block';
}

function formatFileSize(bytes) {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
}

// =============================================================================
// Form Submission
// =============================================================================

uploadForm.addEventListener('submit', async (e) => {
    e.preventDefault();

    const file = fileInput.files[0];
    if (!file) {
        showError('Please select a file to upload.');
        return;
    }

    // Check if API key is configured before proceeding
    if (!apiKeyConfigured) {
        showError('No AI provider configured. Please click the Settings icon to select a provider and enter your API key.');
        return;
    }

    // Prepare form data
    const formData = new FormData();
    formData.append('file', file);
    formData.append('agreement_type', document.getElementById('agreement-type').value);
    formData.append('user_role', document.getElementById('user-role').value);
    formData.append('risk_tolerance', document.getElementById('risk-tolerance').value);

    // Disable button and show progress
    generateBtn.disabled = true;
    generateBtn.textContent = 'Uploading...';

    try {
        // Upload file
        const uploadResponse = await fetch('/api/upload', {
            method: 'POST',
            body: formData
        });

        const uploadData = await uploadResponse.json();

        if (!uploadResponse.ok) {
            throw new Error(uploadData.error || 'Upload failed');
        }

        currentJobId = uploadData.job_id;

        // Show progress section
        showSection('progress');
        updateProgress(5, 'Starting analysis...');
        startReassuranceRotation();

        // Start polling for status updates
        startPollingStatus(currentJobId);

        // Start processing in background
        fetch(`/api/process/${currentJobId}`, {
            method: 'POST'
        }).then(response => response.json()).then(processData => {
            if (processData.status === 'completed') {
                if (statusPollInterval) {
                    clearInterval(statusPollInterval);
                }
                stopReassuranceRotation();
                showSection('result');
                downloadBtn.onclick = () => downloadPlaybook(currentJobId);
            } else if (processData.status === 'error') {
                if (statusPollInterval) {
                    clearInterval(statusPollInterval);
                }
                stopReassuranceRotation();
                showError(processData.error || 'Processing failed');
            }
        }).catch(error => {
            if (progressSection && !progressSection.classList.contains('hidden')) {
                if (statusPollInterval) {
                    clearInterval(statusPollInterval);
                }
                stopReassuranceRotation();
                showError(error.message || 'Processing failed');
            }
        });

    } catch (error) {
        showError(error.message);
    } finally {
        generateBtn.disabled = false;
        generateBtn.textContent = 'Generate Playbook';
    }
});

// =============================================================================
// Progress Updates
// =============================================================================

function updateProgress(percent, message) {
    progressText.textContent = message;

    if (percent < 20) {
        progressSubstatus.textContent = "Parsing document and preparing for analysis";
    } else if (percent < 50) {
        progressSubstatus.textContent = "AI is reviewing contract provisions";
    } else if (percent < 80) {
        progressSubstatus.textContent = "Generating negotiation strategies";
    } else {
        progressSubstatus.textContent = "Finalizing your playbook";
    }
}

function startReassuranceRotation() {
    reassuranceInterval = setInterval(() => {
        reassuranceIndex = (reassuranceIndex + 1) % reassuranceMessages.length;
        if (progressReassurance) {
            progressReassurance.textContent = reassuranceMessages[reassuranceIndex];
        }
    }, 8000);
}

function stopReassuranceRotation() {
    if (reassuranceInterval) {
        clearInterval(reassuranceInterval);
        reassuranceInterval = null;
    }
}

function startPollingStatus(jobId) {
    statusPollInterval = setInterval(async () => {
        try {
            const response = await fetch(`/api/status/${jobId}`);
            const data = await response.json();

            updateProgress(data.progress, data.message);

            if (data.status === 'completed') {
                clearInterval(statusPollInterval);
                showSection('result');
                downloadBtn.onclick = () => downloadPlaybook(jobId);
            } else if (data.status === 'error') {
                clearInterval(statusPollInterval);
                showError(data.error || 'An error occurred');
            }
        } catch (error) {
            clearInterval(statusPollInterval);
            showError('Lost connection to server');
        }
    }, 1000);
}

// =============================================================================
// Download
// =============================================================================

async function downloadPlaybook(jobId) {
    window.location.href = `/api/download/${jobId}`;
}

// =============================================================================
// UI State Management
// =============================================================================

function showSection(section) {
    setupSection.classList.add('hidden');
    uploadSection.classList.add('hidden');
    progressSection.classList.add('hidden');
    resultSection.classList.add('hidden');
    errorSection.classList.add('hidden');

    switch (section) {
        case 'setup':
            setupSection.classList.remove('hidden');
            break;
        case 'upload':
            uploadSection.classList.remove('hidden');
            break;
        case 'progress':
            progressSection.classList.remove('hidden');
            break;
        case 'result':
            resultSection.classList.remove('hidden');
            break;
        case 'error':
            errorSection.classList.remove('hidden');
            break;
    }
}

function showError(message) {
    errorMessage.textContent = message;
    showSection('error');

    if (statusPollInterval) {
        clearInterval(statusPollInterval);
    }
    stopReassuranceRotation();
}

function startOver() {
    currentJobId = null;
    if (statusPollInterval) {
        clearInterval(statusPollInterval);
    }
    stopReassuranceRotation();
    reassuranceIndex = 0;

    // Reset form
    uploadForm.reset();
    removeFile();
    updateProgress(0, 'Starting analysis...');

    showSection('upload');
}

// =============================================================================
// Initialization
// =============================================================================

document.addEventListener('DOMContentLoaded', async () => {
    const configData = await loadConfig();

    if (configData && configData.has_key) {
        // API key is configured, go straight to upload
        showSection('upload');
    } else {
        // No API key, show setup
        showSection('setup');
    }
});
