const loader = document.getElementById("loader");
const serverStatus = document.getElementById("serverstatus");
const STATUS_CHECK_INTERVAL = 12000;  //12 sec

const BASE_URI = "https://api-production-673a.up.railway.app/"
const STATUS_URL = "https://api-production-673a.up.railway.app/status/"
const CATEGORY_URL = "https://api-production-673a.up.railway.app/categories/"

const requestCounter = {
    status: 0,
    wallpaper: 0,
    downloads: 0,
    total: 0,
}

function updateRequestUI() {
    document.getElementById("statusCount").textContent = requestCounter.status;
    document.getElementById("wallpaperCount").textContent = requestCounter.wallpaper;
    document.getElementById("downloadCount").textContent = requestCounter.downloads;
    document.getElementById("totalCount").textContent = requestCounter.total;
}

// Update server status in the UI
function updateStatusUI(status, message) {
    switch (status) {
        case 'running':
            serverStatus.textContent = '✓ Connected';
            serverStatus.style.color = '#28a745';
            break;
        case 'cloning':
            serverStatus.textContent = '⟳ Cloning Repository...';
            serverStatus.style.color = '#ffc107';
            break;
        case 'pulling':
            serverStatus.textContent = '⟳ Updating Repository...';
            serverStatus.style.color = '#ffc107';
            break;
        case 'error':
            serverStatus.textContent = '✗ ' + message;
            serverStatus.style.color = '#dc3545';
            break;
        default:
            serverStatus.textContent = '⟳ Connecting...';
            serverStatus.style.color = '#007bff';
    }
}

async function downloadWallpaper(url, filename) {
    try {
        const response = await fetch(url);
        const blob = await response.blob();
        const downloadUrl = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = downloadUrl;
        link.download = filename;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        window.URL.revokeObjectURL(downloadUrl);
        requestCounter.downloads++
        requestCounter.total++
        updateRequestUI()
    } catch (error) {
        showError('Error downloading wallpaper: ' + error.message);
    }
}

// Check server status
async function checkServerStatus() {
    try {
        const response = await fetch(STATUS_URL);
        const data = await response.json();
        updateStatusUI(data.status, data.message);
        requestCounter.status++
        requestCounter.total++
        updateRequestUI()

        // If server is running and categories haven't been loaded yet
        if (data.status === 'running' &&
            document.getElementById('categorySelect').children.length <= 1) {
            await fetchCategories();
        }
    } catch (error) {
        updateStatusUI('error', 'Server not responding');
    }
}

async function fetchCategories() {
    try {
        const response = await fetch(CATEGORY_URL);
        const data = await response.json();
        const select = document.getElementById('categorySelect');
        select.innerHTML = '';

        data.categories.forEach(category => {
            const option = document.createElement('option');
            option.value = category;
            option.textContent = category;
            select.appendChild(option);
        });
    } catch (error) {
        showError('Error loading categories: ' + error.message);
    }
}

async function fetchWallpaper() {
    const category = document.getElementById('categorySelect').value;
    const errorElement = document.getElementById('errorMessage');
    const infoElement = document.getElementById('wallpaperInfo');
    const imageElement = document.getElementById('wallpaperImage');
    const randomButton = document.getElementById("wallpaper_btn");

    loader.style.display = "block";
    imageElement.style.display = "none";
    randomButton.disabled = true;  // Disable button while loading

    try {
        errorElement.style.display = 'none';
        const response = await fetch(`${BASE_URI}get-wallpaper/?category=${category}`);
        const data = await response.json();

        if (response.ok) {
            requestCounter.wallpaper++
            requestCounter.total++
            updateRequestUI()
            imageElement.style.display = "block";
            imageElement.src = data.wallpaper_url;
            infoElement.innerHTML = `
                <p><strong>Category:</strong> ${data.category}</p>
                <p><strong>Filename:</strong> ${data.filename}</p>
                <button id="download"> <i class="fa-solid fa-download"></i> Download </button>
            `;
            document.getElementById('download').addEventListener('click', () => {
                downloadWallpaper(data.wallpaper_url, data.filename);
            });

            loader.style.display = "none";
        } else {
            loader.style.display = "block";
            imageElement.style.display = "none";
            showError(data.error || '\nFailed to fetch wallpaper');
        }
    } catch (error) {
        loader.style.display = "block";
        imageElement.style.display = "none";
        showError('Error: ' + error.message);
    } finally {
        randomButton.disabled = false;  // Re-enable button after loading
    }
}

function showError(message) {
    const errorElement = document.getElementById('errorMessage');
    errorElement.textContent = message;
    errorElement.style.display = 'block';
}

// Start status checking
checkServerStatus();
setInterval(checkServerStatus, STATUS_CHECK_INTERVAL);