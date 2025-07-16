# =====================
# heat_model.py
# =====================
import numpy as np
import pyvista as pv

class HeatSource:
    """Precise heat source model following hatch lines"""
    def __init__(self, max_temp=1000, sigma=0.2):
        """
        Initialize heat source parameters
        :param max_temp: Maximum temperature at center (°C)
        :param sigma: Spread of the Gaussian distribution perpendicular to hatches (mm)
        """
        self.max_temp = max_temp
        self.sigma = sigma
    
    def create_hatch_heat_map(self, hatches, z, hatch_spacing=0.1):
        """
        Create a heat map that precisely follows hatch lines
        :param hatches: List of hatches (each hatch is list of points)
        :param z: Z-height of the layer
        :param hatch_spacing: Average distance between hatches (mm)
        :return: PyVista mesh with temperature values
        """
        if not hatches:
            return None
            
        # Collect all hatch points
        all_points = []
        for hatch in hatches:
            if len(hatch) >= 2:
                all_points.extend(hatch)
        
        if not all_points:
            return None
            
        # Calculate bounds from points
        points_arr = np.array(all_points)
        x_min, y_min = np.min(points_arr, axis=0)
        x_max, y_max = np.max(points_arr, axis=0)
        
        # Create grid focused on the hatch area
        grid_size = 200  # Higher resolution for detailed view
        xi = np.linspace(x_min, x_max, grid_size)
        yi = np.linspace(y_min, y_max, grid_size)
        xx, yy = np.meshgrid(xi, yi)
        zz = np.full(xx.shape, z)
        
        # Initialize temperature grid
        temp_grid = np.zeros_like(xx)
        
        # Calculate temperature based on distance to nearest hatch
        for i in range(grid_size):
            for j in range(grid_size):
                x = xx[i, j]
                y = yy[i, j]
                min_dist = float('inf')
                
                # Find minimum distance to any hatch segment
                for hatch in hatches:
                    if len(hatch) < 2:
                        continue
                        
                    # Find distance to this hatch polyline
                    for k in range(len(hatch) - 1):
                        p1 = hatch[k]
                        p2 = hatch[k+1]
                        dist = self._distance_to_segment(x, y, p1, p2)
                        if dist < min_dist:
                            min_dist = dist
                
                # Apply Gaussian distribution perpendicular to hatches
                if min_dist < 3 * self.sigma:  # Only calculate within 3 sigma
                    temp_grid[i, j] = self.max_temp * np.exp(-min_dist**2 / (2 * self.sigma**2))
        
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