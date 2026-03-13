function showFeedback(message, isError = false) {
    const feedback = document.getElementById('workspace-feedback');
    if (!feedback) {
        return;
    }

    feedback.hidden = false;
    feedback.classList.toggle('workspace-alert-error', isError);
    feedback.classList.toggle('workspace-alert-success', !isError);
    feedback.textContent = message;
}

function clearFeedback() {
    const feedback = document.getElementById('workspace-feedback');
    if (!feedback) {
        return;
    }

    feedback.hidden = true;
    feedback.textContent = '';
    feedback.classList.remove('workspace-alert-error', 'workspace-alert-success');
}

function getJsonHeaders() {
    const headers = {
        'Content-Type': 'application/json'
    };
    
    // Get CSRF token from cookie
    const csrfToken = getCookie('csrftoken');
    if (csrfToken) {
        headers['X-CSRFToken'] = csrfToken;
    }
    
    return headers;
}

function getCookie(name) {
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

async function fetchDataSourcePlugins() {
    const response = await fetch('/api/plugins/data-sources');
    
    if (!response.ok) {
        throw new Error('Failed to load data source plugins');
    }
    
    const text = await response.text();
    
    try {
        const json = JSON.parse(text);
        return json;
    } catch (parseError) {
        throw parseError;
    }
}

function renderConfigFields(selectedPlugin) {
    const container = document.getElementById('data-source-config-fields');
    container.innerHTML = '';

    if (!selectedPlugin || !Array.isArray(selectedPlugin.required_config) || selectedPlugin.required_config.length === 0) {
        return;
    }

    selectedPlugin.required_config.forEach((field) => {
        const wrapper = document.createElement('div');
        wrapper.className = 'form-field';

        const label = document.createElement('label');
        label.setAttribute('for', `config-${field.key}`);
        label.textContent = field.description || field.key;

        const input = document.createElement('input');
        input.id = `config-${field.key}`;
        input.name = `config.${field.key}`;
        input.type = 'text';
        input.required = true;
        input.placeholder = field.key;

        wrapper.appendChild(label);
        wrapper.appendChild(input);
        container.appendChild(wrapper);
    });
}

function openModal() {
    const modal = document.getElementById('create-workspace-modal');
    modal.hidden = false;
}

function closeModal() {
    const modal = document.getElementById('create-workspace-modal');
    const form = document.getElementById('create-workspace-form');
    const configFields = document.getElementById('data-source-config-fields');

    modal.hidden = true;
    form.reset();
    configFields.innerHTML = '';
}

async function activateWorkspace(workspaceId) {
    const response = await fetch(`/api/workspace/${workspaceId}/activate`, {
        method: 'POST',
        headers: getJsonHeaders()
    });

    if (!response.ok) {
        const payload = await response.json();
        throw new Error(payload.error || 'Failed to activate workspace');
    }

    return response.json();
}

function renderWorkspaceList(workspaces) {
    const list = document.getElementById('workspace-list');
    list.innerHTML = '';

    workspaces.forEach((workspace) => {
        const item = document.createElement('div');
        item.className = `workspace-item ${workspace.active ? 'active' : ''}`;
        item.dataset.workspaceId = workspace.id;
        item.textContent = workspace.name;

        item.addEventListener('click', async () => {
            try {
                clearFeedback();
                await activateWorkspace(workspace.id);
                await refreshWorkspaces();
            } catch (error) {
                showFeedback(error.message, true);
            }
        });

        list.appendChild(item);
    });

    const createCard = document.createElement('div');
    createCard.id = 'open-create-workspace-modal';
    createCard.className = 'workspace-item workspace-item-create';
    createCard.textContent = '+ Create Workspace';
    createCard.addEventListener('click', () => {
        clearFeedback();
        openModal();
    });
    list.appendChild(createCard);
}

async function refreshWorkspaces() {
    const response = await fetch('/api/workspaces');
    if (!response.ok) {
        throw new Error('Failed to load workspaces');
    }

    const workspaces = await response.json();
    renderWorkspaceList(workspaces);
}

async function createWorkspace(payload) {
    const response = await fetch('/api/workspaces/', {
        method: 'POST',
        headers: getJsonHeaders(),
        body: JSON.stringify(payload)
    });

    const text = await response.text();
    
    try {
        const body = JSON.parse(text);
        if (!response.ok) {
            throw new Error(body.error || 'Failed to create workspace');
        }
        return body;
    } catch (parseError) {
        throw new Error('Failed to create workspace - invalid response: ' + parseError.message);
    }
}

document.addEventListener('DOMContentLoaded', async () => {
    const openModalButton = document.getElementById('open-create-workspace-modal');
    const modal = document.getElementById('create-workspace-modal');
    const closeElements = document.querySelectorAll('[data-close-modal="true"]');
    const form = document.getElementById('create-workspace-form');
    const dataSourceSelect = document.getElementById('data-source-select');

    if (!openModalButton || !modal || !form || !dataSourceSelect) {
        return;
    }

    let plugins = [];

    try {
        clearFeedback();
        const pluginResponse = await fetchDataSourcePlugins();
        
        plugins = pluginResponse.plugins || [];

        plugins.forEach((plugin) => {
            const option = document.createElement('option');
            option.value = plugin.id;
            option.textContent = plugin.name;
            dataSourceSelect.appendChild(option);
        });
    } catch (error) {
        showFeedback(error.message, true);
    }

    openModalButton.addEventListener('click', () => {
        clearFeedback();
        openModal();
    });

    closeElements.forEach((element) => {
        element.addEventListener('click', closeModal);
    });

    dataSourceSelect.addEventListener('change', () => {
        const selectedPlugin = plugins.find((plugin) => plugin.id === dataSourceSelect.value);
        renderConfigFields(selectedPlugin);
    });

    form.addEventListener('submit', async (event) => {
        event.preventDefault();
        clearFeedback();

        const formData = new FormData(form);
        const name = (formData.get('name') || '').toString().trim();
        const dataSourceId = (formData.get('data_source_id') || '').toString().trim();

        const config = {};
        for (const [key, value] of formData.entries()) {
            if (!key.startsWith('config.')) {
                continue;
            }
            config[key.replace('config.', '')] = value;
        }

        try {
            await createWorkspace({
                name: name,
                data_source_id: dataSourceId,
                config: config
            });

            closeModal();
            await refreshWorkspaces();
            showFeedback('Workspace successfully created', false);
        } catch (error) {
            showFeedback(error.message, true);
        }
    });

    try {
        await refreshWorkspaces();
    } catch (error) {
        showFeedback(error.message, true);
    }
});

document.addEventListener('DOMContentLoaded', function() {
    const modal = document.getElementById('cli-modal');
    const input = document.getElementById('cli-input');
    const statusView = document.getElementById('cli-status-view');
    const historyView = document.getElementById('cli-history');
    const mainCanvas = document.getElementById('main-view-canvas');

    document.getElementById('open-cli-btn').onclick = () => {
        modal.hidden = false;
        input.focus();
    };
    
    const closeCLI = () => {
        modal.hidden = true;
        statusView.textContent = "Graph data will be displayed here after first command...";
        historyView.innerHTML = "";
        input.value = "";
    };
    document.getElementById('cli-close-x').onclick = closeCLI;
    document.getElementById('cli-close-backdrop').onclick = closeCLI;

    input.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            const command = this.value.trim();
            if (!command) return;

            historyView.innerHTML += `<div class="cli-row"><span class="cli-prompt">user@graph:~$</span> ${command}</div>`;
            this.value = '';

            fetch('/api/cli/execute/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ command: command })
            })
            .then(res => res.json())
            .then(data => {
                if (data.status_text) {
                    statusView.textContent = data.status_text;
                    statusView.scrollTop = 0; 
                }

                const statusClass = data.success ? 'cli-success' : 'cli-error';
                historyView.innerHTML += `<div class="${statusClass}">> ${data.message}</div>`;
                historyView.scrollTop = historyView.scrollHeight;

                if (data.success && data.graph_html) {
                    mainCanvas.innerHTML = data.graph_html;
                    mainCanvas.querySelectorAll("script").forEach(s => {
                        const newS = document.createElement("script");
                        newS.text = s.text;
                        s.parentNode.replaceChild(newS, s);
                    });
                }
            })
            .catch(err => {
                historyView.innerHTML += `<div style="color: red">System error: ${err}</div>`;
            });
        }
    });
});
