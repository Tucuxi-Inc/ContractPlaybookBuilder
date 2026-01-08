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
const progressFill = document.getElementById('progress-fill');
const progressText = document.getElementById('progress-text');
const progressPercent = document.getElementById('progress-percent');
const errorMessage = document.getElementById('error-message');

// State
let currentJobId = null;
let statusPollInterval = null;

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
        updateProgress(5, 'File uploaded. Starting analysis...');

        // Start processing in background (don't await - it takes minutes)
        fetch(`/api/process/${currentJobId}`, {
            method: 'POST'
        }).then(response => response.json()).then(processData => {
            // Processing complete - stop polling and show result
            if (statusPollInterval) {
                clearInterval(statusPollInterval);
            }
            if (processData.status === 'completed') {
                showSection('result');
                downloadBtn.onclick = () => downloadPlaybook(currentJobId);
            } else if (processData.status === 'error') {
                showError(processData.error || 'Processing failed');
            }
        }).catch(error => {
            if (statusPollInterval) {
                clearInterval(statusPollInterval);
            }
            showError(error.message || 'Processing failed');
        });

        // Start polling for status updates while processing
        startPollingStatus(currentJobId);

    } catch (error) {
        showError(error.message);
    } finally {
        generateBtn.disabled = false;
        generateBtn.textContent = 'Generate Playbook';
    }
});

// Progress Updates
function updateProgress(percent, message) {
    progressFill.style.width = `${percent}%`;
    progressPercent.textContent = `${percent}%`;
    progressText.textContent = message;
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
}

function startOver() {
    currentJobId = null;
    if (statusPollInterval) {
        clearInterval(statusPollInterval);
    }

    // Reset form
    uploadForm.reset();
    removeFile();
    updateProgress(0, 'Starting...');

    showSection('upload');
}

// Health check on load
document.addEventListener('DOMContentLoaded', async () => {
    try {
        const response = await fetch('/api/health');
        const data = await response.json();

        if (!data.api_key_configured) {
            showError('OpenAI API key is not configured. Please set the OPENAI_API_KEY environment variable and restart the server.');
        }
    } catch (error) {
        console.log('Health check failed:', error);
    }
});
