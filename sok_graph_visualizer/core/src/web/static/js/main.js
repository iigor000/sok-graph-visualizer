// Main JavaScript file for SOK Graph Visualizer

// Utility function to get CSRF token from cookies (for Django)
function getCsrfToken() {
  const name = "csrftoken";
  let cookieValue = null;
  if (document.cookie && document.cookie !== "") {
    const cookies = document.cookie.split(";");
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === name + "=") {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

document.addEventListener("DOMContentLoaded", async function () {
  console.log("SOK Graph Visualizer initialized");
  //Filter and search
  bindSearchControls();
  bindFilterControls();
  bindResetGraphControl();

  const cliModal = document.getElementById('cli-modal');
  const cliInput = document.getElementById('cli-input');
  const cliStatusView = document.getElementById('cli-status-view');
  const cliHistoryView = document.getElementById('cli-history');
  const openCliBtn = document.getElementById('open-cli-btn');

  if (openCliBtn && cliInput) {
    openCliBtn.onclick = () => {
      cliModal.hidden = false;
      cliInput.focus();
    };

    const closeCLI = () => {
      cliModal.hidden = true;
      cliInput.value = "";
      if (cliStatusView) {
        cliStatusView.textContent = "Waiting for command..."; 
      }
      if (cliHistoryView) {
        cliHistoryView.innerHTML = "";
      }
    };

    const closeX = document.getElementById('cli-close-x');
    const backdrop = document.getElementById('cli-close-backdrop');
    if (closeX) closeX.onclick = closeCLI;
    if (backdrop) backdrop.onclick = closeCLI;

    cliInput.addEventListener('keypress', async function(e) {
      if (e.key === 'Enter') {
        const command = this.value.trim();
        if (!command) return;

        cliHistoryView.innerHTML += `<div class="cli-row"><span class="cli-prompt">user@graph:~$</span> ${command}</div>`;
        this.value = '';

        try {
          const csrfToken = getCsrfToken();
          const response = await fetch('/api/cli/execute/', {
            method: 'POST',
            headers: { 
              'Content-Type': 'application/json',
              ...(csrfToken ? { "X-CSRFToken": csrfToken } : {}),
            },
            body: JSON.stringify({ command: command })
          });

          const data = await response.json();

          if (data.status_text) {
            cliStatusView.textContent = data.status_text;
            cliStatusView.scrollTop = 0; 
          }

          const statusClass = data.success ? 'cli-success' : 'cli-error';
          cliHistoryView.innerHTML += `<div class="${statusClass}">> ${data.message}</div>`;
          cliHistoryView.scrollTop = cliHistoryView.scrollHeight;

          if (data.success) {
            console.log("[CLI] Success, refreshing graph...");
            await refreshGraph();
          }
        } catch (err) {
          cliHistoryView.innerHTML += `<div style="color: red">System error: ${err}</div>`;
        }
      }
    });
  }

  // Load visualizer plugins
  try {
    await loadVisualizerPlugins();
  } catch (error) {
    console.error("[DEBUG] Error loading visualizer plugins:", error);
  }

  // Workspace management on index is handled by workspace.js
  if (document.getElementById("open-create-workspace-modal")) {
    return;
  }

  // Workspace switching
  document.querySelectorAll(".workspace-item").forEach((item) => {
    item.addEventListener("click", async function () {
      const workspaceId = this.dataset.workspaceId;
      if (workspaceId) {
        // Update UI immediately
        document
          .querySelectorAll(".workspace-item")
          .forEach((i) => i.classList.remove("active"));
        this.classList.add("active");

        // Activate workspace on server via AJAX (no page reload)
        try {
          const headers = {
            "Content-Type": "application/json",
          };

          // Add CSRF token for Django
          const csrfToken = getCsrfToken();
          if (csrfToken) {
            headers["X-CSRFToken"] = csrfToken;
          }

          const response = await fetch(
            `/api/workspace/${workspaceId}/activate`,
            {
              method: "POST",
              headers: headers,
            },
          );

          if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
          }

          const data = await response.json();
          console.log("Workspace activated:", data);

          // Load workspace data
          await loadWorkspace(workspaceId);
        } catch (error) {
          console.error("Failed to activate workspace:", error);
          showError("Failed to activate workspace");
        }
      }
    });
  });
});

// Refresh graph visualization from backend

async function refreshGraph() {
  try {
    const response = await fetch("/render/");

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();

    if (!data.success) {
      showError(data.error || "Failed to render graph");
      return;
    }

    const mainViewContent = document.querySelector(".main-view-content");
    if (!mainViewContent) {
      return;
    }

    mainViewContent.innerHTML = "";
    console.log("[DEBUG] refreshGraph - main view cleared");

    const birdViewCanvas = document.getElementById("bird-view-canvas");
    if (birdViewCanvas) {
      birdViewCanvas.innerHTML =
        "<p>Miniature graph overview will appear here</p>";
      console.log("[DEBUG] refreshGraph - bird view cleared");
    }

    const wrappedHtml = `
      <div id="main" style="width: 100%; height: 100%; position: relative;"></div>
      <script>
      ${data.html}
      </script>
    `;

    const parser = new DOMParser();
    const doc = parser.parseFromString(wrappedHtml, "text/html");

    const mainDiv = doc.querySelector("#main");
    const scripts = doc.querySelectorAll("script");

    console.log("[DEBUG] refreshGraph - found main div:", !!mainDiv);
    console.log("[DEBUG] refreshGraph - found scripts:", scripts.length);

    if (mainDiv) {
      const mainDivClone = mainDiv.cloneNode(true);
      mainViewContent.appendChild(mainDivClone);
      console.log("[DEBUG] refreshGraph - inserted main div");
    }

    vizState = {
      mainScale: 1,
      mainTranslate: { x: 0, y: 0 },
      isDragging: false,
      dragStart: { x: 0, y: 0 },
      svg: null,
      g: null,
    };

    await new Promise((resolve, reject) => {
      let scriptIndex = 0;

      const executeNextScript = () => {
        if (scriptIndex < scripts.length) {
          const script = scripts[scriptIndex];
          console.log("[DEBUG] refreshGraph - executing script", scriptIndex);

          const newScript = document.createElement("script");
          const wrappedCode =
            "(function() {\n" + script.textContent + "\n})();";
          newScript.textContent = wrappedCode;

          newScript.onerror = (err) => {
            console.error("[DEBUG] refreshGraph script error:", err);
            reject(err);
          };

          mainViewContent.appendChild(newScript);
          scriptIndex++;

          setTimeout(executeNextScript, 10);
        } else {
          console.log("[DEBUG] refreshGraph - all scripts executed");

          setTimeout(() => {
            try {
              console.log(
                "[DEBUG] refreshGraph - calling initializeVisualization",
              );
              initializeVisualization();
              resolve();
            } catch (e) {
              reject(e);
            }
          }, 100);
        }
      };

      executeNextScript();
    });

    if (typeof loadTreeView === "function") {
      console.log("[DEBUG] refreshGraph - refreshing tree view");
      await loadTreeView();
    }
  } catch (error) {
    console.error("Error refreshing graph:", error);
    showError("Error refreshing graph");
  }
}
// async function refreshGraph() {
//   try {
//     const response = await fetch("/render/");

//     if (!response.ok) {
//       throw new Error(`HTTP error! status: ${response.status}`);
//     }

//     const data = await response.json();

//     if (!data.success) {
//       showError(data.error || "Failed to render graph");
//       return;
//     }

//     const mainViewContent = document.querySelector(".main-view-content");
//     if (!mainViewContent) {
//       return;
//     }

//     mainViewContent.innerHTML = "";
//     console.log("[DEBUG] refreshGraph - main view cleared");

//     const birdViewCanvas = document.getElementById("bird-view-canvas");
//     if (birdViewCanvas) {
//       birdViewCanvas.innerHTML =
//         "<p>Miniature graph overview will appear here</p>";
//       console.log("[DEBUG] refreshGraph - bird view cleared");
//     }

//     const wrappedHtml = `
//       <div id="main" style="width: 100%; height: 100%; position: relative;"></div>
//       <script>
//       ${data.html}
//       </script>
//     `;

//     const parser = new DOMParser();
//     const doc = parser.parseFromString(wrappedHtml, "text/html");

//     const mainDiv = doc.querySelector("#main");
//     const scripts = doc.querySelectorAll("script");

//     console.log("[DEBUG] refreshGraph - found main div:", !!mainDiv);
//     console.log("[DEBUG] refreshGraph - found scripts:", scripts.length);

//     if (mainDiv) {
//       const mainDivClone = mainDiv.cloneNode(true);
//       mainViewContent.appendChild(mainDivClone);
//       console.log("[DEBUG] refreshGraph - inserted main div");
//     }

//     vizState = {
//       mainScale: 1,
//       mainTranslate: { x: 0, y: 0 },
//       isDragging: false,
//       dragStart: { x: 0, y: 0 },
//       svg: null,
//       g: null,
//     };

//     let scriptIndex = 0;
//     const executeNextScript = () => {
//       if (scriptIndex < scripts.length) {
//         const script = scripts[scriptIndex];
//         console.log("[DEBUG] refreshGraph - executing script", scriptIndex);

//         const newScript = document.createElement("script");
//         const wrappedCode = "(function() {\n" + script.textContent + "\n})();";
//         newScript.textContent = wrappedCode;

//         newScript.onerror = (err) => {
//           console.error("[DEBUG] refreshGraph script error:", err);
//           scriptIndex++;
//           executeNextScript();
//         };

//         mainViewContent.appendChild(newScript);
//         scriptIndex++;

//         setTimeout(executeNextScript, 10);
//       } else {
//         console.log("[DEBUG] refreshGraph - all scripts executed");
//         setTimeout(() => {
//           console.log("[DEBUG] refreshGraph - calling initializeVisualization");
//           initializeVisualization();
//         }, 100);
//       }
//     };

//     executeNextScript();
//   } catch (error) {
//     console.error("Error refreshing graph:", error);
//     showError("Error refreshing graph");
//   }
// }

// Search request
function bindSearchControls() {
  const searchBtn = document.getElementById("search-btn");
  const searchInput = document.getElementById("search-input");

  if (!searchBtn || !searchInput) {
    return;
  }

  searchBtn.addEventListener("click", async function () {
    console.log("Search button clicked");
    const query = searchInput.value.trim();

    if (!query) {
      showError("Please enter a search query");
      return;
    }

    try {
      const csrfToken = getCsrfToken();

      const response = await fetch("/api/search/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...(csrfToken ? { "X-CSRFToken": csrfToken } : {}),
        },
        body: JSON.stringify({ query: query }),
      });

      const data = await response.json();

      if (data.success) {
        await refreshGraph();
      } else {
        showError(data.error || data.message || "Search failed");
      }
    } catch (error) {
      console.error("Search error:", error);
      showError("Error while executing search");
    }
  });

  searchInput.addEventListener("keydown", function (e) {
    if (e.key === "Enter") {
      searchBtn.click();
    }
  });
}

