"""Run a contiguous shard of the 729-case Vakya accuracy suite.

Usage:  python3 run_shard.py <start> <end> <out.json>
Runs cases [start, end) and writes per-case results to <out.json>.
Designed so several shards can run concurrently and be aggregated later.
"""
import json
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed

from run_parallel_tests import test_single_case


def main():
    start = int(sys.argv[1])
    end = int(sys.argv[2])
    out_path = sys.argv[3]

    with open("astrology_data .json", "r", encoding="utf-8") as f:
        data = json.load(f)

    end = min(end, len(data))
    indices = list(range(start, end))

    results = {}
    errors = {}
    with ProcessPoolExecutor(max_workers=4) as ex:
        futures = {ex.submit(test_single_case, i, data[i]): i for i in indices}
        for fut in as_completed(futures):
            i = futures[fut]
            try:
                idx, ok, res = fut.result()
                if ok:
                    results[idx] = res
                else:
                    errors[idx] = res
            except Exception as e:  # noqa: BLE001
                errors[i] = str(e)

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump({"results": {str(k): v for k, v in results.items()},
                   "errors": {str(k): v for k, v in errors.items()}},
                  f, ensure_ascii=False)

    print(f"shard {start}-{end}: {len(results)} ok, {len(errors)} errors -> {out_path}")


if __name__ == "__main__":
    main()
