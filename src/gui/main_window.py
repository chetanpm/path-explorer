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
from PyQt6.QtCore import Qt, QSize, pyqtSignal
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
    # Add signals for layer changes
    change_layer_requested = pyqtSignal(int)
    animation_finished = pyqtSignal()
    def __init__(self):
        super().__init__()
        self.dark_mode = True  # Default to dark mode
        self._setup_ui()
        self.cli_data = None
        self.viz_widget.layer_completed.connect(self._on_layer_completed) # required for full layer after layer animation
        
    
    def _setup_ui(self):
        # Set application font with fallbacks
        app_font = QFont("Segoe UI")
        if app_font.exactMatch():
            QApplication.setFont(app_font)
        else:
            # Try fallback fonts
            for font in ["Arial", "Helvetica", "Verdana"]:
                if QFont(font).exactMatch():
                    QApplication.setFont(QFont(font))
                    break
        # Window configuration
        self.setWindowTitle("Path Explorer")
        self.setGeometry(100, 100, 1400, 900)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # Visualization widget
        self.viz_widget = VisualizationWidget()
        self.viz_widget.set_theme("dark")
        main_layout.addWidget(self.viz_widget, 1)
        
        # Control panel
        control_frame = QFrame()
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
        layer_container = QWidget()
        layer_layout = QVBoxLayout(layer_container)
        layer_layout.setContentsMargins(0, 0, 0, 0)
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
        self.addToolBar(toolbar)

        # Add actions to toolbar
        open_action = QAction(get_icon("open") + " Open CLI", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self._open_file)
        open_action.setFont(QFont("Segoe UI", 10))
        toolbar.addAction(open_action)
        
        reset_view_action = QAction(get_icon("reset") + " Reset View", self)
        reset_view_action.setShortcut("R")
        reset_view_action.triggered.connect(self._reset_view)
        reset_view_action.setFont(QFont("Segoe UI", 10))
        toolbar.addAction(reset_view_action)
        
        self.theme_action = QAction(get_icon("theme", self.dark_mode) + " Light Mode", self)
        self.theme_action.triggered.connect(self._toggle_theme)
        self.theme_action.setFont(QFont("Segoe UI", 10))
        toolbar.addAction(self.theme_action)
        
        toolbar.addSeparator()
        
        # Animation controls
        self.play_action = QAction(get_icon("play") + " Play", self)
        self.play_action.setObjectName("play")
        self.play_action.triggered.connect(self.start_single_animation)
        toolbar.addAction(self.play_action)
        
        self.pause_action = QAction(get_icon("pause") + " Pause", self)
        self.pause_action.setObjectName("pause")
        self.pause_action.triggered.connect(self._pause_animation)
        toolbar.addAction(self.pause_action)
        
        self.stop_action = QAction(get_icon("stop") + " Stop", self)
        self.stop_action.setObjectName("stop")
        self.stop_action.triggered.connect(self._stop_animation)
        toolbar.addAction(self.stop_action)
        
        self.continuous_action = QAction(get_icon("play") + " Continuous Play", self)
        self.continuous_action.setObjectName("continuous")
        self.continuous_action.triggered.connect(self._play_continuous)
        toolbar.addAction(self.continuous_action)

        # Animation speed control
        speed_container = QWidget()
        speed_layout = QVBoxLayout(speed_container)
        speed_layout.setContentsMargins(0, 0, 0, 0)
        speed_label = QLabel("Speed:")
        control_layout.addWidget(speed_label)

        self.speed_slider = QSlider(Qt.Orientation.Horizontal)
        self.speed_slider.setRange(1, 500)  # 1ms to 500ms
        self.speed_slider.setValue(1)
        self.speed_slider.valueChanged.connect(self._change_speed)
        self.speed_slider.setStyleSheet(get_dynamic_styles(self.dark_mode, "slider"))
        self.speed_slider.setMinimumHeight(40)
        speed_layout.addWidget(self.speed_slider)
        control_layout.addWidget(self.speed_slider)

        # Status bar
        self.status_bar = QStatusBar()
        self.status_bar.setFont(QFont("Segoe UI", 9))
        if self.dark_mode:
            self.status_bar.setStyleSheet("""
                QStatusBar {
                    background-color: #2b2b2b;
                    color: #e0e0e0;
                    border-top: 1px solid #444;
                }
            """)
        else:
            self.status_bar.setStyleSheet("""
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

        self.change_layer_requested.connect(self._on_change_layer_requested)
        self.animation_finished.connect(self._on_animation_finished)

    def start_single_animation(self):
        """Start animation for current layer without forcing heat"""
        if self.viz_widget.cli_data:
            self.viz_widget.start_animation(
                self.layer_slider.value(),
                continuous=False
            )

    def start_animation_with_heat(self):
        """Start animation with proper heat handling"""
        if not self.viz_widget.cli_data:
            return
            
        # Enable heat visualization if not already enabled
        if not self.heat_toggle.isChecked():
            self.heat_toggle.setChecked(True)
            self._toggle_heat(Qt.CheckState.Checked.value)
            
        self.viz_widget.start_animation(
            self.layer_slider.value(),
            continuous=self.continuous_action.isChecked()
        )

    def _on_layer_completed(self, next_layer):
        """Handle layer completion during continuous animation"""
        # Update UI first
        self.layer_slider.setValue(next_layer)
        self.layer_label.setText(f"Layer: {next_layer}/{self.layer_slider.maximum()}")
        self.status_bar.showMessage(f"Starting layer {next_layer}", 1000)
        
        # Process events to ensure UI updates
        QApplication.processEvents()
        
        # Start animation for next layer
        self.viz_widget.start_animation(next_layer, continuous=True)

        
    def _play_continuous(self):
        """Start continuous animation across layers"""
        if self.viz_widget.cli_data:
            # Reset heat accumulation
            self.viz_widget.layer_heat_grids = {}
                
            # Start animation
            self.viz_widget.start_animation(
                self.layer_slider.value(),
                continuous=True
            )
    
    def _change_layer(self, layer_idx):
        """Switch to different layer"""
        # Stop animation if running
        if self.viz_widget.is_animating:
            self.viz_widget.stop_animation()
            
        self.layer_label.setText(f"Layer: {layer_idx}/{self.layer_slider.maximum()}")
        self.viz_widget.plot_layer(layer_idx)

    def _on_change_layer_requested(self, layer_idx):
        """Handle request to change layer from visualization"""
        self.layer_slider.setValue(layer_idx)
        self.layer_label.setText(f"Layer: {layer_idx}/{self.layer_slider.maximum()}")
        self.status_bar.showMessage(f"Starting layer {layer_idx}", 1000)

    def _on_animation_finished(self):
        """Handle animation completion"""
        self.status_bar.showMessage("Animation completed", 3000)

    def _change_speed(self, value):
        """Change animation speed"""
        if hasattr(self.viz_widget, 'animation_timer'):
            self.viz_widget.animation_speed = value
            if self.viz_widget.is_animating:
                self.viz_widget.animation_timer.setInterval(value)

    def _play_animation(self):
        """Start or resume animation for current layer"""
        if self.viz_widget.cli_data:
            if not self.viz_widget.is_animating:
                # Start single layer animation
                self.viz_widget.start_animation(self.layer_slider.value())
            else:
                # Resume paused animation
                self.viz_widget.animation_timer.start(self.viz_widget.animation_speed)
    
    def _pause_animation(self):
        """Pause animation"""
        if self.viz_widget.is_animating:
            self.viz_widget.animation_timer.stop()
    
    def _stop_animation(self):
        """Stop animation"""
        self.viz_widget.stop_animation()
        # Redraw current layer
        if self.viz_widget.cli_data:
            self.viz_widget.plot_layer(self.layer_slider.value())

    def _set_view_mode(self, mode):
        """Switch between layer and 3D view"""
        self.viz_widget.set_view_mode(mode)
        if mode == "full":
            self.layer_slider.setEnabled(False)
            #self.heat_toggle.setEnabled(False)
            self.status_bar.showMessage("3D full part view", 3000)
        else:
            self.layer_slider.setEnabled(True)
            #self.heat_toggle.setEnabled(True)
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
        # Safely re-render current view
        try:
            if hasattr(self.viz_widget, 'cli_data') and self.viz_widget.cli_data:
                QApplication.processEvents()
                if self.viz_widget.view_mode == "full":
                    self.viz_widget.show_full_part()
                else:
                    self.viz_widget.plot_layer(self.viz_widget.current_layer)
        except Exception as e:
            print(f"Error during theme switch: {e}")
            self.status_bar.showMessage(f"Render error: {str(e)}", 5000)
    
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