// birdView.js - Bird's eye view functionality
// Provides a live miniature overview of the entire graph with a viewport indicator

let birdViewState = {
    birdSvg: null,
    birdViewRect: null,
    updateAnimationId: null,
    isDraggingRect: false,
    lastContentHash: null,
    lastUpdateTime: 0,
    updateThrottleMs: 250 // Throttle to max 4 updates per second
};

// Set up bird view
function setupBirdView() {
    const mainSvg = vizState.svg;
    const birdViewCanvas = document.getElementById('bird-view-canvas');
    
    if (!mainSvg || !birdViewCanvas) {
        console.warn('Missing SVG or bird view canvas');
        return;
    }
    
    // Clear previous bird view
    birdViewCanvas.innerHTML = '';
    
    // Create initial bird view structure
    createBirdViewSvg();
    
    // Set up continuous syncing with main view
    startContinuousSync();
    
    // Set up viewport rect dragging
    setupViewportRectDragging(birdViewCanvas);
}

// Create the bird view SVG container
function createBirdViewSvg() {
    const birdViewCanvas = document.getElementById('bird-view-canvas');
    
    if (!birdViewCanvas) {
        return;
    }
    
    // Create a new SVG for the bird view
    const birdSvg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    birdSvg.style.width = '100%';
    birdSvg.style.height = '100%';
    birdSvg.setAttribute('viewBox', '0 0 800 600');
    birdSvg.style.pointerEvents = 'none';
    
    // Create a group to hold the content
    const contentGroup = document.createElementNS('http://www.w3.org/2000/svg', 'g');
    contentGroup.classList.add('bird-content');
    birdSvg.appendChild(contentGroup);
    
    // Create the viewport rectangle on top
    const rect = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
    rect.classList.add('bird-view-rect');
    rect.style.pointerEvents = 'auto'; // Enable for rect only
    birdSvg.appendChild(rect);
    
    birdViewCanvas.appendChild(birdSvg);
    
    birdViewState.birdSvg = birdSvg;
    birdViewState.birdViewRect = rect;
    
}

// Continuously sync the bird view with the main view
function startContinuousSync() {
    // Cancel any previous animation frame
    if (birdViewState.updateAnimationId) {
        cancelAnimationFrame(birdViewState.updateAnimationId);
    }
    
    function syncLoop() {
        const mainSvg = vizState.svg;
        const birdSvg = birdViewState.birdSvg;
        
        if (mainSvg && birdSvg) {
            // Get a hash of the current content including positions
            const contentHash = getMainSvgContentHash(mainSvg);
            
            // If content changed, check if enough time has passed since last update
            if (contentHash !== birdViewState.lastContentHash) {
                const now = Date.now();
                if (now - birdViewState.lastUpdateTime >= birdViewState.updateThrottleMs) {
                    birdViewState.lastContentHash = contentHash;
                    birdViewState.lastUpdateTime = now;
                    updateBirdViewContent();
                }
            }
        }
        
        updateBirdViewRect();
        birdViewState.updateAnimationId = requestAnimationFrame(syncLoop);
    }
    
    syncLoop();
}

// Generate a hash of the main SVG's content including node positions
function getMainSvgContentHash(mainSvg) {
    const mainGroup = mainSvg.querySelector('g');
    if (!mainGroup) {
        return null;
    }
    
    let hash = '';
    
    // Get all visual elements and their positions
    const elements = mainGroup.querySelectorAll('circle, ellipse, rect, polygon, path, text, line');
    
    for (const el of elements) {
        // Include element type and position attributes in hash
        hash += el.tagName + ':';
        hash += el.getAttribute('cx') || el.getAttribute('x') || '';
        hash += ',' + (el.getAttribute('cy') || el.getAttribute('y') || '');
        hash += ',' + (el.getAttribute('d') || el.getAttribute('points') || '');
        hash += ',' + (el.getAttribute('class') || '');
        hash += ';';
    }
    
    return hash;
}

// Update the bird view content from main view, keeping it zoomed out
function updateBirdViewContent() {
    const mainSvg = vizState.svg;
    const birdSvg = birdViewState.birdSvg;
    const contentGroup = birdSvg.querySelector('.bird-content');
    
    if (!mainSvg || !birdSvg || !contentGroup) {
        return;
    }
    
    // Clear previous content
    contentGroup.innerHTML = '';
    
    // Get main group that contains all the graph elements
    const mainGroup = mainSvg.querySelector('g');
    if (!mainGroup) {
        return;
    }
    
    // Clone all the visual elements but without the transform
    // This way we see the graph in its original positions, not zoomed/panned
    const nodesToClone = mainGroup.querySelectorAll('circle, ellipse, rect, polygon, path, text, line, [data-node-id]');
    
    for (const node of nodesToClone) {
        const clone = node.cloneNode(true);
        
        // Remove the transform attribute to see the original positions
        clone.removeAttribute('transform');
        
        // Disable interactions on cloned elements
        clone.style.pointerEvents = 'none';
        
        contentGroup.appendChild(clone);
    }
    
    // Calculate and set viewBox to fit all content
    try {
        const bbox = contentGroup.getBBox();
        const padding = 20;
        const newViewBox = `${bbox.x - padding} ${bbox.y - padding} ${bbox.width + padding * 2} ${bbox.height + padding * 2}`;
        birdSvg.setAttribute('viewBox', newViewBox);
        
    } catch (e) {
        console.warn('[DEBUG] Could not calculate bird view bounds:', e);
        birdSvg.setAttribute('viewBox', '0 0 800 600');
    }
}

