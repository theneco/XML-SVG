import xml.etree.ElementTree as ET
import argparse
import sys
import os

def convert_xml_to_svg(xml_file, svg_file):
    """
    Parses an XML cut file and converts its contents into an SVG file,
    rotating the drawing 90 degrees clockwise and centering it on the canvas.

    Args:
        xml_file (str): The path to the input XML file.
        svg_file (str): The path for the output SVG file.
    """
    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()
    except ET.ParseError as e:
        print(f"Error: Could not parse XML file. Details: {e}", file=sys.stderr)
        sys.exit(1)
    except FileNotFoundError:
        print(f"Error: Input file not found at '{xml_file}'", file=sys.stderr)
        sys.exit(1)

    # Determine the scaling factor
    units = root.get('units')
    if units == 'hundredths_mm':
        scale_factor = 0.01
    elif units == 'inches':
        scale_factor = 25.4
    else:
        print(f"Warning: Unrecognized XML units '{units}'. Assuming 1:1 scale.", file=sys.stderr)
        scale_factor = 1.0

    # Get the overall canvas dimensions
    try:
        width_mm = float(root.get('width')) * scale_factor
        height_mm = float(root.get('height')) * scale_factor
    except (TypeError, ValueError):
        print("Error: Could not read 'width' or 'height' attributes.", file=sys.stderr)
        sys.exit(1)

    # --- CENTERING CHANGE: First, pre-scan all points to find the drawing's bounding box ---
    all_x_coords, all_y_coords = [], []
    reg_mark_size_mm = 3.0

    # Include registration marks in the bounding box
    for mark in root.findall('reg-mark'):
        try:
            center_x = float(mark.get('x')) * scale_factor
            center_y = height_mm - (float(mark.get('y')) * scale_factor)
            all_x_coords.extend([center_x - reg_mark_size_mm / 2, center_x + reg_mark_size_mm / 2])
            all_y_coords.extend([center_y - reg_mark_size_mm / 2, center_y + reg_mark_size_mm / 2])
        except (TypeError, ValueError):
            continue

    # Include all path points in the bounding box
    for path in root.findall('cut-path'):
        for element in path:
            try:
                if element.tag == 'point':
                    x = float(element.get('x')) * scale_factor
                    y = height_mm - (float(element.get('y')) * scale_factor)
                    all_x_coords.append(x)
                    all_y_coords.append(y)
                elif element.tag == 'spline':
                    # Including control points gives a good approximation of the curve's extents
                    for key in ['x1', 'x2', 'x3']:
                        all_x_coords.append(float(element.get(key)) * scale_factor)
                    for key in ['y1', 'y2', 'y3']:
                        all_y_coords.append(height_mm - (float(element.get(key)) * scale_factor))
            except (TypeError, ValueError):
                continue

    # Calculate the drawing's center
    if not all_x_coords or not all_y_coords:
        print("Warning: No valid drawing elements found.", file=sys.stderr)
        drawing_center_x, drawing_center_y = width_mm / 2, height_mm / 2
    else:
        drawing_center_x = (min(all_x_coords) + max(all_x_coords)) / 2
        drawing_center_y = (min(all_y_coords) + max(all_y_coords)) / 2

    # --- CENTERING CHANGE: Create the multi-step transform string ---
    canvas_center_x = width_mm / 2
    canvas_center_y = height_mm / 2
    
    # SVG transforms are applied right-to-left:
    # 1. Translate drawing's center to the origin (0,0).
    # 2. Rotate 90 degrees around the origin.
    # 3. Translate the rotated drawing to the canvas's center.
    transform_str = (
        f'translate({canvas_center_x:.4f}, {canvas_center_y:.4f}) '
        f'rotate(90) '
        f'translate({-drawing_center_x:.4f}, {-drawing_center_y:.4f})'
    )

    # --- SVG Generation Pass ---
    svg_elements = [
        f'<svg width="{width_mm}mm" height="{height_mm}mm" viewBox="0 0 {width_mm} {height_mm}" xmlns="http://www.w3.org/2000/svg">',
        '',
        f'<g transform="{transform_str}">', # Apply the calculated transform
    ]

    # Process and draw registration marks (coordinates are relative to the transform)
    for mark in root.findall('reg-mark'):
        try:
            center_x = float(mark.get('x')) * scale_factor
            center_y = height_mm - (float(mark.get('y')) * scale_factor)
            top_left_x = center_x - (reg_mark_size_mm / 2)
            top_left_y = center_y - (reg_mark_size_mm / 2)
            svg_elements.append(f'<rect x="{top_left_x:.4f}" y="{top_left_y:.4f}" width="{reg_mark_size_mm}" height="{reg_mark_size_mm}" fill="black"/>')
        except (TypeError, ValueError):
            print(f"Warning: Skipping a registration mark with invalid coordinates.", file=sys.stderr)

    # Process and draw each cut path (coordinates are relative to the transform)
    for i, path in enumerate(root.findall('cut-path')):
        path_data = []
        is_first = True
        for element in path:
            try:
                if element.tag == 'point':
                    x = float(element.get('x')) * scale_factor
                    y = height_mm - (float(element.get('y')) * scale_factor)
                    command = "M" if is_first else "L"
                    path_data.append(f"{command} {x:.4f} {y:.4f}")
                    is_first = False
                elif element.tag == 'spline':
                    x1 = float(element.get('x1')) * scale_factor
                    y1 = height_mm - (float(element.get('y1')) * scale_factor)
                    x2 = float(element.get('x2')) * scale_factor
                    y2 = height_mm - (float(element.get('y2')) * scale_factor)
                    x3 = float(element.get('x3')) * scale_factor
                    y3 = height_mm - (float(element.get('y3')) * scale_factor)
                    path_data.append(f"C {x1:.4f} {y1:.4f}, {x2:.4f} {y2:.4f}, {x3:.4f} {y3:.4f}")
            except (TypeError, ValueError):
                print(f"Warning: Skipping an element in path {i+1} due to invalid coordinates.", file=sys.stderr)

        if path_data:
            path_data.append("Z")
            path_string = " ".join(path_data)
            svg_elements.append(f'<path d="{path_string}" fill="none" stroke="magenta" stroke-width="0.1mm"/>')
    
    svg_elements.extend(['</g>', '</svg>'])

    # Write the result to the output file
    try:
        with open(svg_file, 'w') as f:
            f.write('\n'.join(svg_elements))
        print(f"Successfully converted '{xml_file}' to '{svg_file}'")
    except IOError as e:
        print(f"Error: Could not write to output file '{svg_file}'. Details: {e}", file=sys.stderr)
        sys.exit(1)

