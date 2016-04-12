import analyze_performance
import os


def main(path, N, metric):
    analyze_performance.main3(path, N, metric)


if __name__ == '__main__':
    main('../data/junkout/', 100, 'rets')