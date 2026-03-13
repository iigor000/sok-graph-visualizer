// mainView.js - Main visualization view functionality
// Handles zoom, pan, and interaction with the main SVG canvas

// Set up wheel zoom and pan
function setupMainViewZoom() {
    const mainSvg = vizState.svg;
    const mainGroup = vizState.g;
    
    if (!mainSvg || !mainGroup) {
        return;
    }
    
    
    // Watch for D3 transform changes on the main group
    const observer = new MutationObserver(() => {
        const transform = mainGroup.getAttribute('transform');
        
        if (transform) {
            // Parse transform: "translate(x,y) scale(s)" or variations
            const translateMatch = transform.match(/translate\(([-\d.]+)[,\s]+([-\d.]+)\)/);
            const scaleMatch = transform.match(/scale\(([-\d.]+)\)/);
            
            if (translateMatch) {
                vizState.mainTranslate.x = parseFloat(translateMatch[1]);
                vizState.mainTranslate.y = parseFloat(translateMatch[2]);
            }
            
            if (scaleMatch) {
                vizState.mainScale = parseFloat(scaleMatch[1]);
            }
            
            updateBirdViewRect();
        }
    });
    
    observer.observe(mainGroup, { attributes: true, attributeFilter: ['transform'] });
}

// Apply transform to main view
function updateMainViewZoom() {
    if (!vizState.g) {
        return;
    }
    
    const translateX = vizState.mainTranslate.x;
    const translateY = vizState.mainTranslate.y;
    const scale = vizState.mainScale;
    
    vizState.g.setAttribute('transform', 
        `translate(${translateX},${translateY}) scale(${scale})`);
}