def main():
    """Main function to handle command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Convert XML cut files to SVG, rotating and centering the output.",
        epilog="Example: python xml_to_svg_converter.py ./input_folder -o ./output_folder"
    )
    parser.add_argument("input_folder", help="The path to the folder containing XML files.")
    parser.add_argument("-o", "--output_folder", help="The destination folder for SVG files. Defaults to the input folder.")
    args = parser.parse_args()

    input_folder = args.input_folder
    output_folder = args.output_folder if args.output_folder else input_folder

    if not os.path.isdir(input_folder):
        print(f"Error: Input folder '{input_folder}' does not exist.", file=sys.stderr)
        sys.exit(1)
    
    os.makedirs(output_folder, exist_ok=True)

    xml_files = [f for f in os.listdir(input_folder) if f.endswith('.xml')]
    if not xml_files:
        print(f"Warning: No XML files found in '{input_folder}'.", file=sys.stderr)
        sys.exit(0)

    for xml_file in xml_files:
        input_path = os.path.join(input_folder, xml_file)
        output_path = os.path.join(output_folder, os.path.splitext(xml_file)[0] + '.svg')
        print(f"Converting '{input_path}' to '{output_path}'...")
        convert_xml_to_svg(input_path, output_path)

if __name__ == '__main__':
    main()