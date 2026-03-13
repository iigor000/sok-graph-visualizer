// tree.js - Tree View for SOK Graph Visualizer
// Handles collapsible tree rendering with cycle detection

const treeState = {
    graph: null,       // { nodes: Map<id, node>, adjacency: Map<id, [id]> }
    expanded: new Set(), // set of currently expanded node IDs
    rootId: null
};

// Called after workspace is activated / graph data changes
async function loadTreeView() {
    const container = document.querySelector('.tree-view-content');
    if (!container) return;

    container.innerHTML = '<p class="tree-info">Loading...</p>';

    try {
        const response = await fetch('/api/workspace/graph');
        if (!response.ok) {
            container.innerHTML = '<p class="tree-info">No graph loaded. Select a workspace first.</p>';
            return;
        }
        const data = await response.json();
        initTree(data);
    } catch (err) {
        console.error('[DEBUG] Failed to load graph:', err);
        container.innerHTML = '<p class="tree-error">Failed to load graph data.</p>';
    }
}

// Can be called directly with graph data
function loadTreeViewFromData(graphData) {
    initTree(graphData);
}

function initTree(graphData) {
    const nodes = new Map();
    const adjacency = new Map();

    for (const node of (graphData.nodes || [])) {
        nodes.set(node.id, node);
        adjacency.set(node.id, []);
    }

    for (const edge of (graphData.edges || [])) {
        if (adjacency.has(edge.source)) {
            adjacency.get(edge.source).push(edge.target);
        }
    }

    treeState.graph = { nodes, adjacency };
    treeState.expanded = new Set();

    // pick root: node with the most outgoing edges (most connected)
    let rootId = null;
    let maxDegree = -1;
    for (const [id, neighbors] of adjacency) {
        if (neighbors.length > maxDegree) {
            maxDegree = neighbors.length;
            rootId = id;
        }
    }
    // fallback just take the first node
    if (!rootId && nodes.size > 0) {
        rootId = nodes.keys().next().value;
    }

    treeState.rootId = rootId;
    treeState.expanded.add(rootId);
    renderTree();
}

function renderTree() {
    const container = document.querySelector('.tree-view-content');
    if (!container || !treeState.graph) return;

    if (!treeState.rootId) {
        container.innerHTML = '<p class="tree-info">Graph is empty.</p>';
        return;
    }

    container.innerHTML = '';

    // root info bar
    const infoBar = document.createElement('div');
    infoBar.className = 'tree-info-bar';
    infoBar.textContent = `Root: ${treeState.rootId} · ${treeState.graph.nodes.size} nodes`;
    container.appendChild(infoBar);

    const ul = document.createElement('ul');
    ul.className = 'tree-root';
    // ancestorPath tracks nodes on the current path to detect cycles
    ul.appendChild(buildTreeNode(treeState.rootId, new Set()));
    container.appendChild(ul);
}

