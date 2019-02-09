# DAT2PIC
datfile to picture


## Requirements
- Numpy

- Matplotlib

- Pillow

- Animatplot

  ```shell
  $ pip install -r requirements.txt
  ```

  

### Usage

```shell
# dat -> png & pdf
$ python plot.py [dat_filename]

# datfiles -> gif
# "*.dat" is search query
$ python make_gif.py "*.dat"

# datfiles -> temperature_average
$ python make_gif.py "*.dat" -mt
# 2 click for select range of rectangle
# then 1 click complete
# if you want to select another, 1 right click
```

