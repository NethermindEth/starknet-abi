
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
done


setup_bench_files=()
simple_decode_bench_files=()
# Iterate over combinations of numbers and file extensions
for ext in py abi; do
    for num in 310 311 312; do
        # Generate filenames and append them to the array
        setup_bench_files+=("benchmarks/${num}-stark-${ext}-setup.json")
        simple_decode_bench_files+=("benchmarks/${num}-stark-${ext}-simple-decode.json")
    done
done

echo "# Starknet-abi Benchmarks" > benchmarks/compare.md

echo "## Setup Benchmarks" >> benchmarks/compare.md
pyperf compare_to "${setup_bench_files[@]}" --table --table-format=md >> benchmarks/compare.md
echo "## Simple Decode Benchmarks" >> benchmarks/compare.md
pyperf compare_to "${simple_decode_bench_files[@]}" --table --table-format=md >> benchmarks/compare.md
