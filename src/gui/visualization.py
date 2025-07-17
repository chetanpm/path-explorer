# =====================
# visualization.py
# =====================
import numpy as np
import pyvista as pv
from PyQt6.QtWidgets import QWidget, QVBoxLayout
from PyQt6.QtCore import QTimer
from pyvistaqt import BackgroundPlotter
import time

class VisualizationWidget(QWidget):
    def __init__(self, parent=None):
        self.accumulated_heat = None
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.setLayout(self.layout)
        
        print("Initializing VisualizationWidget...")
        start_time = time.time()
        
        # Create plotter with interactive controls
        self.plotter = BackgroundPlotter(
            show=False,
            toolbar=True,
            menu_bar=False,
            title="ToolPath Visualization"
        )
        # Background will be set by main window
        self.plotter.set_background("#1e1e1e")  # Default dark
        
        # Set initial camera position
        self.plotter.camera_position = "xy"
        
        # Add to layout
        self.layout.addWidget(self.plotter.interactor)
        
        # Initialize state
        self.cli_data = None
        self.heat_model = None
        self.current_layer = 0
        self.theme = "dark"  # Default theme
        self.overall_bounds = None  # Store overall part dimensions
        self.view_mode = "layer"  # 'layer' or 'full'
        self.full_part_mesh = None
        
        # Store camera position between renders
        self.user_camera_position = None
        
        print(f"VisualizationWidget initialized in {time.time() - start_time:.2f} seconds")

        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self._animate_step)
        self.animation_speed = 100  # ms between frames
        self.animation_path = []
        self.current_path_index = 0
        self.is_animating = False
        self.accumulated_heat = None  # For heat accumulation visualization

        self.continuous_mode = False
        self.layer_complete_timer = QTimer()
        self.layer_complete_timer.setSingleShot(True)
        self.layer_complete_timer.timeout.connect(self._start_next_layer)
    
    def _get_path_color(self):
        """Return path color based on current theme"""
        return "white" if self.theme == "dark" else "black"

    def start_animation(self, layer_idx, continuous=False):
        """Prepare and start animation for a layer"""
        if not self.cli_data or layer_idx >= len(self.cli_data['layers']):
            return
            
        self.stop_animation()
        self.is_animating = True
        self.current_layer = layer_idx
        layer = self.cli_data['layers'][layer_idx]
        
        # Prepare animation path
        self.animation_path = []
        z = layer['z']
        for hatch in layer['hatches']:
            if len(hatch) < 2:
                continue
            for i in range(len(hatch) - 1):
                start = hatch[i]
                end = hatch[i+1]
                distance = ((end[0]-start[0])**2 + (end[1]-start[1])**2)**0.5
                num_segments = max(2, int(distance / 0.1))  # 0.1mm resolution
                for t in np.linspace(0, 1, num_segments):
                    x = start[0] + t * (end[0] - start[0])
                    y = start[1] + t * (end[1] - start[1])
                    self.animation_path.append((x, y, z))
        
        self.current_path_index = 0
        self.plotter.clear()
        self._setup_base_visualization(layer)
        self.animation_timer.start(self.animation_speed)
    
    def _animate_step(self):
        """Update animation to next position"""
        if self.current_path_index >= len(self.animation_path) or not self.is_animating:
            if self.continuous_mode:
                # Start transition to next layer
                self.layer_complete_timer.start(1000)  # 1 second pause
            else:
                self.stop_animation()
            return
            
        position = self.animation_path[self.current_path_index]
        self.current_path_index += 1
        
        # Update moving heat spot
        self.plotter.remove_actor("heat_spot")
        spot = None
        
        if self.heat_model:
            try:
                spot, cmap = self.heat_model.create_moving_spot(
                    (position[0], position[1]), 
                    position[2],
                    self.theme
                )
                self.plotter.add_mesh(
                    spot,
                    cmap=cmap,
                    scalars="Temperature",
                    clim=[0, self.heat_model.max_temp],
                    name="heat_spot"
                )
            except Exception as e:
                print(f"Error creating heat spot: {e}")
        
        # Update tool position marker
        self.plotter.remove_actor("tool_position")
        tool = pv.Sphere(radius=0.05, center=position)
        self.plotter.add_mesh(tool, color="red" if self.theme == "dark" else "darkred", name="tool_position")

        
        # Accumulate heat only if spot was created
        if spot:
            if self.accumulated_heat is None:
                self.accumulated_heat = spot
            else:
                try:
                    self.accumulated_heat = self.accumulated_heat.merge(spot)
                except Exception as e:
                    print(f"Error merging heat spots: {e}")
                    self.accumulated_heat = spot
                
            self.plotter.remove_actor("accumulated_heat")
            self.plotter.add_mesh(
                self.accumulated_heat,
                cmap="coolwarm",
                scalars="Temperature",
                clim=[0, self.heat_model.max_temp],
                opacity=0.5,
                name="accumulated_heat"
            )
    
    def _start_next_layer(self):
        """Start animation for the next layer"""
        next_layer = self.current_layer + 1
        total_layers = len(self.cli_data['layers']) if self.cli_data else 0
        
        if next_layer < total_layers:
            # Notify main window to update UI
            if hasattr(self.parent(), 'change_layer_requested'):
                self.parent().change_layer_requested.emit(next_layer)
            
            # Start animation for next layer
            self.start_animation(next_layer, continuous=True)
        else:
            # Reached end of all layers
            self.stop_animation()
            if hasattr(self.parent(), 'animation_finished'):
                self.parent().animation_finished.emit()

    def stop_animation(self):
        """Stop ongoing animation"""
        self.is_animating = False
        self.continuous_mode = False
        self.animation_timer.stop()
        self.layer_complete_timer.stop()
        self.animation_path = []
        self.current_path_index = 0
        self.accumulated_heat = None
    
    def _setup_base_visualization(self, layer):
        """Setup static visualization elements for animation"""
        z = layer['z']
        # Plot hatches as paths
        for hatch in layer['hatches']:
            if len(hatch) < 2:
                continue
            points = np.array([[p[0], p[1], z] for p in hatch])
            poly = pv.lines_from_points(points)
            tube = poly.tube(radius=0.01)
            self.plotter.add_mesh(tube, color="white", name="hatches")
        
        # Add axes and bounds
        if self.overall_bounds:
            min_coords = self.overall_bounds['min']
            max_coords = self.overall_bounds['max']
            self.plotter.add_axes(color="white")
            self.plotter.show_bounds(
                bounds=[
                    min_coords[0], max_coords[0],
                    min_coords[1], max_coords[1],
                    z - 0.01, z + 0.01
                ],
                grid='front',
                location='outer',
                color="white",
            )
    def set_theme(self, theme):
        """Set current theme (dark/light) for visualization"""
        self.theme = theme

    def set_view_mode(self, mode):
        """Set view mode: 'layer' or 'full'"""
        self.view_mode = mode
        if self.cli_data:
            if mode == "full":
                self.show_full_part()
            else:
                self.plot_layer(self.current_layer)
            self.plotter.reset_camera()  # Automatically fit view after mode change
    
    def load_cli(self, file_path):
        """Load and parse CLI file"""
        print(f"Loading CLI file: {file_path}")
        from src.core.cli_parser import parse_cli
        start_time = time.time()
        self.cli_data = parse_cli(file_path)
        self.full_part_mesh = None  # Reset full part mesh
        print(f"Parsed {len(self.cli_data['layers'])} layers in {time.time() - start_time:.2f} seconds")
        
        # Calculate overall bounding box for entire part
        self._calculate_overall_bounds()
        
        # Reset camera position for new file
        self.user_camera_position = None
        self.plot_layer(0)
        self.plotter.reset_camera()  # Automatically fit view after loading
    
    def _calculate_overall_bounds(self):
        """Calculate bounding box for entire part"""
        if not self.cli_data:
            return
            
        all_points = []
        for layer in self.cli_data['layers']:
            z = layer['z']
            for hatch in layer['hatches']:
                for point in hatch:
                    all_points.append([point[0], point[1], z])
        
        if all_points:
            points_array = np.array(all_points)
            min_coords = np.min(points_array, axis=0)
            max_coords = np.max(points_array, axis=0)
            self.overall_bounds = {
                'min': min_coords,
                'max': max_coords,
                'center': (min_coords + max_coords) / 2
            }
            print(f"Overall part dimensions: min={min_coords}, max={max_coords}")
    
    def plot_layer(self, layer_idx):
        """Visualize a specific layer with fixed axes"""
        if not self.cli_data or layer_idx >= len(self.cli_data['layers']):
            print("No CLI data or invalid layer index")
            return
        # Get theme-based path color
        path_color = self._get_path_color()    
        # Save current camera position
        current_camera_position = self.plotter.camera_position
        self.current_layer = layer_idx
        self.plotter.clear()
        layer = self.cli_data['layers'][layer_idx]
        z = layer['z']

        print(f"Plotting layer {layer_idx}...")
        start_time = time.time()
        
        # Save current camera position if user has changed it
        if self.plotter.camera_position != self.user_camera_position:
            self.user_camera_position = self.plotter.camera_position
        
        self.current_layer = layer_idx
        self.plotter.clear()
        layer = self.cli_data['layers'][layer_idx]
        z = layer['z']
        
        # Show original layer number in debug output
        print(f"Layer {layer_idx} (Original: {layer['layer_number']})")

        # Print layer statistics
        num_hatches = len(layer['hatches'])
        print(f"Layer {layer_idx}: z={z:.4f}mm, {num_hatches} hatches")
        
        # Set colors based on theme
        if self.theme == "dark":
            hatch_color = "white"
            axis_color = "white"
            grid_color = "white"
        else:
            hatch_color = "black"
            axis_color = "black"
            grid_color = "black"
        
        # Plot hatches
        hatch_points_count = 0
        all_hatch_points = []  # Collect all points for heatmap
        for hatch in layer['hatches']:
            if len(hatch) < 2:
                continue
            try:
            # Create tube visualization
                points = np.array([[p[0], p[1], z] for p in hatch])
                poly = pv.lines_from_points(points)
                
                # Skip invalid geometries
                if poly.n_points < 2:
                    continue
                    
                tube = poly.tube(radius=0.001)
                self.plotter.add_mesh(tube, color=path_color, name="hatches")
                hatch_points_count += len(hatch)
                all_hatch_points.extend(hatch)
            except Exception as e:
                print(f"Error creating hatch visualization: {e}")
                continue
        
        # Add heat visualization if enabled
        if self.heat_model and layer['hatches']:
            # Calculate average hatch spacing for this layer
            hatch_spacing = self._calculate_hatch_spacing(layer['hatches'])
            print(f"Layer {layer_idx}: hatch spacing = {hatch_spacing:.4f}mm")
            
            # Create precise hatch-centered heat map
            heat_mesh = self.heat_model.create_hatch_heat_map(
                layer['hatches'], 
                z,
                hatch_spacing
            )
            
            if heat_mesh is not None:
                # Determine scalar bar color based on theme
                scalar_bar_color = "white" if self.theme == "dark" else "black"
                
                # Add heat map to plotter
                self.plotter.add_mesh(
                    heat_mesh,
                    cmap="coolwarm",
                    scalars="Temperature",
                    clim=[0, self.heat_model.max_temp],
                    opacity=0.9,
                    show_scalar_bar=True,
                    scalar_bar_args={
                        'title': 'Temperature (°C)',
                        'color': scalar_bar_color,
                        'shadow': True,
                        'title_font_size': 12,
                        'label_font_size': 10
                    },
                    name="heatmap"
                )
                
                # Add hatch lines for reference
                for hatch in layer['hatches']:
                    if len(hatch) < 2:
                        continue
                    points = np.array([[p[0], p[1], z] for p in hatch])
                    poly = pv.lines_from_points(points)
                    tube = poly.tube(radius=0.001)
                    self.plotter.add_mesh(tube, color="yellow" if self.theme == "dark" else "darkred", name="hatches")

        
        # Use overall part dimensions for axes
        if self.overall_bounds:
            min_coords = self.overall_bounds['min']
            max_coords = self.overall_bounds['max']
            
            print(f"Using overall bounds: min={min_coords}, max={max_coords}")
            
            # Add axes widget with theme color
            self.plotter.add_axes(color=axis_color)
            
            # Add bounding box with theme color
            self.plotter.show_bounds(
                bounds=[
                    min_coords[0], max_coords[0],
                    min_coords[1], max_coords[1],
                    z - 0.01, z + 0.01  # Thin slice in Z direction
                ],
                grid='front',
                location='outer',
                color=grid_color,
            )
        else:
            print("No overall bounds available")
        
        # Restore user's camera position if available
        self.plotter.camera_position = current_camera_position
        self.plotter.render()
        
        print(f"Layer rendered in {time.time() - start_time:.2f} seconds")

    def _calculate_hatch_spacing(self, hatches):
        """Calculate average hatch spacing for precise heat visualization"""
        if len(hatches) < 2:
            return 0.1  # Default spacing
            
        # Collect all y-coordinates (assuming hatches are mostly horizontal)
        y_coords = []
        for hatch in hatches:
            if hatch:
                y_coords.append(hatch[0][1])
        
        if len(y_coords) < 2:
            return 0.1
            
        # Sort and calculate differences
        y_coords.sort()
        diffs = [y_coords[i] - y_coords[i-1] for i in range(1, len(y_coords))]
        
        # Return average spacing
        return sum(diffs) / len(diffs)

    def show_full_part(self):
        """Render the entire 3D part"""
        # Get theme-based path color
        path_color = self._get_path_color()
        if not self.cli_data:
            return
            
        print("Rendering full 3D part...")
        start_time = time.time()
        
        # Save current camera position
        current_camera_position = self.plotter.camera_position
        
        self.plotter.clear()

        
        # Set color based on theme
        hatch_color = "white" if self.theme == "dark" else "black"
        
        # Render each layer at its actual Z-height
        for layer in self.cli_data['layers']:
            z = layer['z']
            for hatch in layer['hatches']:
                if len(hatch) < 2:
                    continue
                points = np.array([[p[0], p[1], z] for p in hatch])
                poly = pv.lines_from_points(points)
                tube = poly.tube(radius=0.001)
                self.plotter.add_mesh(tube, color=path_color)
        
        # Add axes and bounds
        if self.overall_bounds:
            minc = self.overall_bounds['min']
            maxc = self.overall_bounds['max']
            
            # Add axes
            axis_color = "white" if self.theme == "dark" else "black"
            self.plotter.add_axes(color=axis_color)
            
            # Add bounding box
            self.plotter.show_bounds(
                bounds=[minc[0], maxc[0], minc[1], maxc[1], minc[2], maxc[2]],
                grid='back',
                location='outer',
                color=axis_color
            )
        
        # Set 3D view
        self.plotter.view_isometric()
        
        # Restore camera position
        if current_camera_position:
            self.plotter.camera_position = current_camera_position
        
        self.plotter.render()
        print(f"Full part rendered in {time.time() - start_time:.2f} seconds")
    
    def add_heat_visualization(self, path, z):
        """Add heat visualization along a path"""
        if len(path) < 2:
            return
            
        # Create sample points along the path
        points = []
        for i in range(len(path) - 1):
            start = path[i]
            end = path[i+1]
            distance = ((end[0]-start[0])**2 + (end[1]-start[1])**2)**0.5
            num_points = max(2, int(distance / 0.1))  # 0.1mm resolution
            for t in np.linspace(0, 1, num_points):
                x = start[0] + t * (end[0] - start[0])
                y = start[1] + t * (end[1] - start[1])
                points.append([x, y, z])
        
        if not points:
            return
            
        # Create heat points
        heat_points = pv.PolyData(points)
        
        # Add to plotter with red color
        self.plotter.add_mesh(
            heat_points,
            color="red",
            point_size=5,  # Scaled for small model
            opacity=0.7,
            render_points_as_spheres=True,
            name="heat_points"
        )
        print(f"Added {len(points)} heat points")
    
    def toggle_heat(self, visible):
        """Toggle heat visualization"""
        print(f"Toggling heat visualization: {visible}")
        if visible:
            from src.core.heat_model import HeatSource
            self.heat_model = HeatSource()
            if self.cli_data:
                self.plot_layer(self.current_layer)
        else:
            self.heat_model = None
            # Remove existing heat points
            self.plotter.remove_actor("heat_points")
            if self.cli_data:
                self.plot_layer(self.current_layer)