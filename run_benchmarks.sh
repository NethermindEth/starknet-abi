
if [ -f "venv/bin/activate" ]; then
  ACTIVATE_SCRIPT="bin/activate"
  PY_BIN="bin/python"
else
  ACTIVATE_SCRIPT="Scripts/activate"
  PY_BIN="Scripts/python"
fi



# Create virtual environment & install dependencies for each python version

source benchmarks/.venv_310/$ACTIVATE_SCRIPT
pip install poetry
poetry install --all-extras
pip install pyperformance starknet_py
deactivate

source benchmarks/.venv_311/$ACTIVATE_SCRIPT
pip install poetry
poetry install --all-extras
pip install pyperformance starknet_py
deactivate

source benchmarks/.venv_312/$ACTIVATE_SCRIPT
pip install poetry
poetry install --all-extras
pip install pyperformance starknet_py
deactivate


# Reset to the default python venv
source .venv/$ACTIVATE_SCRIPT

for PY_VERSION in '310' '311' '312'; do
  PY="benchmarks/.venv_${PY_VERSION}/${PY_BIN}"
  printf '%.0s-' {1..90}; echo
  echo "Running benchmarks for $($PY --version)"
  printf '%.0s-' {1..90}; echo

  echo "Running Benchmark for starknet-py ---- Setup"
  $PY -m pyperf timeit \
    --name setup \
    --setup "from benchmarks.starknet_py import bench_setup; func = bench_setup()" \
    --append benchmarks/$PY_VERSION-stark-py.json \
    "func()"

  echo "Running benchmarks for starknet-py ---- Simple Decode"
  $PY -m pyperf timeit \
    --name simple-decode \
    --setup "from benchmarks.starknet_py import bench_simple_decode; func = bench_simple_decode()" \
    --append benchmarks/$PY_VERSION-stark-py.json \
    "func()"

  echo "Running Benchmark for starknet-py ---- Complex Decode"
  $PY -m pyperf timeit \
    --name complex-decode \
    --setup "from benchmarks.starknet_py import bench_complex_decode; func = bench_complex_decode()" \
    --append benchmarks/$PY_VERSION-stark-py.json \
    "func()"

  echo "Running Benchmark for starknet-abi ---- Setup"
  $PY -m pyperf timeit \
    --name setup \
    --setup "from benchmarks.starknet_abi_base import bench_setup; func = bench_setup()" \
    --append benchmarks/$PY_VERSION-stark-abi.json \
    "func()"

  echo "Running benchmarks for starknet-abi ---- Simple Decode"
  $PY -m pyperf timeit \
    --name simple-decode \
    --setup "from benchmarks.starknet_abi_base import bench_simple_decode; func = bench_simple_decode()" \
    --append benchmarks/$PY_VERSION-stark-abi.json \
    "func()"

  echo "Running Benchmark for starknet-abi ---- Complex Decode"
  $PY -m pyperf timeit \
    --name complex-decode \
    --setup "from benchmarks.starknet_abi_base import bench_complex_decode; func = bench_complex_decode()" \
    --append benchmarks/$PY_VERSION-stark-abi.json \
    "func()"
done

echo "# Benchmark Results" > benchmarks/results.md

pyperf compare_to benchmarks/310-stark-py.json benchmarks/311-stark-py.json benchmarks/312-stark-py.json \
                  benchmarks/310-stark-abi.json benchmarks/311-stark-abi.json benchmarks/312-stark-abi.json \
                  --table --table-format=md >> benchmarks/results.md