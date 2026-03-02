# PDF Thumbnail Generation Tool

## Overview
This tool generates thumbnail images from PDF files, allowing users to preview PDF content without opening the entire document. It extracts the first page of a PDF and converts it into a high-quality image format.

## Features
- Generate thumbnails for PDF files in various image formats (JPEG, PNG)
- Adjustable image quality and size
- Batch processing for multiple PDF files

## Installation
To use this tool, clone the repository and install the necessary dependencies. You can do this by running:

```bash
git clone https://github.com/ARYANjoshi09/pdf-thumbnail.git
cd pdf-thumbnail
pip install -r requirements.txt
```

## Usage
The tool can be run via the command line or through a user interface. Here’s how to use it via the command line:

```bash
python generate_thumbnail.py <path_to_pdf> <output_image_path> --format <image_format> --quality <image_quality>
```

### Parameters:
- `<path_to_pdf>`: Path to the PDF file to generate the thumbnail from.
- `<output_image_path>`: Where to save the generated thumbnail image.
- `--format`: The format of the output image (jpeg or png, default is png).
- `--quality`: The quality of the output image (1-100, higher is better; default is 75).

## Example
```bash
python generate_thumbnail.py example.pdf example_thumbnail.png --format png --quality 90
```

## Contributing
Contributions are welcome! If you have suggestions or improvements, please submit a pull request or open an issue.

## License
This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments
- This project makes use of several libraries, including PyPDF2 and Pillow, for PDF handling and image processing.
- Special thanks to the open-source community for their contributions!
