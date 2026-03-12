// Main JavaScript file for SOK Graph Visualizer

// Utility function to get CSRF token from cookies (for Django)
function getCsrfToken() {
    const name = 'csrftoken';
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

document.addEventListener('DOMContentLoaded', function() {
    console.log('SOK Graph Visualizer initialized');

    // Workspace management on index is handled by workspace.js
    if (document.getElementById('open-create-workspace-modal')) {
        return;
    }
    
    // Workspace switching
    document.querySelectorAll('.workspace-item').forEach(item => {
        item.addEventListener('click', async function() {
            const workspaceId = this.dataset.workspaceId;
            if (workspaceId) {
                // Update UI immediately
                document.querySelectorAll('.workspace-item').forEach(i => i.classList.remove('active'));
                this.classList.add('active');
                
                // Activate workspace on server via AJAX (no page reload)
                try {
                    const headers = {
                        'Content-Type': 'application/json'
                    };
                    
                    // Add CSRF token for Django
                    const csrfToken = getCsrfToken();
                    if (csrfToken) {
                        headers['X-CSRFToken'] = csrfToken;
                    }
                    
                    const response = await fetch(`/api/workspace/${workspaceId}/activate`, {
                        method: 'POST',
                        headers: headers
                    });
                    
                    if (!response.ok) {
                        throw new Error(`HTTP error! status: ${response.status}`);
                    }
                    
                    const data = await response.json();
                    console.log('Workspace activated:', data);
                    
                    // Load workspace data
                    await loadWorkspace(workspaceId);
                } catch (error) {
                    console.error('Failed to activate workspace:', error);
                    showError('Failed to activate workspace');
                }
            }
        });
    });
});

// Load workspace data
async function loadWorkspace(workspaceId) {
    try {
        console.log('Loading workspace:', workspaceId);
        const response = await fetch(`/api/workspace/${workspaceId}`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        console.log('Workspace data:', data);
        
        // TODO: Update tree view, bird view, and main view with workspace data
        updateMainView(data);
    } catch (error) {
        console.error('Failed to load workspace:', error);
        showError('Failed to load workspace');
    }
}

// Update main view with workspace data
function updateMainView(workspaceData) {
    const mainViewContent = document.querySelector('.main-view-content');
    if (mainViewContent) {
        mainViewContent.innerHTML = `<p>Loaded workspace: ${workspaceData.name}</p>`;
        // TODO: Render actual graph visualization
    }
}

// Show error message
function showError(message) {
    const mainViewContent = document.querySelector('.main-view-content');
    if (mainViewContent) {
        mainViewContent.innerHTML = `<p style="color: #dc3545;">${message}</p>`;
    }
}

// Utility function for making API calls
async function apiCall(endpoint, options = {}) {
    try {
        const response = await fetch(endpoint, {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('API call failed:', error);
        throw error;
    }
}

