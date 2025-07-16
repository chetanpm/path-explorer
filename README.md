Project Overview

The Path Explorer is a modern PyQt6-based application designed for visualizing additive manufacturing toolpaths from CLI files. It features thermal simulation, 3D preview inspection capabilities for detailed analysis of manufacturing processes.


```html
## Installation

<div class="tabs">
  <input type="radio" name="os" id="windows" checked>
  <label for="windows"><i class="fab fa-windows"></i> Windows</label>
  
  <input type="radio" name="os" id="arch">
  <label for="arch"><i class="fab fa-linux"></i> Arch Linux</label>
  
  <input type="radio" name="os" id="mac">
  <label for="mac"><i class="fab fa-apple"></i> macOS</label>
  
  <div class="content" id="windows-content">
    <pre><code class="language-bash">powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"</code></pre>
  </div>
  
  <div class="content" id="arch-content">
    <pre><code class="language-bash">sudo pacman -S uv</code></pre>
  </div>
  
  <div class="content" id="mac-content">
    <pre><code class="language-bash">brew install uv</code></pre>
  </div>
</div>

<style>
/* Tab container */
.tabs {
  position: relative;
  margin: 2rem 0;
}

/* Hide radio buttons */
.tabs input[type="radio"] {
  display: none;
}

/* Tab labels */
.tabs label {
  display: inline-block;
  padding: 10px 20px;
  cursor: pointer;
  background: #f1f1f1;
  border-radius: 5px 5px 0 0;
  margin-right: 5px;
  font-weight: bold;
  transition: all 0.3s;
}

/* Dark mode support */
@media (prefers-color-scheme: dark) {
  .tabs label {
    background: #2b2b2b;
    color: #e0e0e0;
  }
}

/* Active tab label */
.tabs input[type="radio"]:checked + label {
  background: #1793d1;
  color: white;
}

/* Tab content */
.tabs .content {
  display: none;
  padding: 20px;
  border: 1px solid #ddd;
  border-radius: 0 5px 5px 5px;
  margin-top: -1px;
}

/* Show active content */
#windows:checked ~ #windows-content,
#arch:checked ~ #arch-content,
#mac:checked ~ #mac-content {
  display: block;
}

/* Code block styling */
.content pre {
  background: #f8f8f8;
  padding: 15px;
  border-radius: 5px;
  overflow-x: auto;
}

@media (prefers-color-scheme: dark) {
  .content pre {
    background: #2b2b2b;
  }
}
</style>