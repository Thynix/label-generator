import argparse
import io
import pickle

import yaml
import pdfme
import qrcode

# These constants are in inches
label_height = 1
label_width = 2 + 5 / 8
horizontal_edge_padding = 1 / 8  # space to the left before label text starts
vertical_edge_padding = 1 / 8  # space to the top before label text starts

horizontal_label_spacing = 1 / 8  # horizontal space between labels; vertical is flush

# space from the edge of the page to the start of the label
horizontal_label_offset = 1 / 5
vertical_label_offset = 1 / 2

points_per_inch = 72
dpi = 72

parser = argparse.ArgumentParser()
parser.add_argument("yamlpath", help="Path to the description of label content")
args = parser.parse_args()

labels = yaml.safe_load(open(args.yamlpath))

content = list()
for label in labels:
    label_content = {
        #"width": label_width * points_per_inch,
        #"height": label_height * points_per_inch,
        #"width": 10, "height": 10,  # smaller content size doesn't modify image size
        "content": [
            label["brand"],
            label["color"],
        ],
    }

    if "url" in label:
        image_buffer = io.BytesIO()
        (
            qrcode.make(label["url"]).get_image().convert("RGB")
            #.resize((10, 10))  # make the image blurry, but not smaller, so it's not sized on DPI
            .save(image_buffer, format="jpeg", quality=100)
         )

        # Seek image buffer to the start so the image can be read.
        image_buffer.seek(0)

        label_content["content"].append({
            # no difference with width/height specified
            #"width": label_height * points_per_inch,
            #"height": label_height * points_per_inch,
            #"width": 10, "height": 10,
            #"style": {
            #    "image_place": "normal",
            #},
            "image": image_buffer,
            "image_name": label["url"],
            "extension": "jpeg",
        })

    content.append(label_content)

document = {
    "style": {
        "margin_bottom": vertical_edge_padding * points_per_inch,
        "margin_top": vertical_edge_padding * points_per_inch,
        "margin_left": horizontal_edge_padding * points_per_inch,
        "margin_right": horizontal_edge_padding * points_per_inch,
        "page_size": "letter",
        "line_height": 1,
    },
    "sections": [
        {
            "cols": {
                "count": 3,
                "gap": horizontal_label_spacing * 2 * points_per_inch,
            },
            "content": content,
        },
    ]
}

with open('document.pdf', 'wb') as f:
    pdfme.build_pdf(document, f)