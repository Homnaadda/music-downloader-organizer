document.getElementById('download-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const url = document.getElementById('url').value;
    const statusDiv = document.getElementById('status');
    const downloadsDiv = document.getElementById('downloads');
    const loadingSpinner = document.getElementById('loading');
    const downloadButton = e.target.querySelector('button[type="submit"]');

    statusDiv.innerHTML = '';
    downloadsDiv.innerHTML = '';
    loadingSpinner.style.display = 'block';
    downloadButton.disabled = true;

    try {
        const response = await fetch('/download', {
            method: 'POST',
            body: new FormData(e.target)
        });

        const data = await response.json();
        loadingSpinner.style.display = 'none';
        downloadButton.disabled = false;

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
        downloadButton.disabled = false;
        statusDiv.innerHTML = `Error: ${error.message}`;
    }
});

document.getElementById('organize-button').addEventListener('click', async () => {
    const organizeStatusDiv = document.getElementById('organize-status');
    const organizeLoadingSpinner = document.getElementById('organize-loading');
    const organizeButton = document.getElementById('organize-button');

    organizeStatusDiv.innerHTML = '';
    organizeLoadingSpinner.style.display = 'block';
    organizeButton.disabled = true;

    try {
        const response = await fetch('/organize', {
            method: 'POST',
        });

        const data = await response.json();
        organizeLoadingSpinner.style.display = 'none';
        organizeButton.disabled = false;

        if (response.ok) {
            organizeStatusDiv.innerHTML = data.message;
        } else {
            organizeStatusDiv.innerHTML = `Error: ${data.error}`;
        }
    } catch (error) {
        organizeLoadingSpinner.style.display = 'none';
        organizeButton.disabled = false;
        organizeStatusDiv.innerHTML = `Error: ${error.message}`;
    }
});
