#!/usr/bin/env python3
"""
Visualize Load Test Results
Generates charts and analysis from load test data
"""

import os
import csv
import json
import glob
from datetime import datetime
from typing import List, Dict, Any

try:
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    print("⚠️  matplotlib not available. Install with: pip install matplotlib")

def find_latest_results(output_dir: str = "load_test_results") -> Dict[str, str]:
    """Find the latest test results files"""
    if not os.path.exists(output_dir):
        print(f"❌ Directory not found: {output_dir}")
        return {}
    
    results_files = glob.glob(os.path.join(output_dir, "results_*.csv"))
    resource_files = glob.glob(os.path.join(output_dir, "resources_*.csv"))
    summary_files = glob.glob(os.path.join(output_dir, "summary_*.json"))
    
    if not results_files:
        print(f"❌ No results files found in {output_dir}")
        return {}
    
    # Get latest files
    latest = {
        'results': max(results_files, key=os.path.getmtime),
        'resources': max(resource_files, key=os.path.getmtime) if resource_files else None,
        'summary': max(summary_files, key=os.path.getmtime) if summary_files else None,
    }
    
    return latest

def load_results(results_file: str) -> List[Dict[str, Any]]:
    """Load results from CSV"""
    with open(results_file, 'r', encoding='utf-8') as f:
        return list(csv.DictReader(f))

def load_resources(resource_file: str) -> List[Dict[str, Any]]:
    """Load resource snapshots from CSV"""
    with open(resource_file, 'r', encoding='utf-8') as f:
        return list(csv.DictReader(f))

