# Benchmark Results
| Benchmark      | 310-stark-py | 311-stark-py           | 312-stark-py         | 310-stark-abi           | 311-stark-abi           | 312-stark-abi           |
|----------------|:------------:|:----------------------:|:--------------------:|:-----------------------:|:-----------------------:|:-----------------------:|
| setup          | 1.18 sec     | 1.01 sec: 1.17x faster | 985 ms: 1.20x faster | 432 us: 2737.40x faster | 379 us: 3123.71x faster | 340 us: 3473.21x faster |
| simple-decode  | 233 us       | 230 us: 1.01x faster   | 286 us: 1.23x slower | 4.09 us: 57.08x faster  | 3.44 us: 67.75x faster  | 2.47 us: 94.46x faster  |
| complex-decode | 446 us       | 432 us: 1.03x faster   | 496 us: 1.11x slower | 37.2 us: 11.97x faster  | 30.3 us: 14.70x faster  | 23.0 us: 19.36x faster  |
