import sys

from benchmark.data_chaos_monkey import main as northwind
from benchmark.yago_data_sampler import main as yago


def main() -> None:
    args = sys.argv[1:]

    for idx, arg in enumerate(args):
        if arg == "-yago":
            values = [args[idx + 1]] if idx + 1 < len(args) else None
            yago(values)

        if arg == "-northwind":
            northwind()


if __name__ == "__main__":
    main()