//Filter request
function bindFilterControls() {
  const filterBtn = document.getElementById("filter-btn");
  const filterAttribute = document.getElementById("filter-attribute");
  const filterOperator = document.getElementById("filter-operator");
  const filterValue = document.getElementById("filter-value");

  if (!filterBtn || !filterAttribute || !filterOperator || !filterValue) {
    return;
  }

  filterBtn.addEventListener("click", async function () {
    const attribute = filterAttribute.value.trim();
    const operator = filterOperator.value;
    const value = filterValue.value.trim();

    if (!attribute || !operator || !value) {
      showError("Please fill attribute, operator and value");
      return;
    }
    const expression = `${attribute} ${operator} ${value}`;
    try {
      const csrfToken = getCsrfToken();

      const response = await fetch("/api/filter/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...(csrfToken ? { "X-CSRFToken": csrfToken } : {}),
        },
        body: JSON.stringify({ expression: expression }),
      });

      const data = await response.json();

      if (data.success) {
        await refreshGraph();
      } else {
        showError(data.error || data.message || "Filter failed");
      }
    } catch (error) {
      console.error("Filter error:", error);
      showError("Error while executing filter");
    }
  });
}
//Graph reset request
function bindResetGraphControl() {
  const resetBtn = document.getElementById("reset-graph-btn");
  const searchInput = document.getElementById("search-input");
  const filterAttribute = document.getElementById("filter-attribute");
  const filterOperator = document.getElementById("filter-operator");
  const filterValue = document.getElementById("filter-value");

  if (!resetBtn) {
    return;
  }

  resetBtn.addEventListener("click", async function () {
    try {
      const csrfToken = getCsrfToken();

      const response = await fetch("/api/workspace/reset/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...(csrfToken ? { "X-CSRFToken": csrfToken } : {}),
        },
      });

      const data = await response.json();

      if (data.success) {
        if (searchInput) searchInput.value = "";
        if (filterAttribute) filterAttribute.value = "";
        if (filterOperator) filterOperator.value = "==";
        if (filterValue) filterValue.value = "";

        await refreshGraph();
      } else {
        showError(data.error || data.message || "Reset failed");
      }
    } catch (error) {
      console.error("Reset graph error:", error);
      showError("Error while resetting graph");
    }
  });
}
// Load workspace data
async function loadWorkspace(workspaceId) {
  try {
    console.log("Loading workspace:", workspaceId);
    const response = await fetch(`/api/workspace/${workspaceId}`);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const data = await response.json();
    console.log("Workspace data:", data);

    // TODO: Update tree view, bird view, and main view with workspace data
    updateMainView(data);
  } catch (error) {
    console.error("Failed to load workspace:", error);
    showError("Failed to load workspace");
  }
}

