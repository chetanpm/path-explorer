def parse_cli(file_path: str) -> dict:
    """Robust parser for .cli files with the specific format"""
    layers = []
    units = 0.001  # Default unit conversion (micrometers to mm)
    minZ = maxZ = 0.0
    total_layers_header = 0  # Renamed for clarity
    layer_height = 0.0
    
    print(f"Parsing CLI file: {file_path}")
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    lines = content.splitlines()
    header_end_index = None
        
    # Find header end
    for i, line in enumerate(lines):
        if line.strip() == "$$HEADEREND":
            header_end_index = i
            break
            
    if header_end_index is None:
        raise ValueError("Header end not found")
    
    # Parse header information
    for i in range(header_end_index + 1):
        line = lines[i].strip()
        if line.startswith("$$UNITS/"):
            units = float(line.split('/')[1])
        elif line.startswith("$$DIMENSION/"):
            dim_data = line.split('/')[1].split(',')
            minZ = float(dim_data[2]) * units
            maxZ = float(dim_data[5]) * units
        elif line.startswith("$$LAYERS/"):
            total_layers_header = int(line.split('/')[1])  # Store header value
    
    # Parse geometry section
    current_layer = None

    for i in range(header_end_index + 1, len(lines)):
        line = lines[i].strip()
        if not line:
            continue
            
        # Start of a new layer
        if line.startswith('$$LAYER/'):
            # Save previous layer if exists
            if current_layer is not None:
                layers.append(current_layer)
                
            try:
                layer_num = int(line.split('/')[1])
                # Calculate layer height based on header dimension
                if total_layers_header > 1:
                    layer_height = (maxZ - minZ) / (total_layers_header - 1)
                else:
                    layer_height = 0
                    
                z = minZ + layer_num * layer_height
                current_layer = {
                    'layer_number': layer_num,  # Original layer number
                    'z': z,
                    'hatches': [],
                    'contours': []
                }
                print(f"Found layer {layer_num} at z={z:.4f}mm")
            except Exception as e:
                print(f"Error parsing layer: {line} - {str(e)}")
                current_layer = None
                
        # Hatch data
        elif line.startswith('$$HATCHES/') and current_layer is not None:
            try:
                data = line[len('$$HATCHES/'):].split(',')
                point_count = int(data[1])
                coords = [float(x) * units for x in data[2:2 + point_count * 2]]
                
                # Convert to point pairs
                points = []
                for j in range(0, len(coords), 2):
                    points.append((coords[j], coords[j+1]))
                
                current_layer['hatches'].append(points)
            except Exception as e:
                print(f"Error parsing hatch: {line} - {str(e)}")
    
    # Add the last layer if exists
    if current_layer is not None:
        layers.append(current_layer)
    
    # Count actual layers
    actual_layers = len(layers)
    
    # Print summary statistics
    hatch_count = sum(len(layer['hatches']) for layer in layers)
    
    print(f"Header specified {total_layers_header} layers")
    print(f"Found {actual_layers} layers in the geometry section")
    print(f"Total hatches: {hatch_count}")
    
    return {
        'layers': layers,
        'total_layers_header': total_layers_header,
        'actual_layers': actual_layers
    }