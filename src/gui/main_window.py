# =====================
# main_window.py
# =====================
import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QHBoxLayout,
    QSlider, QLabel, QCheckBox, QFileDialog, QToolBar, QStatusBar,
    QPushButton, QFrame
)
from PyQt6.QtGui import QAction, QFont
from PyQt6.QtCore import Qt, QSize
from .visualization import VisualizationWidget
from src.core.theme_manager import ThemeManager
from .styles import get_dynamic_styles

# For icons, we'll use emoji as fallback
def get_icon(name, dark_mode=True):
    icons = {
        "open": "📂",
        "reset": "🔄",
        "theme": "🌙" if dark_mode else "☀️",
        "3d": "📦",
        "layer": "📋",
        "fit": "🔍"
    }
    return icons.get(name, "")


class AMVisualizer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.dark_mode = True  # Default to dark mode
        self._setup_ui()
        self.cli_data = None
    
    def _setup_ui(self):
        # Window configuration
        self.setWindowTitle("Path Explorer")
        self.setGeometry(100, 100, 1400, 900)
        
        # Central widget (no hardcoded stylesheet)
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # Visualization widget
        self.viz_widget = VisualizationWidget()
        self.viz_widget.set_theme("dark")  # Set initial theme
        main_layout.addWidget(self.viz_widget, 1)  # Takes 90% of space
        
        # Control panel with modern styling
        control_frame = QFrame()
        control_frame.setFrameShape(QFrame.Shape.StyledPanel)
        control_frame.setStyleSheet("""
            QFrame {
                background-color: #333;
                border-radius: 8px;
                padding: 10px;
            }
        """ if self.dark_mode else """
            QFrame {
                background-color: #f0f0f0;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        control_layout = QHBoxLayout(control_frame)
        
        # Layer navigation
        self.layer_label = QLabel("Layer: 0/0")
        self.layer_label.setFont(QFont("Segoe UI", 10))
        control_layout.addWidget(self.layer_label)
        
        self.layer_slider = QSlider(Qt.Orientation.Horizontal)
        self.layer_slider.setMinimum(0)
        self.layer_slider.setMaximum(0)
        self.layer_slider.valueChanged.connect(self._change_layer)
        self.layer_slider.setStyleSheet(get_dynamic_styles(self.dark_mode, "slider"))
        control_layout.addWidget(self.layer_slider, 4)
        
        # Heat map toggle
        self.heat_toggle = QCheckBox("Show Heat Source")
        self.heat_toggle.setFont(QFont("Segoe UI", 10))
        self.heat_toggle.stateChanged.connect(self._toggle_heat)
        control_layout.addWidget(self.heat_toggle)
        
        # Fit to view button
        self.fit_button = QPushButton(get_icon("fit") + " Fit View")
        self.fit_button.setFont(QFont("Segoe UI", 10))
        self.fit_button.clicked.connect(self._fit_to_view)
        self.fit_button.setStyleSheet(get_dynamic_styles(self.dark_mode, "button"))
        control_layout.addWidget(self.fit_button)
        
        # 3D Preview button
        self.view_3d_button = QPushButton(get_icon("3d") + " 3D Preview")
        self.view_3d_button.setFont(QFont("Segoe UI", 10))
        self.view_3d_button.clicked.connect(self._toggle_3d_view)
        self.view_3d_button.setStyleSheet(get_dynamic_styles(self.dark_mode, "button"))
        control_layout.addWidget(self.view_3d_button)
        
        main_layout.addWidget(control_frame)

        # Modern toolbar
        toolbar = QToolBar("Main Toolbar")
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(24, 24))
        toolbar.setStyleSheet("""
            QToolBar {
                background-color: #2b2b2b;
                border-bottom: 1px solid #444;
                spacing: 10px;
                padding: 5px;
            }
            QToolButton {
                padding: 5px;
                border-radius: 4px;
            }
            QToolButton:hover {
                background-color: #3a3a3a;
            }
        """ if self.dark_mode else """
            QToolBar {
                background-color: #f0f0f0;
                border-bottom: 1px solid #ddd;
                spacing: 10px;
                padding: 5px;
            }
            QToolButton:hover {
                background-color: #e0e0e0;
            }
        """)
        self.addToolBar(toolbar)

        
        # Open action with icon
        open_action = QAction(get_icon("open") + " Open CLI", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self._open_file)
        open_action.setFont(QFont("Segoe UI", 10))
        toolbar.addAction(open_action)
        
        # Reset view action
        reset_view_action = QAction(get_icon("reset") + " Reset View", self)
        reset_view_action.setShortcut("R")
        reset_view_action.triggered.connect(self._reset_view)
        reset_view_action.setFont(QFont("Segoe UI", 10))
        toolbar.addAction(reset_view_action)
        
        # Theme toggle action
        self.theme_action = QAction(get_icon("theme", self.dark_mode) + " Light Mode", self)
        self.theme_action.triggered.connect(self._toggle_theme)
        self.theme_action.setFont(QFont("Segoe UI", 10))
        toolbar.addAction(self.theme_action)
        
        # Add spacer
        toolbar.addSeparator()
        
        # Status bar with modern styling
        self.status_bar = QStatusBar()
        self.status_bar.setFont(QFont("Segoe UI", 9))
        self.status_bar.setStyleSheet("""
            QStatusBar {
                background-color: #2b2b2b;
                color: #e0e0e0;
                border-top: 1px solid #444;
            }
        """ if self.dark_mode else """
            QStatusBar {
                background-color: #f0f0f0;
                color: #333;
                border-top: 1px solid #ddd;
            }
        """)
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
        
        # Apply initial styles
        self.centralWidget().setStyleSheet(get_dynamic_styles(self.dark_mode))
    
    def _set_view_mode(self, mode):
        """Switch between layer and 3D view"""
        self.viz_widget.set_view_mode(mode)
        if mode == "full":
            self.layer_slider.setEnabled(False)
            self.heat_toggle.setEnabled(False)
            self.status_bar.showMessage("3D full part view", 3000)
        else:
            self.layer_slider.setEnabled(True)
            self.heat_toggle.setEnabled(True)
            self.status_bar.showMessage("Layer view", 3000)
    
    def _open_file(self):
        """Open a CLI file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open CLI File", "", "CLI Files (*.cli);;All Files (*)"
        )
        
        if file_path:
            try:
                self.status_bar.showMessage(f"Loading {file_path}...")
                QApplication.processEvents()
                
                self.viz_widget.load_cli(file_path)
                actual_layers = len(self.viz_widget.cli_data['layers'])
                self.layer_slider.setRange(0, actual_layers - 1)
                self.layer_slider.setValue(0)
                self.layer_label.setText(f"Layer: 0/{actual_layers - 1}")
                
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
        visible = state == Qt.CheckState.Checked.value
        print(f"Toggling heat visualization: {visible}")
        
        if visible:
            from src.core.heat_model import HeatSource
            # Use a very small sigma for precise microscope view
            sigma = 0.1  # Focused heat spread
            max_temp = 1000  # Fixed max temperature
            
            self.viz_widget.heat_model = HeatSource(
                max_temp=max_temp,
                sigma=sigma
            )
            print(f"Heat model params: sigma={sigma:.4f}mm (microscope view)")
        else:
            self.viz_widget.heat_model = None
        
        # Re-render current layer
        if self.viz_widget.cli_data:
            self.viz_widget.plot_layer(self.viz_widget.current_layer)
    
    def _fit_to_view(self):
        """Fit current view to content"""
        if hasattr(self.viz_widget, 'plotter'):
            self.viz_widget.plotter.reset_camera()
    
    def _reset_view(self):
        """Reset to default view"""
        if hasattr(self.viz_widget, 'plotter'):
            self.viz_widget.plotter.camera_position = "xy"
            self.viz_widget.plotter.reset_camera()
    
    def _toggle_3d_view(self):
        """Toggle 3D preview"""
        if self.viz_widget.view_mode == "layer":
            self._set_view_mode("full")
            self.view_3d_button.setText(get_icon("layer") + " Layer View")
        else:
            self._set_view_mode("layer")
            self.view_3d_button.setText(get_icon("3d") + " 3D Preview")
    
    def _toggle_theme(self):
        """Toggle between light and dark themes"""
        self.dark_mode = not self.dark_mode
        
        # Apply theme to application
        plotter_bg = ThemeManager.apply_theme(QApplication.instance(), self.dark_mode)
        
        # Update plotter
        self.viz_widget.plotter.set_background(plotter_bg)
        theme_name = "dark" if self.dark_mode else "light"
        self.viz_widget.set_theme(theme_name)
        
        # Update theme action
        if self.dark_mode:
            self.theme_action.setText("☀️ Light Mode")
            self.theme_action.setIconText("☀️ Light Mode")
        else:
            self.theme_action.setText("🌙 Dark Mode")
            self.theme_action.setIconText("🌙 Dark Mode")
        
        # Update UI styles
        self.centralWidget().setStyleSheet(get_dynamic_styles(self.dark_mode))
        
        # Update toolbar icons
        self._update_ui_for_theme()
        
        self.status_bar.showMessage(f"Switched to {'dark' if self.dark_mode else 'light'} mode", 3000)
    
    def _update_ui_for_theme(self):
        """Update UI elements for current theme"""
        # Update button styles
        self.fit_button.setStyleSheet(get_dynamic_styles(self.dark_mode, "button"))
        self.view_3d_button.setStyleSheet(get_dynamic_styles(self.dark_mode, "button"))
        self.layer_slider.setStyleSheet(get_dynamic_styles(self.dark_mode, "slider"))
        
        # Update control frame
        control_frame = self.centralWidget().layout().itemAt(1).widget()
        if self.dark_mode:
            control_frame.setStyleSheet("""
                QFrame {
                    background-color: #333;
                    border-radius: 8px;
                    padding: 10px;
                }
            """)
        else:
            control_frame.setStyleSheet("""
                QFrame {
                    background-color: #f0f0f0;
                    border-radius: 8px;
                    padding: 10px;
                }
            """)
        
        # Update status bar
        self.status_bar.setStyleSheet("""
            QStatusBar {
                background-color: #2b2b2b;
                color: #e0e0e0;
                border-top: 1px solid #444;
            }
        """ if self.dark_mode else """
            QStatusBar {
                background-color: #f0f0f0;
                color: #333;
                border-top: 1px solid #ddd;
            }
        """)
        
        # Update toolbar
        toolbar = self.findChild(QToolBar)
        if toolbar:
            if self.dark_mode:
                toolbar.setStyleSheet("""
                    QToolBar {
                        background-color: #2b2b2b;
                        border-bottom: 1px solid #444;
                        spacing: 10px;
                        padding: 5px;
                    }
                    QToolButton {
                        padding: 5px;
                        border-radius: 4px;
                    }
                    QToolButton:hover {
                        background-color: #3a3a3a;
                    }
                """)
            else:
                toolbar.setStyleSheet("""
                    QToolBar {
                        background-color: #f0f0f0;
                        border-bottom: 1px solid #ddd;
                        spacing: 10px;
                        padding: 5px;
                    }
                    QToolButton:hover {
                        background-color: #e0e0e0;
                    }
                """)

def main():
    # Configure application
    app = QApplication(sys.argv)
    
    # Apply the initial theme (dark mode) to the application
    plotter_bg = ThemeManager.apply_theme(app, dark_mode=True)
    
    # Create and show window
    window = AMVisualizer()
    # Set the plotter background to match the initial theme
    window.viz_widget.plotter.set_background(plotter_bg)
    window.show()
    
    # Start event loop
    sys.exit(app.exec())

if __name__ == "__main__":
    main()