// ecursively build a list for a node
// ancestorPath: Set of node IDs that are ancestors of this node in the current path
function buildTreeNode(nodeId, ancestorPath) {
    const { nodes, adjacency } = treeState.graph;
    const node = nodes.get(nodeId);
    const children = adjacency.get(nodeId) || [];
    const isCycle = ancestorPath.has(nodeId);
    const isExpanded = treeState.expanded.has(nodeId);
    const hasChildren = children.length > 0;

    const li = document.createElement('li');
    li.className = 'tree-node';
    li.dataset.nodeId = nodeId;

    const row = document.createElement('div');
    row.className = 'tree-node-row';
    row.dataset.id = nodeId;

    // cycle: already visited on this path
    if (isCycle) {
        const icon = document.createElement('span');
        icon.className = 'tree-toggle tree-cycle-icon';
        icon.title = 'Cycle detected - this node is an ancestor';
        icon.textContent = '↳↰ ';

        const label = document.createElement('span');
        label.className = 'tree-label tree-cycle';
        label.textContent = `${getNodeLabel(node, nodeId)}`;

        const badge = document.createElement('span');
        badge.className = 'tree-cycle-badge';
        badge.textContent = 'cycle';

        row.appendChild(icon);
        row.appendChild(label);
        row.appendChild(badge);
        li.appendChild(row);
        return li;
    }

    // toggle icon
    const toggle = document.createElement('span');
    if (hasChildren) {
        toggle.className = 'tree-toggle tree-toggle-btn';
        toggle.textContent = isExpanded ? '−' : '+';
        toggle.title = isExpanded ? 'Collapse' : 'Expand';
        toggle.addEventListener('click', (e) => {
            e.stopPropagation();
            toggleNode(nodeId);
        });
    } else {
        toggle.className = 'tree-toggle tree-toggle-leaf';
        toggle.textContent = '·';
    }

    // node label
    const label = document.createElement('span');
    label.className = 'tree-label';
    label.textContent = getNodeLabel(node, nodeId);
    label.title = buildTooltip(node, nodeId);

    if (hasChildren) {
        label.style.cursor = 'pointer';
        label.addEventListener('click', () => {
            toggleNode(nodeId);
            if (typeof window.highlightMainNode === 'function') {
                window.highlightMainNode(nodeId);
            }
        });
    } else {
        // leaf node only heighlit
        label.style.cursor = 'pointer';
        label.addEventListener('click', () => {
            if (typeof window.highlightMainNode === 'function') {
                window.highlightMainNode(nodeId);
            }
        });
    }

    row.appendChild(toggle);
    row.appendChild(label);

    // edge count badge
    if (hasChildren) {
        const badge = document.createElement('span');
        badge.className = 'tree-edge-badge';
        badge.textContent = children.length;
        badge.title = `${children.length} connection${children.length !== 1 ? 's' : ''}`;
        row.appendChild(badge);
    }

    li.appendChild(row);

    // children (only rendered when expanded)
    if (isExpanded && hasChildren) {
        // add current node to path before descending
        const childPath = new Set(ancestorPath);
        childPath.add(nodeId);

        const ul = document.createElement('ul');
        ul.className = 'tree-children';

        for (const childId of children) {
            ul.appendChild(buildTreeNode(childId, childPath));
        }

        li.appendChild(ul);
    }

    return li;
}

function toggleNode(nodeId) {
    if (treeState.expanded.has(nodeId)) {
        treeState.expanded.delete(nodeId);
    } else {
        treeState.expanded.add(nodeId);
    }
        renderTree();
}

// Determine the display label for a node
function getNodeLabel(node, nodeId) {
    if (!node) return nodeId;
    const attrs = node.attributes || {};
    // Try common label attributes in priority order
    const label = attrs.name ?? attrs.n ?? attrs.label ?? attrs.title ?? null;
    if (label) {
        // Show both label and ID if they differ
        return label !== nodeId ? `${label}` : label;
    }
    return nodeId;
}

// Build a tooltip string from node attributes
function buildTooltip(node, nodeId) {
    const lines = [`id: ${nodeId}`];
    if (!node) return lines.join('\n');
    const attrs = node.attributes || {};
    for (const [k, v] of Object.entries(attrs)) {
        if (v !== null && v !== undefined) {
            lines.push(`${k}: ${v}`);
        }
    }
    return lines.join('\n');
}

// Called from workspace.js when a workspace is activated
async function onWorkspaceActivated() {
    await loadTreeView();
}

// Hook into the existing workspace activation flow.
// workspace.js calls refreshWorkspaces → activateWorkspace.
document.addEventListener('workspaceActivated', async () => {
    await loadTreeView();
});

// Also load on DOMContentLoaded if a workspace is already active
document.addEventListener('DOMContentLoaded', async () => {
    await loadTreeView();
});

function highlightTreeNode(nodeId) {
    document.querySelectorAll('.tree-node-row.selected')
        .forEach(el => el.classList.remove('selected'));

    const row = document.querySelector(`.tree-node-row[data-id="${CSS.escape(nodeId)}"]`);
    if (row) {
        row.classList.add('selected');
        row.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
}

window.highlightTreeNode = highlightTreeNode;

document.addEventListener('node-clicked', (e) => {
    highlightTreeNode(e.detail);
});