// Update main view with workspace data
function updateMainView(workspaceData) {
  const mainViewContent = document.querySelector(".main-view-content");
  if (mainViewContent) {
    mainViewContent.innerHTML = `<p>Loaded workspace: ${workspaceData.name}</p>`;
    // TODO: Render actual graph visualization
  }
}

// Show error message
function showError(message) {
  const mainViewContent = document.querySelector(".main-view-content");
  if (mainViewContent) {
    mainViewContent.innerHTML = `<p style="color: #dc3545;">${message}</p>`;
  }
}

// Utility function for making API calls
async function apiCall(endpoint, options = {}) {
  try {
    const response = await fetch(endpoint, {
      headers: {
        "Content-Type": "application/json",
        ...options.headers,
      },
      ...options,
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error("API call failed:", error);
    throw error;
  }
}

// Load and populate visualizer plugins
async function loadVisualizerPlugins() {
  const visualizerSelect = document.getElementById("visualizer-select");
  if (!visualizerSelect) {
    return;
  }

  try {
    const response = await fetch("/api/plugins/visualizers/");

    if (!response.ok) {
      return;
    }

    const pluginResponse = await response.json();

    const plugins = pluginResponse.plugins || [];

    // Add visualizer options
    plugins.forEach((plugin) => {
      const option = document.createElement("option");
      option.value = plugin.id;
      option.textContent = plugin.name;
      visualizerSelect.appendChild(option);
    });

    // Add change event listener
    visualizerSelect.addEventListener("change", async function () {
      const visualizerId = this.value;

      if (!visualizerId) {
        return;
      }

      try {
        await selectVisualizer(visualizerId);
      } catch (error) {
        console.error("Error selecting visualizer:", error);
      }
    });
  } catch (error) {
    console.error("Error loading visualizer plugins:", error);
  }
}

// Execute the SELECT_VISUALIZER command
async function selectVisualizer(visualizerId) {
  try {
    // Clear previous visualization state
    console.log("[DEBUG] selectVisualizer - clearing previous state");
    vizState = {
      mainScale: 1,
      mainTranslate: { x: 0, y: 0 },
      isDragging: false,
      dragStart: { x: 0, y: 0 },
      svg: null,
      g: null,
    };

    // Get CSRF token for Django
    const csrfToken = getCsrfToken();
    const headers = {
      "Content-Type": "application/json",
    };
    if (csrfToken) {
      headers["X-CSRFToken"] = csrfToken;
    }

    console.log(
      "[DEBUG] selectVisualizer - sending request for visualizer:",
      visualizerId,
    );

    // Send request to set visualizer for active workspace
    const response = await fetch("/api/workspace/visualizer/", {
      method: "POST",
      headers: headers,
      body: JSON.stringify({
        visualizer_id: visualizerId,
      }),
    });

    console.log("[DEBUG] selectVisualizer - response status:", response.status);

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    console.log(
      "[DEBUG] selectVisualizer - response received, success:",
      data.success,
    );

    if (data.success) {
      // Update the main view with the rendered graph
      if (data.html) {
        const mainViewContent = document.querySelector(".main-view-content");
        console.log(
          "[DEBUG] selectVisualizer - mainViewContent element found:",
          !!mainViewContent,
        );

        if (mainViewContent) {
          // Clear the main view content completely
          mainViewContent.innerHTML = "";
          console.log("[DEBUG] selectVisualizer - main view cleared");

          // Clear bird view
          const birdViewCanvas = document.getElementById("bird-view-canvas");
          if (birdViewCanvas) {
            birdViewCanvas.innerHTML =
              "<p>Miniature graph overview will appear here</p>";
            console.log("[DEBUG] selectVisualizer - bird view cleared");
          }

          // Extract script tags and content from HTML
          const htmlContent = data.html;
          const parser = new DOMParser();
          const doc = parser.parseFromString(htmlContent, "text/html");

          // Get the main div and scripts
          const mainDiv = doc.querySelector("#main");
          const scripts = doc.querySelectorAll("script");

          console.log("[DEBUG] selectVisualizer - found main div:", !!mainDiv);
          console.log(
            "[DEBUG] selectVisualizer - found scripts:",
            scripts.length,
          );

          // Insert the main div
          if (mainDiv) {
            const mainDivClone = mainDiv.cloneNode(true);
            mainViewContent.appendChild(mainDivClone);
            console.log("[DEBUG] selectVisualizer - inserted main div");
          }

          // Execute scripts sequentially, each in its own scope
          let scriptIndex = 0;
          const executeNextScript = () => {
            if (scriptIndex < scripts.length) {
              const script = scripts[scriptIndex];
              console.log(
                "[DEBUG] selectVisualizer - executing script",
                scriptIndex,
              );
              const newScript = document.createElement("script");
              // Wrap script content in IIFE to avoid variable redeclaration errors
              const wrappedCode =
                "(function() {\n" + script.textContent + "\n})();";
              newScript.textContent = wrappedCode;
              newScript.onerror = (err) => {
                console.error("[DEBUG] Script error:", err);
                scriptIndex++;
                executeNextScript();
              };
              mainViewContent.appendChild(newScript);
              scriptIndex++;
              // Give a tiny bit of time between scripts
              setTimeout(executeNextScript, 10);
            } else {
              console.log("[DEBUG] selectVisualizer - all scripts executed");
              setTimeout(() => {
                console.log(
                  "[DEBUG] selectVisualizer - calling initializeVisualization",
                );
                initializeVisualization();
              }, 100);
            }
          };
          executeNextScript();
        }
      }

      return true;
    } else {
      throw new Error(data.error || "Failed to set visualizer");
    }
  } catch (error) {
    console.error("Error in selectVisualizer:", error);
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
  g: null,
};

// Initialize visualization with zoom, pan, and bird view
function initializeVisualization() {
  console.log("[DEBUG] initializeVisualization called");

  const mainViewCanvas = document.getElementById("main-view-canvas");
  console.log("[DEBUG] main-view-canvas element:", !!mainViewCanvas);

  if (!mainViewCanvas) {
    console.error("[DEBUG] main-view-canvas element not found");
    return;
  }

  // Try to find SVG in the main div
  let mainSvg = mainViewCanvas.querySelector("#main svg");
  console.log("[DEBUG] SVG from #main svg:", !!mainSvg);

  if (!mainSvg) {
    mainSvg = mainViewCanvas.querySelector("svg");
    console.log("[DEBUG] SVG from any svg:", !!mainSvg);
  }

  if (!mainSvg) {
    // Check if main div exists and what's inside it
    const mainDiv = document.getElementById("main");
    console.log("[DEBUG] Found main div:", !!mainDiv);
    if (mainDiv) {
      console.log(
        "[DEBUG] main div innerHTML length:",
        mainDiv.innerHTML.length,
      );
      console.log("[DEBUG] main div children:", mainDiv.children.length);
      mainSvg = mainDiv.querySelector("svg");
      console.log("[DEBUG] SVG inside main div:", !!mainSvg);
    }
  }

  if (!mainSvg) {
    console.error("[DEBUG] SVG not found! Checking all elements:");
    console.log(
      "[DEBUG] All SVGs on page:",
      document.querySelectorAll("svg").length,
    );
    const allSvgs = document.querySelectorAll("svg");
    allSvgs.forEach((svg, i) =>
      console.log(
        `[DEBUG] SVG ${i}:`,
        svg.parentElement.id,
        svg.parentElement.className,
      ),
    );
    return;
  }

  console.log("[DEBUG] Found SVG, initializing...");
  vizState.svg = mainSvg;

  // Create or get the main group
  let g = mainSvg.querySelector("g");
  console.log("[DEBUG] Found group:", !!g);

  if (!g) {
    console.log("[DEBUG] Creating new group for SVG transform");
    // If no group exists, wrap SVG content
    const newG = document.createElementNS("http://www.w3.org/2000/svg", "g");
    while (mainSvg.firstChild) {
      newG.appendChild(mainSvg.firstChild);
    }
    mainSvg.appendChild(newG);
    g = newG;
  }

  vizState.g = g;

  // Set up main view zoom and pan
  console.log("[DEBUG] About to call setupMainViewZoom");
  setupMainViewZoom();

  // Set up bird view
  setupBirdView();

  console.log("[DEBUG] Visualization initialized successfully");
}

// Set up zoom control buttons
// Set up wheel zoom and pan
function setupMainViewZoom() {
  const mainSvg = vizState.svg;
  const mainGroup = vizState.g;

  if (!mainSvg || !mainGroup) {
    console.warn("[DEBUG] setupMainViewZoom - svg or group not found!");
    return;
  }

  console.log("[DEBUG] setupMainViewZoom - watching D3 transforms");

  // Watch for D3 transform changes on the main group
  const observer = new MutationObserver(() => {
    const transform = mainGroup.getAttribute("transform");
    console.log("[DEBUG] D3 transform changed:", transform);

    if (transform) {
      // Parse transform: "translate(x,y) scale(s)" or variations
      const translateMatch = transform.match(
        /translate\(([-\d.]+)[,\s]+([-\d.]+)\)/,
      );
      const scaleMatch = transform.match(/scale\(([-\d.]+)\)/);

      if (translateMatch) {
        vizState.mainTranslate.x = parseFloat(translateMatch[1]);
        vizState.mainTranslate.y = parseFloat(translateMatch[2]);
        console.log("[DEBUG] Extracted translate:", vizState.mainTranslate);
      }

      if (scaleMatch) {
        vizState.mainScale = parseFloat(scaleMatch[1]);
        console.log("[DEBUG] Extracted scale:", vizState.mainScale);
      }

      updateBirdViewRect();
    }
  });

  observer.observe(mainGroup, {
    attributes: true,
    attributeFilter: ["transform"],
  });
  console.log("[DEBUG] MutationObserver attached to main group");
}

// Apply transform to main view
function updateMainViewZoom() {
  if (!vizState.g) {
    return;
  }

  const translateX = vizState.mainTranslate.x;
  const translateY = vizState.mainTranslate.y;
  const scale = vizState.mainScale;

  vizState.g.setAttribute(
    "transform",
    `translate(${translateX},${translateY}) scale(${scale})`,
  );
}

// Set up bird view
function setupBirdView() {
  const mainSvg = vizState.svg;
  const birdViewCanvas = document.getElementById("bird-view-canvas");

  if (!mainSvg || !birdViewCanvas) {
    console.warn("Missing SVG or bird view canvas");
    return;
  }

  // Clear previous bird view
  birdViewCanvas.innerHTML = "";

  // Clone SVG for bird view
  const birdSvg = mainSvg.cloneNode(true);
  birdSvg.style.width = "100%";
  birdSvg.style.height = "100%";

  // Get or set viewBox
  let viewBox = mainSvg.getAttribute("viewBox");
  if (!viewBox) {
    try {
      const bbox = mainSvg.getBBox();
      viewBox = `${bbox.x} ${bbox.y} ${bbox.width} ${bbox.height}`;
    } catch (e) {
      viewBox = "0 0 800 600";
    }
    mainSvg.setAttribute("viewBox", viewBox);
  }

  birdSvg.setAttribute("viewBox", viewBox);
  birdViewCanvas.appendChild(birdSvg);

  // Create visible area rectangle
  const viewBoxParts = viewBox.split(/[\s,]+/).map(Number);
  const vbX = viewBoxParts[0];
  const vbY = viewBoxParts[1];
  const vbWidth = viewBoxParts[2];
  const vbHeight = viewBoxParts[3];

  const rect = document.createElementNS("http://www.w3.org/2000/svg", "rect");
  rect.classList.add("bird-view-rect");
  rect.setAttribute("x", vbX);
  rect.setAttribute("y", vbY);
  rect.setAttribute("width", vbWidth);
  rect.setAttribute("height", vbHeight);

  // Add to SVG layers (on top)
  const birdSvgGroup = birdSvg.querySelector("g");
  if (birdSvgGroup && birdSvgGroup.parentNode === birdSvg) {
    birdSvg.appendChild(rect);
  } else {
    birdSvg.appendChild(rect);
  }

  // Make rectangle draggable to pan main view
  let isDraggingRect = false;

  rect.addEventListener("mousedown", (e) => {
    isDraggingRect = true;
    e.preventDefault();
  });

  document.addEventListener("mousemove", (e) => {
    if (isDraggingRect) {
      const birdRect = birdViewCanvas.getBoundingClientRect();
      const rectX = e.clientX - birdRect.left;
      const rectY = e.clientY - birdRect.top;

      // Calculate SVG coordinates
      const svg = birdSvg;
      const pt = svg.createSVGPoint();
      pt.x = rectX;
      pt.y = rectY;
      const svgCoords = pt.matrixTransform(svg.getScreenCTM().inverse());

      // Calculate pan to center visible rectangle here
      const rectWidth = parseFloat(rect.getAttribute("width"));
      const rectHeight = parseFloat(rect.getAttribute("height"));

      vizState.mainTranslate.x =
        -(svgCoords.x * vizState.mainScale) + birdRect.width / 2;
      vizState.mainTranslate.y =
        -(svgCoords.y * vizState.mainScale) + birdRect.height / 2;

      updateMainViewZoom();
      updateBirdViewRect();
    }
  });

  document.addEventListener("mouseup", () => {
    isDraggingRect = false;
  });

  updateBirdViewRect();
}

// Update bird view rectangle position to match main view viewport
function updateBirdViewRect() {
  console.log("[DEBUG] updateBirdViewRect called");
  const mainViewContent = document.querySelector(".main-view-content");
  const birdViewCanvas = document.getElementById("bird-view-canvas");
  const rect = birdViewCanvas
    ? birdViewCanvas.querySelector(".bird-view-rect")
    : null;

  console.log(
    "[DEBUG] elements found - content:",
    !!mainViewContent,
    "canvas:",
    !!birdViewCanvas,
    "rect:",
    !!rect,
    "svg:",
    !!vizState.svg,
  );

  if (!mainViewContent) {
    console.warn("[DEBUG] updateBirdViewRect - mainViewContent not found");
    return;
  }
  if (!birdViewCanvas) {
    console.warn("[DEBUG] updateBirdViewRect - birdViewCanvas not found");
    return;
  }
  if (!rect) {
    console.warn("[DEBUG] updateBirdViewRect - rect not found");
    console.log(
      "[DEBUG] checking bird-view-canvas contents:",
      birdViewCanvas.innerHTML.substring(0, 200),
    );
    return;
  }
  if (!vizState.svg) {
    console.warn("[DEBUG] updateBirdViewRect - vizState.svg not found");
    return;
  }

  // Get the main SVG's viewBox
  const mainSvg = vizState.svg;
  let viewBoxStr = mainSvg.getAttribute("viewBox");

  // If no viewBox, calculate it from the SVG's bounding box
  if (!viewBoxStr) {
    console.log("[DEBUG] No viewBox found, calculating from SVG bounds");
    try {
      const bbox = mainSvg.getBBox();
      console.log("[DEBUG] SVG bbox:", bbox);
      viewBoxStr = `${bbox.x} ${bbox.y} ${bbox.width} ${bbox.height}`;
      mainSvg.setAttribute("viewBox", viewBoxStr);
      console.log("[DEBUG] Set viewBox to:", viewBoxStr);
    } catch (e) {
      console.warn("[DEBUG] Could not calculate viewBox:", e);
      // Fallback viewBox
      viewBoxStr = "0 0 800 600";
      mainSvg.setAttribute("viewBox", viewBoxStr);
    }
  }

  const viewBoxParts = viewBoxStr.split(/[\s,]+/).map(Number);
  const vbX = viewBoxParts[0];
  const vbY = viewBoxParts[1];
  const vbWidth = viewBoxParts[2];
  const vbHeight = viewBoxParts[3];

  // Get the actual pixel dimensions of the main view container
  const containerWidth = mainViewContent.clientWidth;
  const containerHeight = mainViewContent.clientHeight;

  console.log(
    "[DEBUG] ViewBox:",
    vbWidth,
    "x",
    vbHeight,
    "MainContainer:",
    containerWidth,
    "x",
    containerHeight,
  );

  // What portion of the viewBox is visible depends on:
  // 1. The zoom level (scale) - when zoomed in 2x, we see half as much
  // 2. The container's aspect ratio

  // Visible area in graph coordinates (viewBox space)
  // At scale=1, we should see roughly the entire graph (or what fits the aspect ratio)
  // At scale=2, we see half as much

  // The aspect ratio of what we can see
  const visibleAspect = containerWidth / containerHeight;
  const graphAspect = vbWidth / vbHeight;

  let visibleWidth, visibleHeight;

  if (visibleAspect > graphAspect) {
    // Container is wider than graph - constrain to graph height
    visibleHeight = vbHeight / vizState.mainScale;
    visibleWidth = visibleHeight * visibleAspect;
  } else {
    // Container is narrower than graph - constrain to graph width
    visibleWidth = vbWidth / vizState.mainScale;
    visibleHeight = visibleWidth / visibleAspect;
  }

  // Position based on pan translation (converted to graph coordinates)
  // When translate is positive (moved right), the visible area starts further left
  const visibleX = -vizState.mainTranslate.x / vizState.mainScale;
  const visibleY = -vizState.mainTranslate.y / vizState.mainScale;

  console.log(
    "[DEBUG] Bird rect update - x=" +
      Math.round(visibleX) +
      ", y=" +
      Math.round(visibleY) +
      ", w=" +
      Math.round(visibleWidth) +
      ", h=" +
      Math.round(visibleHeight) +
      " scale=" +
      vizState.mainScale.toFixed(2) +
      " translate=(" +
      Math.round(vizState.mainTranslate.x) +
      "," +
      Math.round(vizState.mainTranslate.y) +
      ")" +
      " containerAspect=" +
      visibleAspect.toFixed(2) +
      " graphAspect=" +
      graphAspect.toFixed(2),
  );

  rect.setAttribute("x", visibleX);
  rect.setAttribute("y", visibleY);
  rect.setAttribute("width", visibleWidth);
  rect.setAttribute("height", visibleHeight);
}
