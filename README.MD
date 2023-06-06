# PS1-Stray-Sheep

Stray Sheep - The Adventure of Poe & Merry

---


## Usage
- `--input`
  - `<file>`
  - `<directory>`
- `--output`
  - `<directory>`
  - `<directory>`
- `--mode`
  - `extract`
  - `create`

### Examples

```batch
python main.py --mode=extract --input=GBL --output=EXTRACTED
```

---

```batch
python main.py --mode=create --input=EXTRACTED --output=CREATED
```

## Requirements
* [Python 3.11.0](https://www.python.org/downloads/release/python-3110/)
* [kaitaistruct 0.10](https://pypi.org/project/kaitaistruct/0.10/)

---

## Built with
 - [Kaitai Struct](https://kaitai.io/)
 - [PyCharm](https://www.jetbrains.com/pycharm/) 2023.3.2 EAP (Community Edition)
