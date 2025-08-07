// Enhanced JavaScript with better error handling and UI feedback

document.addEventListener('DOMContentLoaded', () => {
    // Initialize theme
    initializeTheme();
    
    // Initialize event listeners
    initializeEventListeners();
});

function initializeTheme() {
    const nightModeToggle = document.getElementById('night-mode-toggle');
    const modeIcon = document.getElementById('mode-icon');
    
    // Check for saved theme preference or default to light mode
    const savedTheme = localStorage.getItem('theme') || 'light';
    if (savedTheme === 'dark') {
        document.body.classList.add('night-mode');
        modeIcon.src = "../static/sun.png";
        modeIcon.alt = 'Switch to light mode';
    }
    
    nightModeToggle.addEventListener('click', toggleTheme);
}

function toggleTheme() {
    const modeIcon = document.getElementById('mode-icon');
    const isNightMode = document.body.classList.toggle('night-mode');
    
    if (isNightMode) {
        modeIcon.src = "../static/sun.png";
        modeIcon.alt = 'Switch to light mode';
        localStorage.setItem('theme', 'dark');
    } else {
        modeIcon.src = "../static/moon.png";
        modeIcon.alt = 'Switch to dark mode';
        localStorage.setItem('theme', 'light');
    }
}

function initializeEventListeners() {
    // Download form
    const downloadForm = document.getElementById('download-form');
    downloadForm.addEventListener('submit', handleDownload);
    
    // Clear URL button
    const clearButton = document.getElementById('clear-url');
    clearButton.addEventListener('click', clearUrl);
    
    // Organize button
    const organizeButton = document.getElementById('organize-button');
    organizeButton.addEventListener('click', handleOrganize);
    
    // URL input validation
    const urlInput = document.getElementById('url');
    urlInput.addEventListener('input', validateUrl);
}

function validateUrl() {
    const urlInput = document.getElementById('url');
    const url = urlInput.value.trim();
    
    if (url && !isValidUrl(url)) {
        urlInput.style.borderColor = 'var(--error)';
    } else {
        urlInput.style.borderColor = 'var(--border)';
    }
}

function isValidUrl(string) {
    try {
        new URL(string);
        return true;
    } catch (_) {
        return false;
    }
}

function clearUrl() {
    const urlInput = document.getElementById('url');
    urlInput.value = '';
    urlInput.style.borderColor = 'var(--border)';
    urlInput.focus();
}

