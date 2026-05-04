"""
PowerSense Model Trainer
========================
Run this script on your log files to train and export the model.

Usage:
    python train_model.py log1.txt log2.txt log3.txt

Output:
    power_model.json  — load this in the web app
"""

import sys
import json
import re
import numpy as np
from collections import Counter


def parse_log(filepath):
    values = []
    timestamps = []
    with open(filepath, 'r') as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) == 2:
                try:
                    timestamps.append(parts[0])
                    values.append(float(parts[1]))
                except:
                    pass
            elif len(parts) == 1:
                try:
                    values.append(float(parts[0]))
                    timestamps.append(None)
                except:
                    pass
    return np.array(values), timestamps


def extract_features(values, window=10):
    features = []
    for i in range(len(values)):
        start = max(0, i - window)
        window_vals = values[start:i+1]
        feat = {
            'value': values[i],
            'rolling_mean': float(np.mean(window_vals)),
            'rolling_std': float(np.std(window_vals)) if len(window_vals) > 1 else 0.0,
            'rolling_min': float(np.min(window_vals)),
            'rolling_max': float(np.max(window_vals)),
            'delta': float(values[i] - values[i-1]) if i > 0 else 0.0,
            'delta2': float(values[i] - values[i-2]) if i > 1 else 0.0,
        }
        features.append(feat)
    return features


def compute_global_stats(all_values):
    return {
        'mean': float(np.mean(all_values)),
        'std': float(np.std(all_values)),
        'min': float(np.min(all_values)),
        'max': float(np.max(all_values)),
        'p5': float(np.percentile(all_values, 5)),
        'p25': float(np.percentile(all_values, 25)),
        'p75': float(np.percentile(all_values, 75)),
        'p95': float(np.percentile(all_values, 95)),
        'median': float(np.median(all_values)),
        'count': int(len(all_values)),
    }


def classify_value(value, stats):
    mean = stats['mean']
    std = stats['std']
    if value < mean - 2 * std:
        return 'critical_low'
    elif value < mean - std:
        return 'low'
    elif value > mean + 2 * std:
        return 'critical_high'
    elif value > mean + std:
        return 'high'
    else:
        return 'normal'


def compute_zscore_thresholds(all_values):
    mean = np.mean(all_values)
    std = np.std(all_values)
    return {
        'mean': float(mean),
        'std': float(std),
        'anomaly_threshold': 2.5,
        'warning_threshold': 1.5,
    }


def build_transition_matrix(values, stats):
    labels = [classify_value(v, stats) for v in values]
    classes = ['critical_low', 'low', 'normal', 'high', 'critical_high']
    matrix = {c: {c2: 0 for c2 in classes} for c in classes}
    for i in range(1, len(labels)):
        matrix[labels[i-1]][labels[i]] += 1
    for row in matrix:
        total = sum(matrix[row].values())
        if total > 0:
            for col in matrix[row]:
                matrix[row][col] = round(matrix[row][col] / total, 4)
    return matrix


def linear_regression_params(values):
    n = len(values)
    x = np.arange(n)
    slope = float(np.polyfit(x, values, 1)[0])
    intercept = float(np.polyfit(x, values, 1)[1])
    return {'slope': slope, 'intercept': intercept, 'n': n}


def compute_stability_score(values, stats):
    cv = stats['std'] / stats['mean'] if stats['mean'] != 0 else 0
    anomaly_rate = sum(1 for v in values if abs(v - stats['mean']) > 2.5 * stats['std']) / len(values)
    range_score = 1 - min((stats['max'] - stats['min']) / (stats['mean'] * 0.1 + 0.001), 1)
    stability = (1 - min(cv * 10, 1)) * 0.4 + (1 - anomaly_rate) * 0.4 + range_score * 0.2
    return round(float(stability * 100), 1)


def train(filepaths):
    all_values = []
    file_stats = []

    print(f"\nLoading {len(filepaths)} file(s)...")

    for fp in filepaths:
        try:
            vals, _ = parse_log(fp)
            if len(vals) == 0:
                print(f"  Warning: No values found in {fp}")
                continue
            all_values.extend(vals.tolist())
            fstats = compute_global_stats(vals)
            fstats['file'] = fp
            file_stats.append(fstats)
            print(f"  {fp}: {len(vals)} readings, mean={fstats['mean']:.4f}, std={fstats['std']:.4f}")
        except Exception as e:
            print(f"  Error reading {fp}: {e}")

    if not all_values:
        print("No data loaded. Exiting.")
        sys.exit(1)

    all_values = np.array(all_values)
    print(f"\nTotal readings: {len(all_values)}")

    global_stats = compute_global_stats(all_values)
    zscore_params = compute_zscore_thresholds(all_values)
    transition = build_transition_matrix(all_values, global_stats)
    regression = linear_regression_params(all_values)
    stability = compute_stability_score(all_values, global_stats)

    label_counts = Counter([classify_value(v, global_stats) for v in all_values])

    model = {
        'version': '1.0',
        'trained_on': int(len(all_values)),
        'files': len(filepaths),
        'global_stats': global_stats,
        'zscore_params': zscore_params,
        'classification_thresholds': {
            'critical_low': float(global_stats['mean'] - 2 * global_stats['std']),
            'low': float(global_stats['mean'] - global_stats['std']),
            'normal_low': float(global_stats['mean'] - global_stats['std']),
            'normal_high': float(global_stats['mean'] + global_stats['std']),
            'high': float(global_stats['mean'] + global_stats['std']),
            'critical_high': float(global_stats['mean'] + 2 * global_stats['std']),
        },
        'transition_matrix': transition,
        'regression': regression,
        'stability_score': stability,
        'label_distribution': dict(label_counts),
        'file_stats': file_stats,
        'histogram': {
            'bins': 20,
            'range': [float(all_values.min()), float(all_values.max())],
        }
    }

    output = 'power_model.json'
    with open(output, 'w') as f:
        json.dump(model, f, indent=2)

    print(f"\nModel trained successfully!")
    print(f"Stability score: {stability}/100")
    print(f"Saved to: {output}")
    print(f"\nLabel distribution:")
    for label, count in sorted(label_counts.items()):
        pct = count / len(all_values) * 100
        print(f"  {label}: {count} ({pct:.1f}%)")
    print(f"\nNow upload power_model.json to the web app.")
    return model


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python train_model.py file1.txt file2.txt ...")
        print("Example: python train_model.py voltagedata.txt")
        sys.exit(1)
    train(sys.argv[1:])
