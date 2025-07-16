from PyQt6.QtWidgets import QFileDialog
from PyQt6.QtCore import Qt
from .model.visualization_model import VisualizationModel
from .view.main_window import MainWindow

class AMController:
    def __init__(self):
        self.model = VisualizationModel()
        self.view = MainWindow(self)
        self.current_layer = 0

    def open_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self.view, "Open CLI File", "", "CLI Files (*.cli);;All Files (*)"
        )
        if file_path:
            try:
                self.view.show_message(f"Loading {file_path}...")
                self.model.load_cli(file_path)
                actual_layers = self.model.get_layer_count()
                max_index = actual_layers - 1
                self.current_layer = 0
                self.view.update_layer_ui(0, max_index)
                self.view.viz_widget.plot_layer(self.model, 0)
                
                header_layers = self.model.cli_data['total_layers_header']
                self.view.show_message(
                    f"Loaded: {actual_layers} of {header_layers} layers | {file_path}", 
                    5000
                )
            except Exception as e:
                self.view.show_message(f"Error: {str(e)}", 5000)

    def change_layer(self, layer_idx):
        self.current_layer = layer_idx
        max_index = self.model.get_layer_count() - 1
        self.view.update_layer_ui(layer_idx, max_index)
        self.view.viz_widget.plot_layer(self.model, layer_idx)

    def toggle_heat(self, state):
        self.model.set_heat_model(state == Qt.CheckState.Checked.value)
        self.view.viz_widget.plot_layer(self.model, self.current_layer)

    def fit_to_view(self):
        self.view.viz_widget.plotter.reset_camera()

    def reset_view(self):
        self.view.viz_widget.plotter.camera_position = "xy"
        self.view.viz_widget.plotter.reset_camera()

    def run(self):
        self.view.show()