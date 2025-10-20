# XML to SVG Converter

A Python script that converts XML cut files to SVG format, preserving all dimensions and locations. This tool is designed for processing CNC cutting files or similar XML-based design files.

## Features

- **Batch Processing**: Convert all XML files in a folder at once
- **Unit Conversion**: Automatically detects and converts between different units (hundredths of millimeters, inches)
- **Coordinate System Correction**: Flips Y-axis coordinates for proper SVG rendering
- **Registration Marks**: Converts registration marks to 3x3mm black squares
- **Cut Paths**: Converts cut paths including points and splines to SVG paths
- **Flexible Output**: Save SVG files to the same folder or a specified output directory

## Requirements

- Python 3.6 or higher
- No external dependencies required (uses only standard library modules)

## Installation

1. Clone or download the script to your local machine
2. Ensure you have Python 3.6+ installed
3. No additional installation steps required

## Usage

### Basic Syntax

```bash
python xml_to_svg_converter.py <input_folder> [options]
```

### Command Line Options

| Argument | Description |
|----------|-------------|
| `input_folder` | Path to the folder containing XML files to convert (required) |
| `-o, --output_folder` | Path for the destination folder to save SVG files (optional) |

### Examples

#### Convert all XML files in a folder (output to same folder)

```bash
python xml_to_svg_converter.py ./input_folder
```

This will convert all `.xml` files in `input_folder` and save the corresponding `.svg` files in the same location.

#### Convert all XML files in a folder (output to different folder)

```bash
python xml_to_svg_converter.py ./input_folder -o ./output_folder
```

This will convert all `.xml` files in `input_folder` and save the `.svg` files in `output_folder`.

#### Process files in current directory

```bash
python xml_to_svg_converter.py .
```

## Input File Format

The script expects XML files with the following structure:

```xml
<cut-list units="hundredths_mm" width="1000" height="800">
    <reg-mark x="100" y="100"/>
    <cut-path>
        <point x="200" y="200"/>
        <point x="300" y="250"/>
        <spline x1="400" y1="300" x2="500" y2="350" x3="600" y3="400"/>
    </cut-path>
</cut-list>
```

### Supported Elements

- **cut-list**: Root element with overall dimensions and units
  - `units`: Either "hundredths_mm" or "inches"
  - `width`: Overall width of the design
  - `height`: Overall height of the design

- **reg-mark**: Registration marks (converted to 3x3mm black squares)
  - `x`: X-coordinate of the mark center
  - `y`: Y-coordinate of the mark center

- **cut-path**: Cutting paths (converted to SVG paths)
  - `point`: Straight line segments
    - `x`: X-coordinate of the point
    - `y`: Y-coordinate of the point
  - `spline`: Cubic Bezier curves
    - `x1`, `y1`: First control point
    - `x2`, `y2`: Second control point
    - `x3`, `y3`: End point

## Output Format

The script generates SVG files with the following characteristics:

- **Canvas Size**: Matches the original dimensions from the XML file
- **Coordinate System**: Top-left origin (Y-axis flipped from typical bottom-left)
- **Colors**:
  - Background: White with gray border
  - Registration marks: Black squares (3x3mm)
  - Cut paths: Red lines (0.1mm stroke width)
- **Paths**: Closed shapes with no fill

## Unit Conversion

The script automatically handles different units:

- **hundredths_mm**: Converts from 1/100mm to millimeters (scale factor: 0.01)
- **inches**: Converts from inches to millimeters (scale factor: 25.4)
- **Unknown units**: Assumes 1:1 mapping to millimeters (with warning)

## Error Handling

The script includes comprehensive error handling for:

- **Invalid folder paths**: Checks if input folder exists
- **Missing files**: Handles cases where no XML files are found
- **Malformed XML**: Reports XML parsing errors
- **Invalid coordinates**: Skips elements with invalid coordinates and continues processing
- **File I/O errors**: Reports issues writing output files

## Limitations

- **No recursion**: Only processes files in the specified folder, not subfolders
- **XML structure dependent**: Requires specific XML structure as described above
- **Memory usage**: Loads entire files into memory (may be unsuitable for very large files)

## Troubleshooting

### Common Issues

1. **"Input folder does not exist"**
   - Verify the folder path is correct
   - Use absolute paths if relative paths cause issues

2. **"No XML files found"**
   - Check that files in the folder have `.xml` extension
   - Ensure files are not hidden or system files

3. **"Could not parse XML file"**
   - Verify XML is well-formed
   - Check for encoding issues (script expects UTF-8)

4. **Incorrect scaling**
   - Verify the `units` attribute in your XML files
   - Check that width/height values are numeric

## Contributing

To modify or extend the script:

1. The main conversion logic is in the `convert_xml_to_svg()` function
2. Command-line argument parsing is handled in the `main()` function
3. Unit conversion factors can be modified in the scaling section

## License

This script is provided as-is for educational and commercial use.

## Version History

- **v1.0**: Initial release with single file conversion
- **v1.1**: Added batch folder processing functionality