# label-generator

For Avery 1"x2 5/8" labels such as [5160](https://www.avery.com/products/labels/5160)
used by 3D printing filament swatches such as [this](https://www.printables.com/model/111326-filament-swatch-library)
and [this](https://www.printables.com/model/367598-filament-swatches-avery-no-15660).
(I'm using the latter, which includes filament type in the print, so I'd put filament type in the notes if at all.)

## Setup

    sudo apt install -y ghostscript
    pip install -r requirements.txt

## Example

    python main.py example.yaml

[![example photo](/IMG_1987-480.jpg)](/IMG_1987.jpg)

## Format

Takes YAML list of filaments:

```yaml
- brand: Prusament
  color: Galaxy Black
```

`brand` and `color` are required. The others are optional:

* `url`: added as a QR code
* `note`: smaller font, and on the third line.
* `note2`: smaller font, and on the fourth line.
* `color2`: same font as color, but on the third line. Good for overflow.
* `color3`: same font as color, but on the fourth line. Good for overflow.
