import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QHBoxLayout,
    QSlider, QLabel, QCheckBox, QFileDialog, QToolBar, QStatusBar,
    QPushButton  # Added missing import
)
from PyQt6.QtGui import QAction
from PyQt6.QtCore import Qt
from src.visualization import VisualizationWidget

class AMVisualizer(QMainWindow):
    def __init__(self):
        super().__init__()
        self._setup_ui()
        self.cli_data = None
    
    def _setup_ui(self):
        # Window configuration
        self.setWindowTitle("AM Toolpath Visualizer")
        self.setGeometry(100, 100, 1200, 800)
        
        # Central widget with dark theme
        central_widget = QWidget()
        central_widget.setStyleSheet("""
            background-color: #2b2b2b; 
            color: #e0e0e0;
            QSlider::groove:horizontal {
                background: #3a3a3a;
                height: 8px;
            }
            QSlider::handle:horizontal {
                background: #61afef;
                width: 16px;
                margin: -4px 0;
                border-radius: 8px;
            }
        """)
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Visualization widget
        self.viz_widget = VisualizationWidget()
        main_layout.addWidget(self.viz_widget, 1)  # Takes 90% of space
        
        # Control panel
        control_layout = QHBoxLayout()
        
        # Layer navigation
        self.layer_label = QLabel("Layer: 0/0")
        control_layout.addWidget(self.layer_label)
        
        self.layer_slider = QSlider(Qt.Orientation.Horizontal)
        self.layer_slider.setMinimum(0)
        self.layer_slider.setMaximum(0)
        self.layer_slider.valueChanged.connect(self._change_layer)
        control_layout.addWidget(self.layer_slider)
        
        # Heat map toggle
        self.heat_toggle = QCheckBox("Show Heat Source")
        self.heat_toggle.stateChanged.connect(self._toggle_heat)
        control_layout.addWidget(self.heat_toggle)
        
        # Add fit to view button
        self.fit_button = QPushButton("Fit to View")
        self.fit_button.clicked.connect(self._fit_to_view)
        control_layout.addWidget(self.fit_button)
        
        main_layout.addLayout(control_layout)
        
        # Toolbar
        toolbar = QToolBar("Main Toolbar")
        toolbar.setMovable(False)
        self.addToolBar(toolbar)
        
        # Open action
        open_action = QAction("Open CLI File", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self._open_file)
        toolbar.addAction(open_action)
        
        # Reset view action
        reset_view_action = QAction("Reset View", self)
        reset_view_action.setShortcut("R")
        reset_view_action.triggered.connect(self._reset_view)
        toolbar.addAction(reset_view_action)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
    
    def _open_file(self):
        """Open a CLI file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open CLI File", "", "CLI Files (*.cli);;All Files (*)"
        )
        
        if file_path:
            try:
                self.status_bar.showMessage(f"Loading {file_path}...")
                QApplication.processEvents()  # Update UI immediately
                
                self.viz_widget.load_cli(file_path)
                # Use actual layers instead of header value
                actual_layers = len(self.viz_widget.cli_data['layers'])
                self.layer_slider.setRange(0, actual_layers - 1)
                self.layer_slider.setValue(0)
                self.layer_label.setText(f"Layer: 0/{actual_layers - 1}")
                # Show summary in status bar
                header_layers = self.viz_widget.cli_data['total_layers_header']
                self.status_bar.showMessage(
                    f"Loaded: {actual_layers} of {header_layers} layers | {file_path}", 
                    5000
                )
            except Exception as e:
                self.status_bar.showMessage(f"Error: {str(e)}", 5000)
    
    def _change_layer(self, layer_idx):
        """Switch to different layer"""
        self.layer_label.setText(f"Layer: {layer_idx}/{self.layer_slider.maximum()}")
        self.viz_widget.plot_layer(layer_idx)
    
    def _toggle_heat(self, state):
        """Toggle heat visualization"""
        self.viz_widget.toggle_heat(state == Qt.CheckState.Checked.value)
    
    def _fit_to_view(self):
        """Fit current layer to view"""
        if hasattr(self.viz_widget, 'plotter'):
            self.viz_widget.plotter.reset_camera()
    
    def _reset_view(self):
        """Reset to default view"""
        if hasattr(self.viz_widget, 'plotter'):
            self.viz_widget.plotter.camera_position = "xy"
            self.viz_widget.plotter.reset_camera()

def main():
    # Configure application
    app = QApplication(sys.argv)
    app.setStyle("Fusion")  # Modern style
    
    # Create and show window
    window = AMVisualizer()
    window.show()
    
    # Start event loop
    sys.exit(app.exec())

if __name__ == "__main__":
    main()