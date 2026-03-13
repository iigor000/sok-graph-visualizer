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

document.addEventListener('DOMContentLoaded', async function() {

    // Load visualizer plugins
    try {
        await loadVisualizerPlugins();
    } catch (error) {
        console.error('[DEBUG] Error loading visualizer plugins:', error);
    }
    
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
        const response = await fetch(`/api/workspace/${workspaceId}`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        
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

// Load and populate visualizer plugins
async function loadVisualizerPlugins() {
    const visualizerSelect = document.getElementById('visualizer-select');
    if (!visualizerSelect) {
        return;
    }
    
    try {
        const response = await fetch('/api/plugins/visualizers/');
        
        if (!response.ok) {
            return;
        }
        
        const pluginResponse = await response.json();
        
        const plugins = pluginResponse.plugins || [];
        
        // Add visualizer options
        plugins.forEach((plugin) => {
            const option = document.createElement('option');
            option.value = plugin.id;
            option.textContent = plugin.name;
            visualizerSelect.appendChild(option);
        });
        
        // Add change event listener
        visualizerSelect.addEventListener('change', async function() {
            const visualizerId = this.value;
            
            if (!visualizerId) {
                return;
            }
            
            try {
                await selectVisualizer(visualizerId);
            } catch (error) {
                console.error('Error selecting visualizer:', error);
            }
        });
        
    } catch (error) {
        console.error('Error loading visualizer plugins:', error);
    }
}

// Execute the SELECT_VISUALIZER command
async function selectVisualizer(visualizerId) {
    try {
        // Clear previous visualization state
        vizState = {
            mainScale: 1,
            mainTranslate: { x: 0, y: 0 },
            isDragging: false,
            dragStart: { x: 0, y: 0 },
            svg: null,
            g: null
        };
        
        // Get CSRF token for Django
        const csrfToken = getCsrfToken();
        const headers = {
            'Content-Type': 'application/json'
        };
        if (csrfToken) {
            headers['X-CSRFToken'] = csrfToken;
        }
        
        
        // Send request to set visualizer for active workspace
        const response = await fetch('/api/workspace/visualizer/', {
            method: 'POST',
            headers: headers,
            body: JSON.stringify({
                visualizer_id: visualizerId
            })
        });
        
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        if (data.success) {
            // Update the main view with the rendered graph
            if (data.html) {
                const mainViewContent = document.querySelector('.main-view-content');
                
                if (mainViewContent) {
                    // Clear the main view content completely
                    mainViewContent.innerHTML = '';
                    
                    // Clear bird view
                    const birdViewCanvas = document.getElementById('bird-view-canvas');
                    if (birdViewCanvas) {
                        birdViewCanvas.innerHTML = '<p>Miniature graph overview will appear here</p>';
                    }
                    
                    // Extract script tags and content from HTML
                    const htmlContent = data.html;
                    const parser = new DOMParser();
                    const doc = parser.parseFromString(htmlContent, 'text/html');
                    
                    // Get the main div and scripts
                    const mainDiv = doc.querySelector('#main');
                    const scripts = doc.querySelectorAll('script');
                    
                    
                    // Insert the main div
                    if (mainDiv) {
                        const mainDivClone = mainDiv.cloneNode(true);
                        mainViewContent.appendChild(mainDivClone);
                    }
                    
                    // Execute scripts sequentially, each in its own scope
                    let scriptIndex = 0;
                    const executeNextScript = () => {
                        if (scriptIndex < scripts.length) {
                            const script = scripts[scriptIndex];
                            const newScript = document.createElement('script');
                            // Wrap script content in IIFE to avoid variable redeclaration errors
                            const wrappedCode = '(function() {\n' + script.textContent + '\n})();';
                            newScript.textContent = wrappedCode;
                            newScript.onerror = (err) => {
                                console.error('Script error:', err);
                                scriptIndex++;
                                executeNextScript();
                            };
                            mainViewContent.appendChild(newScript);
                            scriptIndex++;
                            // Give a tiny bit of time between scripts
                            setTimeout(executeNextScript, 10);
                        } else {
                            setTimeout(() => {
                                initializeVisualization();
                                if (typeof loadTreeView === 'function') {
                                    loadTreeView();
                                }
                            }, 100);
                        }
                    };
                    executeNextScript();
                }
            }
            
            return true;
        } else {
            throw new Error(data.error || 'Failed to set visualizer');
        }
    } catch (error) {
        console.error('Error in selectVisualizer:', error);
        throw error;
    }
}

// Visualization state
let vizState = {
    mainScale: 1,
    mainTranslate: { x: 0, y: 0 },
    isDragging: false,
    dragStart: { x: 0, y: 0 },
    svg: null,
    g: null
};

// Initialize visualization with zoom, pan, and bird view
function initializeVisualization() {
    
    const mainViewCanvas = document.getElementById('main-view-canvas');
    
    if (!mainViewCanvas) {
        return;
    }
    
    // Try to find SVG in the main div
    let mainSvg = mainViewCanvas.querySelector('#main svg');
    
    if (!mainSvg) {
        mainSvg = mainViewCanvas.querySelector('svg');
    }
    
    if (!mainSvg) {
        // Check if main div exists and what's inside it
        const mainDiv = document.getElementById('main');
        if (mainDiv) {
            mainSvg = mainDiv.querySelector('svg');
        }
    }
    
    if (!mainSvg) {
        const allSvgs = document.querySelectorAll('svg');
        allSvgs.forEach((svg, i) => console.log(`[DEBUG] SVG ${i}:`, svg.parentElement.id, svg.parentElement.className));
        return;
    }
    
    vizState.svg = mainSvg;
    
    // Create or get the main group
    let g = mainSvg.querySelector('g');
    
    if (!g) {
        // If no group exists, wrap SVG content
        const newG = document.createElementNS('http://www.w3.org/2000/svg', 'g');
        while (mainSvg.firstChild) {
            newG.appendChild(mainSvg.firstChild);
        }
        mainSvg.appendChild(newG);
        g = newG;
    }
    
    vizState.g = g;
    
    // Set up main view zoom and pan
    setupMainViewZoom();
    
    // Set up bird view
    setupBirdView();
    
}




