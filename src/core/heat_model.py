import numpy as np
import pyvista as pv

class HeatSource:
    def __init__(self, max_temp=1000, sigma=0.2, spot_size=0.5, base_temp=200, thermal_diffusivity=1e-5, grid_size=20):
        self.max_temp = max_temp
        self.sigma = sigma
        self.spot_size = spot_size
        self.base_temp = base_temp  # Preheat temperature
        self.thermal_diffusivity = thermal_diffusivity  # Material property
        self.time_step = 0.05  # Time between heat spot update
        self.grid_size = grid_size  # Add grid_size parameter
        self.decay_factor = 0.7  # Heat decay factor between layers
        
    def create_moving_spot(self, position, z, prev_temps=None, time_elapsed=0, theme="dark"):
        """Create a moving heat spot at given position"""
        x0, y0 = position
        # Create a small grid around the current position
        grid_size = self.grid_size
        xi = np.linspace(x0 - self.spot_size, x0 + self.spot_size, grid_size)
        yi = np.linspace(y0 - self.spot_size, y0 + self.spot_size, grid_size)
        xx, yy = np.meshgrid(xi, yi)
        zz = np.full(xx.shape, z)

        # Initialize temperature grid with residual heat from previous layers
        temp_grid = np.full(xx.shape, self.base_temp)
        if prev_temps is not None:
            # Apply decay to previous temperatures
            residual = (prev_temps - self.base_temp) * self.decay_factor
            temp_grid = np.maximum(temp_grid, residual + self.base_temp)
        
        # Calculate temperature distribution
        dist = np.sqrt((xx - x0)**2 + (yy - y0)**2)
        new_heat = self.max_temp * np.exp(-dist**2 / (2 * self.sigma**2))
        temp_grid = np.maximum(temp_grid, new_heat)

        # Apply thermal diffusion if previous temperatures exist
        if prev_temps is not None:
            # Simple diffusion model (would be more complex in real implementation)
            diffused = prev_temps * np.exp(-self.thermal_diffusivity * time_elapsed)
            temp_grid = np.maximum(temp_grid, diffused)
        
        # Create structured grid
        grid = pv.StructuredGrid(xx, yy, zz)
        grid["Temperature"] = temp_grid.flatten(order="F")
        
        # Use theme-based colormap
        cmap = "coolwarm" if theme == "dark" else "hot"
        return grid, cmap, temp_grid

    # Residual heat handling
    def apply_residual_heat(self, base_temp, prev_temps, decay_factor=0.7):
        """Apply residual heat from previous layers"""
        if prev_temps is None:
            return base_temp
            
        # Apply decay to previous temperatures
        residual = (prev_temps - base_temp) * decay_factor
        return np.maximum(base_temp, residual + base_temp)

    
    def create_hatch_heat_map(self, hatches, z, hatch_spacing, overall_bounds):
        """Create heat map visualization for hatches using entire part bounds"""
        if not hatches or not overall_bounds:
            return None
            
        minx, miny, _ = overall_bounds['min']
        maxx, maxy, _ = overall_bounds['max']
        
        # Create grid covering entire part with fixed resolution
        resolution = 0.1  # Fixed resolution for consistent visualization
        xi = np.arange(minx, maxx, resolution)
        yi = np.arange(miny, maxy, resolution)
        xx, yy = np.meshgrid(xi, yi)
        zz = np.full(xx.shape, z)
        
        # Initialize temperature grid with base temperature
        base_temp = 100
        temp_grid = np.full(xx.shape, base_temp)
        
        # Add temperature contribution from each hatch point
        for hatch in hatches:
            for point in hatch:
                x0, y0 = point
                dist = np.sqrt((xx - x0)**2 + (yy - y0)**2)
                temp_contribution = self.max_temp * np.exp(-dist**2 / (2 * self.sigma**2))
                temp_grid = np.maximum(temp_grid, base_temp + temp_contribution)
        
        # Create structured grid
        grid = pv.StructuredGrid(xx, yy, zz)
        grid["Temperature"] = temp_grid.flatten(order="F")
        return grid
    
    def _distance_to_segment(self, x, y, p1, p2):
        """Calculate distance from point (x,y) to line segment (p1-p2)"""
        # Vector from p1 to p2
        vx = p2[0] - p1[0]
        vy = p2[1] - p1[1]
        
        # Vector from p1 to point
        wx = x - p1[0]
        wy = y - p1[1]
        
        # Calculate dot product
        c1 = wx * vx + wy * vy
        if c1 <= 0:
            # Closest to p1
            return np.sqrt(wx**2 + wy**2)
            
        c2 = vx * vx + vy * vy
        if c2 <= c1:
            # Closest to p2
            return np.sqrt((x - p2[0])**2 + (y - p2[1])**2)
            
        # Closest to a point along the segment
        b = c1 / c2
        pbx = p1[0] + b * vx
        pby = p1[1] + b * vy
        return np.sqrt((x - pbx)**2 + (y - pby)**2)