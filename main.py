import argparse
import subprocess
import sys

import qrcode
import yaml
from PIL import PSDraw


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("yamlpath", help="Path to the description of label content")
    parser.add_argument("--draw_edges",
                        help="If specified, draw alignment lines near the edges of the page.",
                        action="store_true")
    parser.add_argument("--skip_count",
                        help="Skip labels at the beginning of the page. For if a previous print left some over.",
                        default=0, type=int)
    args = parser.parse_args()

    labels = yaml.safe_load(open(args.yamlpath))
    if len(labels) > 30:
        print(f"Error: too many labels. Found {len(labels)}, but a page only fits 30.")
        exit(1)

    page_width, page_height = 612, 792  # letter size in points
    # page_width, page_height = 595, 842  # A4 size in points

    with open("labels.ps", "wb") as ps_file:
        ps = PSDraw.PSDraw(ps_file)
        ps.begin_document()

        # Define the PostScript fonts
        font_name = "Helvetica-Bold"
        font_size = 12
        note_font_name = "Helvetica"
        note_font_size = 10
        dpi = 72

        # Label page layout measurements in inches
        label_height = 1
        label_width = 2 + 5 / 8
        horizontal_edge_padding = 1 / 8  # space to the left before label text starts
        vertical_edge_padding = 1 / 16  # space to the top before label text starts

        horizontal_label_spacing = 1 / 8  # horizontal space between labels; vertical is flush

        # space from the edge of the page to the start of the label
        horizontal_label_offset = 1 / 5
        vertical_label_offset = 1 / 3

        # Draw a box halfway between the edges and the labels in to show where the bounds are.
        # Go entirely to the edge instead of only having lines at the halfway mark to be clearer about what's happening.
        def horizontal_line(y):
            ps.line((0, y), (page_width, y))

        def vertical_line(x):
            ps.line((x, 0), (x, page_height))

        if args.draw_edges:
            horizontal_line(vertical_label_offset * dpi // 2)
            horizontal_line(page_height - (vertical_label_offset * dpi // 2))
            vertical_line(horizontal_label_offset * dpi // 2)
            vertical_line(page_width - (horizontal_label_offset * dpi // 2))

        # 3 columns of 10 labels
        i = 0
        for column_index in range(3):
            for row_index in range(10):
                if not labels:
                    break

                if args.skip_count > 0:
                    args.skip_count -= 1
                    continue

                label = labels.pop()
                i += 1

                if not ("brand" in label and "color" in label):
                    print(f"label {i} is missing brand and/or color. Its fields are: {label}", file=sys.stderr)
                    exit(1)

                # Height in PostScript starts at the bottom of the page
                y = int((vertical_label_offset + label_height * (row_index + 1) - vertical_edge_padding) * dpi)
                x = int((horizontal_label_offset + (
                            label_width + horizontal_label_spacing) * column_index + horizontal_edge_padding) * dpi)

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

    subprocess.run(["ps2pdf",
                    f"-dDEVICEWIDTHPOINTS={page_width}", f"-dDEVICEHEIGHTPOINTS={page_height}",
                    # "-sPAPERSIZE=legal",  # For some cursed reason, this results in an extra 3 inches of blank space at the top of the page.
                    "labels.ps", "labels.pdf"])


main()
