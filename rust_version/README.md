# Rust version of knit-portrait

This version runs much faster than the Python implementation an is therefore 
better suited for quick testing of different parameter settings.

## Installation
This repo only contains the source code and needs to be compiled.

1. Install Rust following the steps as described here: https://www.rust-lang.org/tools/install
2. Navigate to the repo directory e.g. via `cd knit-portrait/rust_version` 
   (after having cloned the repo).
3. Compile the command line program via `cargo build --profile release`

## Usage
The compiled version is located in 
`knit-portrait/rust_version/target/release/` and can be called using 
multiple ordered arguments:

```bash
cd ./knit-portrait/rust_version/target/release
IMAGE=</path/to/image.jpg>
OUTPUT=</path/to/output.csv>
HOOKS=201 #(optional; default is 201)
STRINGS=5000 #(optional; default is 5000)
DISCOUNT=0.7 #(optional; default is 0.7)
NEIGHBOR_DISTANCE=15 #(optional; default is 15)

./knit_portrait $IMAGE $OUTPUT $HOOKS $STRINGS $DISCOUNT $NEIGHBOR_DISTANCE
```

All arguments must be specified in this order. To e.g. provide 
`NEIGHBOR_DISTANCE`, all previous arguments must be provided as well.

## Results
The result is compatible with the Python version and can thus be used 
similarly for visualization and further processing. 

### Quick visualization using Python
```python
import numpy as np
import matplotlib.pyplot as plt

num_hooks = 201  # must be equal to what has been set before
num_display_strings = 3000  # smaller or equal to the strings computed

# Compute circle coordinates
theta = np.linspace(0, 2 * np.pi, num_hooks)
circle = np.asarray([np.cos(theta), np.sin(theta)]).T

# load data
data = np.genfromtxt('tommy.csv', delimiter=',', dtype=int)

# Use data to index circle coordinates
for (_, d_from, d_to) in data[:num_display_strings]:
    plt.plot([circle[d_from, 0], circle[d_to, 0]],
             [circle[d_from, 1], circle[d_to, 1]], color="k", linewidth=0.1)

# Cosmetics
plt.axis('equal')
plt.axis('off')
plt.tight_layout()
plt.gca().invert_yaxis()
plt.show()
```

A documentation can be compiled using `cargo doc --open`.