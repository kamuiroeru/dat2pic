# DAT2PIC
datfile to picture


## Requirements
- Numpy
- Matplotlib
- Pillow
- Animatplot

### Usage

```python
# dat -> png & pdf
python plot.py [dat_filename]

# datfiles -> gif
# "*.dat" is search query
python make_gif.py "*.dat"

# datfiles -> temperature_average
python make_gif.py "*.dat" -mt
```

