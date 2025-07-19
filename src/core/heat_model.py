# =====================
# heat_model.py
# =====================
import numpy as np
import pyvista as pv

class HeatSource:
    def __init__(self, max_temp=1000, sigma=0.2, spot_size=0.5):
        self.max_temp = max_temp
        self.sigma = sigma
        self.spot_size = spot_size  # Size of the moving heat spot
        
    def create_moving_spot(self, position, z, theme="dark"):
        """Create a moving heat spot at given position"""
        x0, y0 = position
        # Create a small grid around the current position
        grid_size = 20
        xi = np.linspace(x0 - self.spot_size, x0 + self.spot_size, grid_size)
        yi = np.linspace(y0 - self.spot_size, y0 + self.spot_size, grid_size)
        xx, yy = np.meshgrid(xi, yi)
        zz = np.full(xx.shape, z)
        
        # Calculate temperature distribution
        dist = np.sqrt((xx - x0)**2 + (yy - y0)**2)
        temp_grid = self.max_temp * np.exp(-dist**2 / (2 * self.sigma**2))

        # Use theme-based colormap
        cmap = "coolwarm" if theme == "dark" else "hot"
        
        # Create structured grid
        grid = pv.StructuredGrid(xx, yy, zz)
        grid["Temperature"] = temp_grid.flatten(order="F")
        return grid, cmap

    def create_hatch_heat_map(self, hatches, z, hatch_spacing):
        """Create a heat map visualization for hatches"""
        # Create a grid that covers the hatch area
        all_points = [point for hatch in hatches for point in hatch]
        if not all_points:
            return None
            
        xs = [p[0] for p in all_points]
        ys = [p[1] for p in all_points]
        
        # Create grid with resolution based on hatch spacing
        resolution = max(0.05, hatch_spacing / 5)  # Higher resolution than hatch spacing
        xi = np.arange(min(xs) - self.spot_size, max(xs) + self.spot_size, resolution)
        yi = np.arange(min(ys) - self.spot_size, max(ys) + self.spot_size, resolution)
        xx, yy = np.meshgrid(xi, yi)
        zz = np.full(xx.shape, z)
        
        # Initialize temperature grid
        temp_grid = np.zeros_like(xx)
        
        # Add temperature contribution from each hatch point
        for hatch in hatches:
            for point in hatch:
                x0, y0 = point
                dist = np.sqrt((xx - x0)**2 + (yy - y0)**2)
                temp_contribution = self.max_temp * np.exp(-dist**2 / (2 * self.sigma**2))
                temp_grid = np.maximum(temp_grid, temp_contribution)
        
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