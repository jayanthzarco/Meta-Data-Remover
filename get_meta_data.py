import OpenEXR
import Imath
import os
import sys
import argparse


def get_all_exr_metadata(exr_path):
    """Extract all available metadata from an EXR file and return as key-value pairs."""
    try:
        # Open the EXR file
        exr_file = OpenEXR.InputFile(exr_path)

        # Get the header, which contains the metadata
        header = exr_file.header()

        # Initialize metadata dictionary
        metadata = {}

        # Extract ALL header attributes
        for key in header.keys():
            try:
                metadata[key] = header[key]
            except:
                # Some complex types may need special handling
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


def process_exr_sequence(input_path, output_file=None):
    """Process all EXR images in a directory and output metadata as key=value pairs."""
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

    # Sort to ensure proper sequence order (numerical sort if possible)
    exr_files.sort(key=lambda x: int(''.join(filter(str.isdigit, x))) if any(c.isdigit() for c in x) else x)

    # Open output file if specified
    out_file = None
    if output_file:
        out_file = open(output_file, 'w')

    # Process each image
    for i, exr_file in enumerate(exr_files):
        full_path = os.path.join(input_path, exr_file)
        metadata = get_all_exr_metadata(full_path)

        # Output header for this file
        header_line = f"=== Image {i}: {exr_file} ==="
        if out_file:
            out_file.write(header_line + '\n')
        else:
            print(header_line)

        # Output metadata as key=value pairs
        for key, value in metadata.items():
            line = f"{key}={value}"
            if out_file:
                out_file.write(line + '\n')
            else:
                print(line)

        # Add a blank line between images
        if out_file:
            out_file.write('\n')
        else:
            print()

    # Close output file if opened
    if out_file:
        out_file.close()
        print(f"Metadata written to {output_file}")


def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Extract metadata from EXR image sequence')
    parser.add_argument('--path', '-p', required=True, help='Path to the folder containing EXR image sequence')
    parser.add_argument('--output', '-o', help='Output file path (optional)')

    # Parse arguments
    args = parser.parse_args()

    # Process the sequence
    process_exr_sequence(args.path, args.output)


if __name__ == "__main__":
    main()