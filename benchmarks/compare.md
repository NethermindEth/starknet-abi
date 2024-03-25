# Starknet-abi Benchmarks
## Setup Benchmarks
| Benchmark | 310-stark-py-setup | 311-stark-py-setup     | 312-stark-py-setup   | 310-stark-abi-setup     | 311-stark-abi-setup     | 312-stark-abi-setup     |
|-----------|:------------------:|:----------------------:|:--------------------:|:-----------------------:|:-----------------------:|:-----------------------:|
| setup     | 1.44 sec           | 1.03 sec: 1.40x faster | 995 ms: 1.45x faster | 373 us: 3869.36x faster | 314 us: 4593.88x faster | 287 us: 5022.58x faster |
## Simple Decode Benchmarks
| Benchmark     | 310-stark-py-simple-decode | 311-stark-py-simple-decode | 312-stark-py-simple-decode | 310-stark-abi-simple-decode | 311-stark-abi-simple-decode | 312-stark-abi-simple-decode |
|---------------|:--------------------------:|:--------------------------:|:--------------------------:|:---------------------------:|:---------------------------:|:---------------------------:|
| simple-decode | 248 us                     | not significant            | 312 us: 1.26x slower       | 4.37 us: 56.87x faster      | 3.55 us: 70.02x faster      | 2.64 us: 94.02x faster      |