def load_summary(summary_file: str) -> Dict[str, Any]:
    """Load summary from JSON"""
    with open(summary_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def print_text_analysis(results: List[Dict], resources: List[Dict], summary: Dict):
    """Print text-based analysis"""
    print("\n" + "="*80)
    print("📊 LOAD TEST ANALYSIS")
    print("="*80)
    
    # Summary metrics
    if summary:
        print(f"\n📈 KEY METRICS:")
        print(f"  Total Prompts: {summary['total_prompts']}")
        print(f"  Success Rate: {summary['successful_prompts']/summary['total_prompts']*100:.1f}%")
        print(f"  Throughput: {summary['throughput_per_second']:.2f} prompts/sec")
        print(f"  Avg Latency: {summary['avg_latency_seconds']:.2f}s")
        print(f"  P95 Latency: {summary['p95_latency_seconds']:.2f}s")
        print(f"  P99 Latency: {summary['p99_latency_seconds']:.2f}s")
        print(f"  Peak CPU: {summary['max_cpu_percent']:.1f}%")
        print(f"  Peak Memory: {summary['max_memory_mb']:.1f} MB")
    
    # Latency distribution
    latencies = [float(r['latency_seconds']) for r in results]
    latencies.sort()
    
    print(f"\n⏱️  LATENCY DISTRIBUTION:")
    print(f"  Min: {min(latencies):.2f}s")
    print(f"  25th percentile: {latencies[int(len(latencies)*0.25)]:.2f}s")
    print(f"  50th percentile (median): {latencies[int(len(latencies)*0.50)]:.2f}s")
    print(f"  75th percentile: {latencies[int(len(latencies)*0.75)]:.2f}s")
    print(f"  90th percentile: {latencies[int(len(latencies)*0.90)]:.2f}s")
    print(f"  95th percentile: {latencies[int(len(latencies)*0.95)]:.2f}s")
    print(f"  99th percentile: {latencies[int(len(latencies)*0.99)]:.2f}s")
    print(f"  Max: {max(latencies):.2f}s")
    
    # Worker performance
    worker_stats = {}
    for r in results:
        worker_id = int(r['worker_id'])
        if worker_id not in worker_stats:
            worker_stats[worker_id] = []
        worker_stats[worker_id].append(float(r['latency_seconds']))
    
    print(f"\n👷 WORKER PERFORMANCE:")
    for worker_id in sorted(worker_stats.keys()):
        latencies = worker_stats[worker_id]
        avg_latency = sum(latencies) / len(latencies)
        print(f"  Worker {worker_id}: {len(latencies)} prompts, avg {avg_latency:.2f}s")
    
    # Status breakdown
    status_counts = {}
    for r in results:
        status = r['status']
        status_counts[status] = status_counts.get(status, 0) + 1
    
    print(f"\n✅ STATUS BREAKDOWN:")
    for status, count in status_counts.items():
        print(f"  {status}: {count} ({count/len(results)*100:.1f}%)")
    
    print("="*80 + "\n")

def create_visualizations(results: List[Dict], resources: List[Dict], output_dir: str):
    """Create visualization charts"""
    if not MATPLOTLIB_AVAILABLE:
        print("⚠️  Skipping visualizations (matplotlib not installed)")
        return
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Create figure with subplots
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('Load Test Results Analysis', fontsize=16, fontweight='bold')
    
    # 1. Latency over time
    ax1 = axes[0, 0]
    latencies = [float(r['latency_seconds']) for r in results]
    prompt_ids = [int(r['prompt_id']) for r in results]
    ax1.plot(prompt_ids, latencies, marker='o', linestyle='-', alpha=0.6)
    ax1.set_xlabel('Prompt ID')
    ax1.set_ylabel('Latency (seconds)')
    ax1.set_title('Latency per Prompt')
    ax1.grid(True, alpha=0.3)
    
    # 2. Latency distribution (histogram)
    ax2 = axes[0, 1]
    ax2.hist(latencies, bins=20, edgecolor='black', alpha=0.7)
    ax2.set_xlabel('Latency (seconds)')
    ax2.set_ylabel('Frequency')
    ax2.set_title('Latency Distribution')
    ax2.axvline(sum(latencies)/len(latencies), color='red', linestyle='--', label='Mean')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # 3. CPU Usage over time
    ax3 = axes[1, 0]
    if resources:
        timestamps = [datetime.fromisoformat(r['timestamp']) for r in resources]
        cpu_values = [float(r['cpu_percent']) for r in resources]
        ax3.plot(timestamps, cpu_values, color='orange', linewidth=2)
        ax3.set_xlabel('Time')
        ax3.set_ylabel('CPU Usage (%)')
        ax3.set_title('CPU Usage Over Time')
        ax3.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
        plt.setp(ax3.xaxis.get_majorticklabels(), rotation=45)
        ax3.grid(True, alpha=0.3)
    else:
        ax3.text(0.5, 0.5, 'No resource data available', 
                ha='center', va='center', transform=ax3.transAxes)
    
    # 4. Memory Usage over time
    ax4 = axes[1, 1]
    if resources:
        memory_values = [float(r['memory_mb']) for r in resources]
        ax4.plot(timestamps, memory_values, color='green', linewidth=2)
        ax4.set_xlabel('Time')
        ax4.set_ylabel('Memory Usage (MB)')
        ax4.set_title('Memory Usage Over Time')
        ax4.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
        plt.setp(ax4.xaxis.get_majorticklabels(), rotation=45)
        ax4.grid(True, alpha=0.3)
    else:
        ax4.text(0.5, 0.5, 'No resource data available', 
                ha='center', va='center', transform=ax4.transAxes)
    
    plt.tight_layout()
    
    # Save figure
    chart_file = os.path.join(output_dir, f"analysis_{timestamp}.png")
    plt.savefig(chart_file, dpi=150, bbox_inches='tight')
    print(f"📊 Visualizations saved to {chart_file}")
    
    # Show plot
    plt.show()

def main():
    """Main entry point"""
    output_dir = "load_test_results"
    
    print("\n🔍 Finding latest load test results...")
    files = find_latest_results(output_dir)
    
    if not files.get('results'):
        print("❌ No results found. Run load test first.")
        return
    
    print(f"📂 Loading results from: {files['results']}")
    results = load_results(files['results'])
    
    resources = []
    if files.get('resources'):
        print(f"📂 Loading resources from: {files['resources']}")
        resources = load_resources(files['resources'])
    
    summary = {}
    if files.get('summary'):
        print(f"📂 Loading summary from: {files['summary']}")
        summary = load_summary(files['summary'])
    
    # Print text analysis
    print_text_analysis(results, resources, summary)
    
    # Create visualizations
    create_visualizations(results, resources, output_dir)

if __name__ == "__main__":
    main()