async function handleDownload(e) {
    e.preventDefault();
    
    const url = document.getElementById('url').value.trim();
    const statusDiv = document.getElementById('status');
    const downloadsDiv = document.getElementById('downloads');
    const loadingSpinner = document.getElementById('loading');
    const downloadButton = document.getElementById('download-btn');
    
    // Reset UI
    statusDiv.innerHTML = '';
    downloadsDiv.innerHTML = '';
    
    // Validate URL
    if (!url) {
        showStatus('Please enter a valid URL', 'error');
        return;
    }
    
    if (!isValidUrl(url)) {
        showStatus('Please enter a valid URL format', 'error');
        return;
    }
    
    // Show loading state
    setLoadingState(true, downloadButton, loadingSpinner);
    
    try {
        const formData = new FormData();
        formData.append('url', url);
        
        const response = await fetch('/download', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (response.ok && data.success !== false) {
            const statusType = data.warning ? 'warning' : 'success';
            showStatus(data.message || 'Download completed successfully!', statusType);
            
            if (data.files && data.files.length > 0) {
                displayDownloadLinks(data.files);
            } else if (data.success) {
                // Even if no files detected, show success if backend says it succeeded
                showStatus('Download completed! Check your downloads folder.', statusType);
            } else {
                showStatus('Download may be processing. Please check your downloads folder.', 'warning');
            }
        } else {
            const errorMessage = data.error || data.details || 'Download failed. Please try again.';
            showStatus(errorMessage, 'error');
            console.error('Download error:', data);
        }
    } catch (error) {
        console.error('Network error:', error);
        showStatus('Network error. Please check your connection and try again.', 'error');
    } finally {
        setLoadingState(false, downloadButton, loadingSpinner);
    }
}

async function handleOrganize() {
    const organizeStatusDiv = document.getElementById('organize-status');
    const organizeLoadingSpinner = document.getElementById('organize-loading');
    const organizeButton = document.getElementById('organize-button');
    
    // Reset UI
    organizeStatusDiv.innerHTML = '';
    
    // Show loading state
    setLoadingState(true, organizeButton, organizeLoadingSpinner);
    
    try {
        const response = await fetch('/organize', { 
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showOrganizeStatus(data.message || 'Music organized successfully!', 'success');
        } else {
            const errorMessage = data.error || 'Organization failed. Please try again.';
            showOrganizeStatus(errorMessage, 'error');
            console.error('Organize error:', data);
        }
    } catch (error) {
        console.error('Network error:', error);
        showOrganizeStatus('Network error. Please check your connection and try again.', 'error');
    } finally {
        setLoadingState(false, organizeButton, organizeLoadingSpinner);
    }
}

function setLoadingState(isLoading, button, spinner) {
    if (isLoading) {
        button.disabled = true;
        button.style.opacity = '0.7';
        spinner.style.display = 'block';
    } else {
        button.disabled = false;
        button.style.opacity = '1';
        spinner.style.display = 'none';
    }
}

function showStatus(message, type) {
    const statusDiv = document.getElementById('status');
    let iconSvg;
    
    if (type === 'success') {
        iconSvg = '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="currentColor" viewBox="0 0 16 16"><path d="M16 8A8 8 0 1 1 0 8a8 8 0 0 1 16 0zm-3.97-3.03a.75.75 0 0 0-1.08.022L7.477 9.417 5.384 7.323a.75.75 0 0 0-1.06 1.061L6.97 11.03a.75.75 0 0 0 1.079-.02l3.992-4.99a.75.75 0 0 0-.01-1.05z"/></svg>';
    } else if (type === 'warning') {
        iconSvg = '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="currentColor" viewBox="0 0 16 16"><path d="M8.982 1.566a1.13 1.13 0 0 0-1.96 0L.165 13.233c-.457.778.091 1.767.98 1.767h13.713c.889 0 1.438-.99.98-1.767L8.982 1.566zM8 5c.535 0 .954.462.9.995l-.35 3.507a.552.552 0 0 1-1.1 0L7.1 5.995A.905.905 0 0 1 8 5zm.002 6a1 1 0 1 1 0 2 1 1 0 0 1 0-2z"/></svg>';
    } else {
        iconSvg = '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="currentColor" viewBox="0 0 16 16"><path d="M16 8A8 8 0 1 1 0 8a8 8 0 0 1 16 0zM5.354 4.646a.5.5 0 1 0-.708.708L7.293 8l-2.647 2.646a.5.5 0 0 0 .708.708L8 8.707l2.646 2.647a.5.5 0 0 0 .708-.708L8.707 8l2.647-2.646a.5.5 0 0 0-.708-.708L8 7.293 5.354 4.646z"/></svg>';
    }
    
    statusDiv.innerHTML = `
        <div class="status-message status-${type}">
            ${iconSvg}
            <span>${message}</span>
        </div>
    `;
}

function showOrganizeStatus(message, type) {
    const statusDiv = document.getElementById('organize-status');
    const iconSvg = type === 'success' 
        ? '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="currentColor" viewBox="0 0 16 16"><path d="M16 8A8 8 0 1 1 0 8a8 8 0 0 1 16 0zm-3.97-3.03a.75.75 0 0 0-1.08.022L7.477 9.417 5.384 7.323a.75.75 0 0 0-1.06 1.061L6.97 11.03a.75.75 0 0 0 1.079-.02l3.992-4.99a.75.75 0 0 0-.01-1.05z"/></svg>'
        : '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="currentColor" viewBox="0 0 16 16"><path d="M16 8A8 8 0 1 1 0 8a8 8 0 0 1 16 0zM5.354 4.646a.5.5 0 1 0-.708.708L7.293 8l-2.647 2.646a.5.5 0 0 0 .708.708L8 8.707l2.646 2.647a.5.5 0 0 0 .708-.708L8.707 8l2.647-2.646a.5.5 0 0 0-.708-.708L8 7.293 5.354 4.646z"/></svg>';
    
    statusDiv.innerHTML = `
        <div class="status-message status-${type}">
            ${iconSvg}
            <span>${message}</span>
        </div>
    `;
}

function displayDownloadLinks(files) {
    const downloadsDiv = document.getElementById('downloads');
    
    if (files.length === 0) {
        return;
    }
    
    const downloadHtml = `
        <div class="downloads-container">
            <h3 class="downloads-title">
                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="currentColor" viewBox="0 0 16 16">
                    <path d="M.5 9.9a.5.5 0 0 1 .5.5v2.5a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1v-2.5a.5.5 0 0 1 1 0v2.5a2 2 0 0 1-2 2H2a2 2 0 0 1-2-2v-2.5a.5.5 0 0 1 .5-.5z"/>
                    <path d="M7.646 11.854a.5.5 0 0 0 .708 0l3-3a.5.5 0 0 0-.708-.708L8.5 10.293V1.5a.5.5 0 0 0-1 0v8.793L5.354 8.146a.5.5 0 1 0-.708.708l3 3z"/>
                </svg>
                Downloaded Files
            </h3>
            ${files.map(file => `
                <a href="/download/${encodeURIComponent(file)}" class="download-link" download>
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16" class="download-icon">
                        <path d="M9.293 0H4a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h8a2 2 0 0 0 2-2V4.707A1 1 0 0 0 13.707 4L10 .293A1 1 0 0 0 9.293 0zM9.5 3.5v-2l3 3h-2a1 1 0 0 1-1-1zM4.5 9a.5.5 0 0 1 0-1h7a.5.5 0 0 1 0 1h-7zM4.5 10.5a.5.5 0 0 1 0-1h7a.5.5 0 0 1 0 1h-7z"/>
                    </svg>
                    <span>${file}</span>
                </a>
            `).join('')}
        </div>
    `;
    
    downloadsDiv.innerHTML = downloadHtml;
}

// Add keyboard shortcuts
document.addEventListener('keydown', (e) => {
    // Ctrl/Cmd + Enter to download
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
        e.preventDefault();
        const downloadForm = document.getElementById('download-form');
        downloadForm.dispatchEvent(new Event('submit'));
    }
    
    // Escape to clear URL
    if (e.key === 'Escape') {
        clearUrl();
    }
});

// Add smooth scrolling for better UX
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// Add connection status indicator
window.addEventListener('online', () => {
    showStatus('Connection restored', 'success');
    setTimeout(() => {
        document.getElementById('status').innerHTML = '';
    }, 3000);
});

window.addEventListener('offline', () => {
    showStatus('Connection lost. Please check your internet connection.', 'error');
});