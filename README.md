# knit-portrait
My take on the portrait abstraction algorithm introduced by Petros Vrellis, transforming portrait photographs into a knit portrait.

## Usage

There are two main functions, used for computation and visualization of the knit portrait.

Type:
`python compute_string_order.py -h` to see the following help for the computation script

```
usage: compute_string_order.py [-h] [-f FILE] [-sa SAVE_AS] [-s SIZE]
                               [-cf CROP_FACTOR] [-st STRINGS] [-ho HOOKS]
                               [-d DISCOUNT] [-nd NEIGHBOR_DISTANCE]
                               [-r RANDOM_ACCEPT_RATE]

optional arguments:
  -h, --help            show this help message and exit
  -f FILE, --file FILE  image to process
  -sa SAVE_AS, --save_as SAVE_AS
                        image to process
  -s SIZE, --size SIZE  new size in pixel of the input image (default=2500)
  -cf CROP_FACTOR, --crop_factor CROP_FACTOR
                        crop image in every direction by this factor
                        (default=1)
  -st STRINGS, --strings STRINGS
                        number of precomputed strings (default=5000)
  -ho HOOKS, --hooks HOOKS
                        number of hooks (default=201)
  -d DISCOUNT, --discount DISCOUNT
                        discount each selected line of the original image by
                        multiplying with this value (default=0.3)
  -nd NEIGHBOR_DISTANCE, --neighbor_distance NEIGHBOR_DISTANCE
                        minimum hook distance (default=15)
  -r RANDOM_ACCEPT_RATE, --random_accept_rate RANDOM_ACCEPT_RATE
                        randomly make a tring with this probability
                        (default=0)
```

and type:
`python display_result.py -h` to see the following help for the visualization script

```
usage: display_result.py [-h] [-st STRINGS] config_file

positional arguments:
  config_file

optional arguments:
  -h, --help            show this help message and exit
  -st STRINGS, --strings STRINGS
                        number of precomputed strings - set to -1 to show all
                        precomputed strings (default=-1)
```

A `.json` file will be created after running `compute_string_order.py`, storing all information about the computation, that have been specified in key value paired arguments.

Furthermore a `.csv` file will store the order of strings that have to be knitted. Thereby the first column is the index of the string and the second and third column from which to which hook the string must be span.

Example:

`python compute_string_order.py -f ./tommy.jpg -sa ./tommy -s 2500 -cf 1 -st 5000 -ho 201 -d 0.3 -nd 15 -r 0`

The above example is composed of all default values. It will take "tommy.jpg", resize it to 2500 x 2500px, crop it by a factor of 1 (no cropping) and compute 5000 strings for 201 hooks. Furthermore no random strings are set (`-r 0`) and a minimum distance of 15 hooks to find the next best hook will be applied. Once a thread was "drawn", the pixel values python compute_string_order.pyon this line will be multiplied by 0.3 to discount them for the next iteration.

Afterwards calling `python display_result.py tommy.json -st 2500` will display the original next to the knitted portrait using the first 2500 strings. 

Since it is not desirable to recompute the entire order, it is advisable to precompuet more strings than probably needed in order to play around with the amout for displaying and thus result selection.

Here is the example result from above:

![Image of knitted Tommy](https://github.com/tommyclausner/knit-portrait/tommy_result.jpg)
