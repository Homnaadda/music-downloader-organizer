document.getElementById('download-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const url = document.getElementById('url').value;
    const statusDiv = document.getElementById('status');
    const downloadsDiv = document.getElementById('downloads');
    const loadingSpinner = document.getElementById('loading');

    statusDiv.innerHTML = '';
    downloadsDiv.innerHTML = '';
    loadingSpinner.style.display = 'block';

    try {
        const response = await fetch('/download', {
            method: 'POST',
            body: new FormData(e.target)
        });

        const data = await response.json();
        loadingSpinner.style.display = 'none';

        if (response.ok) {
            statusDiv.innerHTML = data.message;
            
            // Create download links for the files downloaded in the current event
            if (data.files) {
                downloadsDiv.innerHTML = '';
                data.files.forEach(file => {
                    const link = document.createElement('a');
                    link.href = `/download/${encodeURIComponent(file)}`;
                    link.textContent = file;
                    link.className = 'download-link';
                    downloadsDiv.appendChild(link);
                });
            }
        } else {
            statusDiv.innerHTML = `Error: ${data.error}`;
        }
    } catch (error) {
        loadingSpinner.style.display = 'none';
        statusDiv.innerHTML = `Error: ${error.message}`;
    }
});

document.getElementById('organize-button').addEventListener('click', async () => {
    const organizeStatusDiv = document.getElementById('organize-status');
    const organizeLoadingSpinner = document.getElementById('organize-loading');

    organizeStatusDiv.innerHTML = '';
    organizeLoadingSpinner.style.display = 'block';

    try {
        const response = await fetch('/organize', {
            method: 'POST',
        });

        // Ensure loading spinner is hidden regardless of outcome
        const data = await response.json();

        if (response.ok) {
            organizeStatusDiv.innerHTML = data.message;
        } else {
            organizeStatusDiv.innerHTML = `Error: ${data.error}`;
        }
    } catch (error) {
        organizeStatusDiv.innerHTML = `Error: ${error.message}`;
    } finally {
        organizeLoadingSpinner.style.display = 'none';
    }
});
