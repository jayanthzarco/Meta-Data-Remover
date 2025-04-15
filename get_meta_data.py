import OpenEXR
import Imath
import os
import json

# Input path to EXR sequence directory
input_path = "/path/to/your/exr/sequence"  # CHANGE THIS TO YOUR PATH
output_file = "exr_metadata.json"  # Output JSON file name


def json_serializable(obj):
    """Convert non-serializable objects to serializable format for JSON."""
    if isinstance(obj, bytes):
        return obj.decode('utf-8', errors='replace')
    elif isinstance(obj, (Imath.Box2i, Imath.V2f)):
        return str(obj)
    elif hasattr(obj, '__dict__'):
        return obj.__dict__
    else:
        return str(obj)


def get_all_exr_metadata(exr_path):
    """Extract all available metadata from an EXR file."""
    try:
        # Open the EXR file
        exr_file = OpenEXR.InputFile(exr_path)

        # Get the header, which contains the metadata
        header = exr_file.header()

        # Initialize metadata dictionary
        metadata = {}

        # Extract header attributes
        for key in header.keys():
            try:
                value = header[key]
                # Process the value to ensure it's JSON serializable
                if isinstance(value, bytes):
                    metadata[key] = value.decode('utf-8', errors='replace')
                elif isinstance(value, (Imath.Box2i, Imath.V2f)):
                    metadata[key] = str(value)
                elif hasattr(value, '__dict__'):
                    metadata[key] = value.__dict__
                else:
                    try:
                        # Test if value is JSON serializable
                        json.dumps(value)
                        metadata[key] = value
                    except:
                        metadata[key] = str(value)
            except:
                metadata[key] = str(header[key])

        # Get image dimensions
        dw = header['dataWindow']
        width = dw.max.x - dw.min.x + 1
        height = dw.max.y - dw.min.y + 1
        metadata['width'] = width
        metadata['height'] = height

        # Get channel information
        channels = header['channels']
        channel_info = {}
        for c in channels:
            channel_info[c] = {
                'pixel_type': channels[c].type.v,
                'x_sampling': channels[c].xSampling,
                'y_sampling': channels[c].ySampling
            }
        metadata['channel_details'] = channel_info

        # Close the file
        exr_file.close()
        return metadata

    except Exception as e:
        return {"Error": f"Failed to process {exr_path}: {str(e)}"}


def process_exr_sequence(input_path, output_file):
    """Process all EXR images in a directory and output metadata as JSON."""
    # Check if path exists
    if not os.path.exists(input_path):
        print(f"Error: Path '{input_path}' does not exist")
        return

    # Get all EXR files in directory
    exr_files = [f for f in os.listdir(input_path)
                 if os.path.isfile(os.path.join(input_path, f))
                 and f.lower().endswith('.exr')]

    if not exr_files:
        print(f"No EXR files found in {input_path}")
        return

    # Sort to ensure proper sequence order
    exr_files.sort(key=lambda x: int(''.join(filter(str.isdigit, x))) if any(c.isdigit() for c in x) else x)

    # Dictionary to hold all metadata
    all_metadata = {}

    # Process each image
    for i, exr_file in enumerate(exr_files):
        full_path = os.path.join(input_path, exr_file)
        metadata = get_all_exr_metadata(full_path)
        all_metadata[exr_file] = metadata

    # Custom JSON encoder to handle non-serializable objects
    class CustomJSONEncoder(json.JSONEncoder):
        def default(self, obj):
            return json_serializable(obj)

    # Write JSON to file using the custom encoder
    with open(output_file, 'w') as f:
        json.dump(all_metadata, f, indent=4, cls=CustomJSONEncoder)

    print(f"Metadata written to {output_file}")


# Run the function with the specified path
process_exr_sequence(input_path, output_file)