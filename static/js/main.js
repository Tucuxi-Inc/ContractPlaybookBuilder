/**
 * Contract Playbook Builder - Frontend JavaScript
 */

// DOM Elements
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

// State
let currentJobId = null;
let statusPollInterval = null;
let reassuranceInterval = null;
let reassuranceIndex = 0;

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

// File Upload Handling
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

// Form Submission
uploadForm.addEventListener('submit', async (e) => {
    e.preventDefault();

    const file = fileInput.files[0];
    if (!file) {
        showError('Please select a file to upload.');
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

        // Start polling for status updates - this is the primary completion detection
        startPollingStatus(currentJobId);

        // Start processing in background (don't await - it takes minutes)
        // The polling will detect completion, but we also handle it here as backup
        fetch(`/api/process/${currentJobId}`, {
            method: 'POST'
        }).then(response => response.json()).then(processData => {
            // Processing complete - the polling should have already detected this
            // but handle here as backup in case polling missed it
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
            // If neither completed nor error, let polling continue to handle it
        }).catch(error => {
            // Only show error if we're still in processing state
            // (polling might have already handled completion)
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

// Progress Updates
function updateProgress(percent, message) {
    progressText.textContent = message;

    // Update substatus based on progress
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
    // Rotate reassurance messages every 8 seconds
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

// Download
async function downloadPlaybook(jobId) {
    window.location.href = `/api/download/${jobId}`;
}

// UI State Management
function showSection(section) {
    uploadSection.classList.add('hidden');
    progressSection.classList.add('hidden');
    resultSection.classList.add('hidden');
    errorSection.classList.add('hidden');

    switch (section) {
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

// Health check on load
document.addEventListener('DOMContentLoaded', async () => {
    try {
        const response = await fetch('/api/health');
        const data = await response.json();

        if (!data.api_key_configured) {
            showError('API key is not configured. Please set the ANTHROPIC_API_KEY (or OPENAI_API_KEY) environment variable and restart the server.');
        }
    } catch (error) {
        console.log('Health check failed:', error);
    }
});
