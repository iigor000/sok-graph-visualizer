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

    if (selectedPlugin.id === 'xml_datasource') {
        const wrapper = document.createElement('div');
        wrapper.className = 'form-field';

        const label = document.createElement('label');
        label.setAttribute('for', 'config-reference_attr');
        label.textContent = 'Reference attribute (optional, default: reference)';

        const input = document.createElement('input');
        input.id = 'config-reference_attr';
        input.name = 'config.reference_attr';
        input.type = 'text';
        input.required = false;
        input.placeholder = 'reference';

        wrapper.appendChild(label);
        wrapper.appendChild(input);
        container.appendChild(wrapper);
    }
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
        
        const content = document.createElement('div');
        content.className = 'workspace-item-content';
        
        const name = document.createElement('span');
        name.className = 'workspace-item-name';
        name.textContent = workspace.name;
        
        const deleteBtn = document.createElement('button');
        deleteBtn.className = 'workspace-item-delete';
        deleteBtn.type = 'button';
        deleteBtn.dataset.workspaceId = workspace.id;
        deleteBtn.dataset.workspaceName = workspace.name;
        deleteBtn.title = 'Delete workspace';
        deleteBtn.innerHTML = '<span class="delete-icon">✕</span>';
        
        // Add direct click listener to delete button
        deleteBtn.addEventListener('click', (e) => {
            console.log('[DEBUG] Direct button click listener triggered');
            e.stopPropagation();
            e.preventDefault();
            openDeleteModal(workspace.id, workspace.name);
        });
        
        content.appendChild(name);
        content.appendChild(deleteBtn);
        item.appendChild(content);

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

    if (typeof loadTreeView === 'function') {
        await loadTreeView();
    }
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

function openDeleteModal(workspaceId, workspaceName) {
    console.log('[DEBUG] openDeleteModal called with:', { workspaceId, workspaceName });
    const modal = document.getElementById('delete-workspace-modal');
    const nameElement = document.getElementById('delete-workspace-name');
    const confirmBtn = document.getElementById('confirm-delete-workspace');
    
    console.log('[DEBUG] Modal elements:', { modal, nameElement, confirmBtn });
    
    if (!modal || !nameElement || !confirmBtn) {
        console.error('[ERROR] Delete modal elements not found');
        return;
    }
    
    nameElement.textContent = workspaceName;
    modal.hidden = false;
    console.log('[DEBUG] Modal opened');
    
    // Remove old event listeners and attach new one
    const newConfirmBtn = confirmBtn.cloneNode(true);
    confirmBtn.parentNode.replaceChild(newConfirmBtn, confirmBtn);
    
    newConfirmBtn.addEventListener('click', async () => {
        console.log('[DEBUG] Confirm delete clicked');
        try {
            clearFeedback();
            await deleteWorkspaceApi(workspaceId);
            closeDeleteModal();
            await refreshWorkspaces();
            showFeedback('Workspace deleted successfully', false);
        } catch (error) {
            console.error('[ERROR] Delete failed:', error);
            showFeedback(error.message, true);
        }
    });
}

function closeDeleteModal() {
    const modal = document.getElementById('delete-workspace-modal');
    if (!modal) {
        return;
    }
    modal.hidden = true;
}

async function deleteWorkspaceApi(workspaceId) {
    const response = await fetch(`/api/workspaces/${workspaceId}`, {
        method: 'DELETE',
        headers: getJsonHeaders()
    });

    const text = await response.text();
    
    try {
        const body = JSON.parse(text);
        if (!response.ok) {
            throw new Error(body.error || 'Failed to delete workspace');
        }
        return body;
    } catch (parseError) {
        throw new Error('Failed to delete workspace - invalid response: ' + parseError.message);
    }
}

document.addEventListener('DOMContentLoaded', async () => {
    const openModalButton = document.getElementById('open-create-workspace-modal');
    const modal = document.getElementById('create-workspace-modal');
    const closeElements = document.querySelectorAll('[data-close-modal="true"]');
    const form = document.getElementById('create-workspace-form');
    const dataSourceSelect = document.getElementById('data-source-select');
    
    // Setup delete modal close handlers
    const deleteModal = document.getElementById('delete-workspace-modal');
    const deleteCloseElements = deleteModal ? deleteModal.querySelectorAll('[data-close-modal="true"]') : [];

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
    
    // Setup delete modal close handlers
    deleteCloseElements.forEach((element) => {
        element.addEventListener('click', closeDeleteModal);
    });

    dataSourceSelect.addEventListener('change', () => {
        const selectedPlugin = plugins.find((plugin) => plugin.id === dataSourceSelect.value);
        renderConfigFields(selectedPlugin);
    });

    // Event delegation for workspace item delete buttons (both static and dynamic)
    const workspaceList = document.getElementById('workspace-list');
    if (workspaceList) {
        console.log('[DEBUG] Setting up event delegation for delete buttons');
        workspaceList.addEventListener('click', (e) => {
            console.log('[DEBUG] Click event on workspace-list', e.target);
            const deleteBtn = e.target.closest('.workspace-item-delete');
            console.log('[DEBUG] Closest delete btn:', deleteBtn);
            if (deleteBtn) {
                e.stopPropagation();
                e.preventDefault();
                const workspaceId = deleteBtn.dataset.workspaceId;
                const workspaceName = deleteBtn.dataset.workspaceName;
                console.log('[DEBUG] Delete button clicked via delegation', { workspaceId, workspaceName });
                if (workspaceId && workspaceName) {
                    openDeleteModal(workspaceId, workspaceName);
                }
            }
        });
    } else {
        console.log('[ERROR] workspace-list element not found');
    }
    
    // Also handle static delete buttons from template if they exist
    const staticDeleteBtns = document.querySelectorAll('.workspace-item-delete');
    console.log('[DEBUG] Found', staticDeleteBtns.length, 'static delete buttons');
    staticDeleteBtns.forEach(btn => {
        btn.addEventListener('click', (e) => {
            console.log('[DEBUG] Static delete button clicked');
            e.stopPropagation();
            e.preventDefault();
            const workspaceId = btn.dataset.workspaceId;
            const workspaceName = btn.dataset.workspaceName;
            if (workspaceId && workspaceName) {
                openDeleteModal(workspaceId, workspaceName);
            }
        });
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