// Set up viewport rect dragging
function setupViewportRectDragging(birdViewCanvas) {
    const rect = birdViewState.birdViewRect;
    
    if (!rect) {
        return;
    }
    
    rect.addEventListener('mousedown', (e) => {
        birdViewState.isDraggingRect = true;
        e.preventDefault();
    });
    
    document.addEventListener('mousemove', (e) => {
        if (birdViewState.isDraggingRect && birdViewState.birdSvg) {
            const birdRect = birdViewCanvas.getBoundingClientRect();
            const rectX = e.clientX - birdRect.left;
            const rectY = e.clientY - birdRect.top;
            
            // Calculate SVG coordinates
            const svg = birdViewState.birdSvg;
            const pt = svg.createSVGPoint();
            pt.x = rectX;
            pt.y = rectY;
            
            try {
                const svgCoords = pt.matrixTransform(svg.getScreenCTM().inverse());
                
                // Calculate pan to center visible rectangle
                const rectWidth = parseFloat(rect.getAttribute('width'));
                const rectHeight = parseFloat(rect.getAttribute('height'));
                
                vizState.mainTranslate.x = -(svgCoords.x * vizState.mainScale) + (birdRect.width / 2);
                vizState.mainTranslate.y = -(svgCoords.y * vizState.mainScale) + (birdRect.height / 2);
                
                updateMainViewZoom();
                updateBirdViewRect();
            } catch (e) {
                console.warn('[DEBUG] Error calculating SVG coords:', e);
            }
        }
    });
    
    document.addEventListener('mouseup', () => {
        birdViewState.isDraggingRect = false;
    });
}

// Update bird view rectangle position to match main view viewport
function updateBirdViewRect() {
    const mainViewContent = document.querySelector('.main-view-content');
    const birdViewCanvas = document.getElementById('bird-view-canvas');
    const rect = birdViewState.birdViewRect;
    const birdSvg = birdViewState.birdSvg;
    
    if (!mainViewContent || !birdViewCanvas || !rect || !vizState.svg || !birdSvg) {
        return;
    }
    
    // Get the bird view's viewBox (which is fitted to the content)
    const birdViewBoxStr = birdSvg.getAttribute('viewBox');
    const birdViewBoxParts = birdViewBoxStr.split(/[\s,]+/).map(Number);
    const birdVbX = birdViewBoxParts[0];
    const birdVbY = birdViewBoxParts[1];
    const birdVbWidth = birdViewBoxParts[2];
    const birdVbHeight = birdViewBoxParts[3];
    
    // Get the main SVG's viewBox
    const mainSvg = vizState.svg;
    let mainViewBoxStr = mainSvg.getAttribute('viewBox');
    
    // If no viewBox, calculate it from the SVG's bounding box
    if (!mainViewBoxStr) {
        try {
            const bbox = mainSvg.getBBox();
            mainViewBoxStr = `${bbox.x} ${bbox.y} ${bbox.width} ${bbox.height}`;
            mainSvg.setAttribute('viewBox', mainViewBoxStr);
        } catch (e) {
            mainViewBoxStr = '0 0 800 600';
            mainSvg.setAttribute('viewBox', mainViewBoxStr);
        }
    }
    
    const mainViewBoxParts = mainViewBoxStr.split(/[\s,]+/).map(Number);
    const mainVbX = mainViewBoxParts[0];
    const mainVbY = mainViewBoxParts[1];
    const mainVbWidth = mainViewBoxParts[2];
    const mainVbHeight = mainViewBoxParts[3];
    
    // Get the actual pixel dimensions of the main view container
    const containerWidth = mainViewContent.clientWidth;
    const containerHeight = mainViewContent.clientHeight;
    
    // Calculate scale factors between coordinate systems
    const scaleX = birdVbWidth / mainVbWidth;
    const scaleY = birdVbHeight / mainVbHeight;
    
    // Calculate the visible area in graph coordinates
    // This is what portion of the graph we can see at the current zoom level
    const visibleWidth = containerWidth / vizState.mainScale;
    const visibleHeight = containerHeight / vizState.mainScale;
    
    // Calculate the top-left corner of the visible area
    // The pan translation moves the graph, so negative translate means we see content to the right
    const visibleX = -vizState.mainTranslate.x / vizState.mainScale;
    const visibleY = -vizState.mainTranslate.y / vizState.mainScale;
    
    // Map these coordinates from main view space to bird view space
    const mappedX = birdVbX + (visibleX - mainVbX) * scaleX;
    const mappedY = birdVbY + (visibleY - mainVbY) * scaleY;
    const mappedWidth = visibleWidth * scaleX;
    const mappedHeight = visibleHeight * scaleY;
    
    rect.setAttribute('x', mappedX);
    rect.setAttribute('y', mappedY);
    rect.setAttribute('width', mappedWidth);
    rect.setAttribute('height', mappedHeight);
}


