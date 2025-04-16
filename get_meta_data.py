import OpenImageIO as oiio

def get_exr_metadata(file_path):
    input_file = oiio.ImageInput.open(file_path)
    if not input_file:
        raise Exception("Could not open EXR file")

    spec = input_file.spec()
    metadata = {}

    for key in spec.extra_attribs:
        metadata[key.name] = key.value

    input_file.close()
    return metadata

# Example usage:
meta = get_exr_metadata("Tree.exr")
print(meta)
