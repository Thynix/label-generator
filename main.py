import argparse
import os
import sys

import qrcode
import yaml
from PIL import Image, PSDraw


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("yamlpath", help="Path to the description of label content")
    parser.add_argument("--show-template",
                        help="Specify to enable showing the template with label bounds",
                        action="store_true")
    args = parser.parse_args()

    labels = yaml.safe_load(open(args.yamlpath))

    with open("labels.ps", "wb") as ps_file:
        ps = PSDraw.PSDraw(ps_file)
        ps.begin_document()

        page_width, page_height = 595, 842  # A4 size in points

        # Define the PostScript fonts
        font_name = "Helvetica-Bold"
        font_size = 12
        note_font_name = "Helvetica"
        note_font_size = 10
        dpi = 72

        # Fill the page with the template
        if args.show_template:
            print("this feature is busted due to being misaligned", file=sys.stderr)
            exit(2)
            png_path = os.path.join(os.path.dirname(__file__), "Avery15660AddressLabels.png")
            with Image.open(png_path) as label_background:
                # Why is it an inch offset? Dunno
                ps.image((0, 0, page_width, page_height), label_background, dpi)

        label_height = 1
        label_width = 2 + 5 / 8
        horizontal_edge_padding = 1 / 8  # space to the left before label text starts
        vertical_edge_padding = 1 / 8  # space to the top before label text starts

        horizontal_label_spacing = 1 / 8  # horizontal space between labels; vertical is flush

        # space from the edge of the page to the start of the label
        horizontal_label_offset = 1 / 5
        vertical_label_offset = 1 / 2

        # 3 columns of 10 labels
        i = 0
        for column_index in range(3):
            for row_index in range(10):
                if not labels:
                    break

                label = labels.pop()
                i += 1

                if not ("brand" in label and "color" in label):
                    print(f"label {i} is missing brand and/or color. Its fields are: {label}", file=sys.stderr)
                    exit(1)

                # orizontal_label_offset, page_width - horizontal_label_offset, int(dpi * (label_width + horizontal_label_padding))
                # vertical_label_offset, page_height - vertical_label_offset, int(dpi * label_height)
                # Height in PostScript starts at the bottom of the page
                y = int((vertical_label_offset + label_height * (row_index + 1) - vertical_edge_padding) * dpi)
                x = int((horizontal_label_offset + (label_width + horizontal_label_spacing) * column_index + horizontal_edge_padding) * dpi)

                print(x, y, label["color"])

                ps.setfont(font_name, font_size)
                ps.text((x, y), label["brand"])
                ps.text((x, y - font_size), label["color"])
                if "color2" in label:
                    ps.text((x, y - font_size * 2), label["color2"])
                if "color3" in label:
                    ps.text((x, y - font_size * 3), label["color3"])

                ps.setfont(note_font_name, note_font_size)
                if "note" in label:
                    ps.text((x, y - font_size * 2), label["note"])
                if "note2" in label:
                    ps.text((x, y - font_size * 3), label["note2"])

                height_offset = 18  # I don't yet know where this comes from
                width_offset = 5
                if "url" in label:
                    ps.image((
                        x + int(dpi * label_width / 2) - width_offset, y - int(dpi * label_height) + height_offset,
                        # TODO: where does 14 come from?
                        x + int(dpi * label_width) - width_offset, y + int(dpi * label_height / 14) + height_offset,
                    ),
                        qrcode.make(label["url"]).get_image().convert("RGB"))
                # else:
                # TODO: maybe big X or "discontinued" if not specified

        ps.end_document()
        Image.open("labels.png").save(ps)

    if len(labels):
        print(f"{len(labels)} remaining labels not included")


main()
