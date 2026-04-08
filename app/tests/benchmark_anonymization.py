import time
import shutil
from pathlib import Path

from app.services.anonymization import AnonymizationService
from app.schemas.anonymization import MaskingConfig

# CONFIGURATION
INPUT_FILE = "app/data/large.csv"
WORK_FILE = "app/data/tmp_test.csv"

COLUMNS = [
    "Address",
    "Email",
]

RUNS = 3


def prepare_file():
    shutil.copy(INPUT_FILE, WORK_FILE)


def build_configs(method: str):
    configs = []

    for col in COLUMNS:
        if method == "proportional":
            configs.append(
                MaskingConfig(
                    column_name=col,
                    method="proportional",
                    params={"alpha": 0.5}
                )
            )

        elif method == "structure_aware":
            configs.append(
                MaskingConfig(
                    column_name=col,
                    method="structure_aware",
                    params={"p": 2, "q": 2}
                )
            )

        else:
            raise ValueError(f"Unknown method: {method}")

    return configs

def run_once(service, configs, suffix):
    prepare_file()

    output_path = WORK_FILE.replace(".csv", f"_{suffix}.csv")

    start = time.perf_counter()

    service._process_csv_streaming(
        WORK_FILE,
        output_path,
        configs
    )

    end = time.perf_counter()

    return end - start


def benchmark_method(name, service):
    print(f"\n===== Benchmark: {name} ({len(COLUMNS)} columns) =====")

    configs = build_configs(name)
    times = []

    for i in range(RUNS):
        print(f"Run {i+1}...")

        t = run_once(service, configs, name)
        times.append(t)

        print(f"Time: {t:.2f} seconds")

    avg = sum(times) / len(times)

    file_size_mb = Path(INPUT_FILE).stat().st_size / (1024 * 1024)
    throughput = file_size_mb / avg

    print("\n------------------------------")
    print(f"{name} Average: {avg:.2f} seconds")
    print(f"{name} Throughput: {throughput:.2f} MB/s")
    print("------------------------------")

    return avg

def run_benchmark():
    service = AnonymizationService(None, None)

    avg_prop = benchmark_method("proportional", service)
    avg_struct = benchmark_method("structure_aware", service)

    print(f"FINAL COMPARISON ({len(COLUMNS)} columns)")

    print(f"Proportional:     {avg_prop:.2f} s")
    print(f"Structure-aware:  {avg_struct:.2f} s")

    if avg_prop < avg_struct:
        print("→ Proportional is faster")
    else:
        print("→ Structure-aware is faster")


if __name__ == "__main__":
    run_benchmark()