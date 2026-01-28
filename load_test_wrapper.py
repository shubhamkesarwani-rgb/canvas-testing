#!/usr/bin/env python3
"""
Load and Concurrency Testing Wrapper for Rule Processor
Monitors system resources, latency, and throughput during concurrent execution
"""

import os
import csv
import json
import time
import psutil
import threading
import argparse
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict
from dataclasses import dataclass, asdict
import statistics
from queue import Queue

# Import the process_prompt function from the main script
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rule_processor_v3_script import process_prompt, create_session, run_agent_sse

# ============================
# DATA STRUCTURES
# ============================

@dataclass
class PromptResult:
    """Result of processing a single prompt"""
    prompt_id: int
    prompt: str
    response: str
    status: str
    session_id: str
    latency_seconds: float
    start_time: str
    end_time: str
    worker_id: int
    iteration: int = 1
    iterations_count: int = 0

@dataclass
class ResourceSnapshot:
    """System resource snapshot"""
    timestamp: str
    cpu_percent: float
    memory_percent: float
    memory_mb: float
    cpu_count: int

@dataclass
class LoadTestSummary:
    """Summary of load test execution"""
    total_prompts: int
    concurrent_workers: int
    total_duration_seconds: float
    successful_prompts: int
    failed_prompts: int
    avg_latency_seconds: float
    median_latency_seconds: float
    min_latency_seconds: float
    max_latency_seconds: float
    p95_latency_seconds: float
    p99_latency_seconds: float
    throughput_per_second: float
    avg_cpu_percent: float
    max_cpu_percent: float
    avg_memory_percent: float
    max_memory_percent: float
    avg_memory_mb: float
    max_memory_mb: float

# ============================
# RESOURCE MONITORING
# ============================

class ResourceMonitor:
    """Monitors system resources in a background thread"""
    
    def __init__(self, interval: float = 1.0):
        self.interval = interval
        self.snapshots: List[ResourceSnapshot] = []
        self.monitoring = False
        self.thread: Optional[threading.Thread] = None
        self.process = psutil.Process()
        
    def start(self):
        """Start monitoring in background thread"""
        self.monitoring = True
        self.thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.thread.start()
        print(f"📊 Resource monitoring started (interval: {self.interval}s)")
        
    def stop(self):
        """Stop monitoring"""
        self.monitoring = False
        if self.thread:
            self.thread.join(timeout=5)
        print(f"📊 Resource monitoring stopped ({len(self.snapshots)} snapshots collected)")
        
    def _monitor_loop(self):
        """Background monitoring loop"""
        while self.monitoring:
            try:
                snapshot = ResourceSnapshot(
                    timestamp=datetime.now().isoformat(),
                    cpu_percent=self.process.cpu_percent(interval=0.1),
                    memory_percent=self.process.memory_percent(),
                    memory_mb=self.process.memory_info().rss / (1024 * 1024),
                    cpu_count=psutil.cpu_count()
                )
                self.snapshots.append(snapshot)
            except Exception as e:
                print(f"⚠️  Error monitoring resources: {e}")
            
            time.sleep(self.interval)
    
    def get_summary_stats(self) -> Dict[str, float]:
        """Get summary statistics of resource usage"""
        if not self.snapshots:
            return {}
        
        cpu_values = [s.cpu_percent for s in self.snapshots]
        memory_percent_values = [s.memory_percent for s in self.snapshots]
        memory_mb_values = [s.memory_mb for s in self.snapshots]
        
        return {
            'avg_cpu_percent': statistics.mean(cpu_values),
            'max_cpu_percent': max(cpu_values),
            'avg_memory_percent': statistics.mean(memory_percent_values),
            'max_memory_percent': max(memory_percent_values),
            'avg_memory_mb': statistics.mean(memory_mb_values),
            'max_memory_mb': max(memory_mb_values),
        }
    
    def save_snapshots(self, filepath: str):
        """Save resource snapshots to CSV"""
        if not self.snapshots:
            return
        
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=[
                'timestamp', 'cpu_percent', 'memory_percent', 
                'memory_mb', 'cpu_count'
            ])
            writer.writeheader()
            for snapshot in self.snapshots:
                writer.writerow(asdict(snapshot))
        print(f"💾 Resource snapshots saved to {filepath}")

# ============================
# CONCURRENT EXECUTION FUNCTIONS
# ============================

def execute_prompt_thread(prompt_id: int, prompt: str, thread_id: int, iteration: int, results_queue: Queue):
    """
    Execute a single prompt in a thread
    All threads start simultaneously for true concurrent load testing
    """
    start_time = datetime.now()
    start_timestamp = start_time.isoformat()
    
    try:
        response, status, session_id = process_prompt(prompt)
        end_time = datetime.now()
        latency = (end_time - start_time).total_seconds()
        
        result = PromptResult(
            prompt_id=prompt_id,
            prompt=prompt,
            response=response,
            status=status,
            session_id=session_id,
            latency_seconds=latency,
            start_time=start_timestamp,
            end_time=end_time.isoformat(),
            worker_id=thread_id,
            iteration=iteration
        )
        results_queue.put(result)
        
    except Exception as e:
        end_time = datetime.now()
        latency = (end_time - start_time).total_seconds()
        
        result = PromptResult(
            prompt_id=prompt_id,
            prompt=prompt,
            response=f"ERROR: {str(e)}",
            status="ERROR",
            session_id="N/A",
            latency_seconds=latency,
            start_time=start_timestamp,
            end_time=end_time.isoformat(),
            worker_id=thread_id,
            iteration=iteration
        )
        results_queue.put(result)

# ============================
# LOAD TEST ORCHESTRATOR
# ============================

class LoadTestOrchestrator:
    """Orchestrates load testing with multiple workers"""
    
    def __init__(
        self,
        input_file: str,
        output_dir: str = "load_test_results",
        concurrent_workers: int = 2,
        max_prompts: Optional[int] = None,
        iterations: int = 1,
        resource_monitor_interval: float = 1.0
    ):
        self.input_file = input_file
        self.output_dir = output_dir
        self.concurrent_workers = concurrent_workers
        self.max_prompts = max_prompts
        self.iterations = iterations
        self.resource_monitor_interval = resource_monitor_interval
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Initialize monitor
        self.monitor = ResourceMonitor(interval=resource_monitor_interval)
        
        # Results storage
        self.results: List[PromptResult] = []
        
    def load_prompts(self) -> List[Tuple[int, str]]:
        """Load prompts from CSV file"""
        with open(self.input_file, encoding='utf-8') as f:
            rows = list(csv.DictReader(f))
        
        prompt_col = next(c for c in rows[0] if c.lower() in ("prompt", "prompts", "input"))
        
        prompts = []
        for idx, row in enumerate(rows, 1):
            prompt = row.get(prompt_col, "").strip()
            if prompt:
                prompts.append((idx, prompt))
                if self.max_prompts and len(prompts) >= self.max_prompts:
                    break
        
        return prompts
    
    def run_load_test(self) -> LoadTestSummary:
        """Execute load test with truly concurrent execution and iterations"""
        print("\n" + "="*80)
        print("🚀 LOAD TEST STARTED - TRUE CONCURRENT EXECUTION")
        print("="*80)
        print(f"📁 Input file: {self.input_file}")
        print(f"🔥 Concurrent requests per iteration: {self.concurrent_workers}")
        print(f"🔁 Iterations: {self.iterations}")
        print(f"📊 Total requests: {self.concurrent_workers * self.iterations}")
        print(f"💻 CPU cores available: {psutil.cpu_count()}")
        print(f"📊 Resource monitoring interval: {self.resource_monitor_interval}s")
        print("="*80 + "\n")
        
        # Load prompts
        prompts = self.load_prompts()
        print(f"📋 Loaded {len(prompts)} prompts from {self.input_file}\n")
        
        # Calculate total prompts needed
        total_prompts_needed = self.concurrent_workers * self.iterations
        if len(prompts) < total_prompts_needed:
            print(f"⚠️  Warning: Only {len(prompts)} prompts available, need {total_prompts_needed}")
            print(f"   Will cycle through prompts to complete all iterations\n")
        
        # Start resource monitoring
        self.monitor.start()
        test_start_time = time.time()
        
        # Create results queue for thread-safe result collection
        results_queue = Queue()
        
        # Run iterations
        for iteration in range(1, self.iterations + 1):
            print("\n" + "="*80)
            print(f"🔁 ITERATION {iteration}/{self.iterations}")
            print("="*80)
            
            # Calculate prompt indices for this iteration
            start_idx = (iteration - 1) * self.concurrent_workers
            end_idx = start_idx + self.concurrent_workers
            
            # Get prompts for this iteration (cycle if necessary)
            prompts_for_iteration = []
            for i in range(start_idx, end_idx):
                prompt_idx = i % len(prompts)
                prompts_for_iteration.append(prompts[prompt_idx])
            
            print(f"🔥 Launching {len(prompts_for_iteration)} requests SIMULTANEOUSLY...\n")
            
            # Create and start all threads simultaneously
            threads = []
            thread_start_time = time.time()
            
            for idx, (prompt_id, prompt) in enumerate(prompts_for_iteration):
                thread = threading.Thread(
                    target=execute_prompt_thread,
                    args=(prompt_id, prompt, idx, iteration, results_queue),
                    daemon=True
                )
                threads.append(thread)
            
            # Start all threads at once for true concurrent load
            print(f"⚡ Starting all {len(threads)} requests simultaneously...")
            for thread in threads:
                thread.start()
            
            launch_time = time.time() - thread_start_time
            print(f"✅ All {len(threads)} requests launched in {launch_time:.3f}s\n")
            print(f"⏳ Waiting for all requests to complete...\n")
            
            # Wait for all threads to complete and show progress
            completed = 0
            for thread in threads:
                thread.join()
                completed += 1
                if completed % 5 == 0 or completed == len(threads):
                    print(f"   [{completed}/{len(threads)}] requests completed...")
            
            iteration_time = time.time() - thread_start_time
            print(f"\n✅ Iteration {iteration} completed in {iteration_time:.2f}s")
            
            # Small delay between iterations (optional, can be made configurable)
            if iteration < self.iterations:
                print(f"   ⏸  Preparing for next iteration...\n")
                time.sleep(0.5)
        
        # Stop monitoring
        test_end_time = time.time()
        self.monitor.stop()
        
        # Collect results from queue
        while not results_queue.empty():
            result = results_queue.get()
            self.results.append(result)
        
        # Sort results by iteration then prompt_id for consistent output
        self.results.sort(key=lambda x: (x.iteration, x.prompt_id))
        
        # Print individual results grouped by iteration
        print("\n" + "="*80)
        print("📊 INDIVIDUAL RESULTS")
        print("="*80)
        for iteration in range(1, self.iterations + 1):
            print(f"\n--- Iteration {iteration} ---")
            iteration_results = [r for r in self.results if r.iteration == iteration]
            for result in iteration_results:
                status_emoji = "✅" if result.status == "PASS" else "❌"
                print(f"{status_emoji} Prompt {result.prompt_id} | "
                      f"Thread {result.worker_id} | "
                      f"Latency: {result.latency_seconds:.2f}s | "
                      f"Status: {result.status}")
        
        total_duration = test_end_time - test_start_time
        
        # Generate summary
        summary = self._generate_summary(total_duration)
        
        # Save results
        self._save_results()
        
        return summary
    
    def _generate_summary(self, total_duration: float) -> LoadTestSummary:
        """Generate test summary statistics"""
        successful = [r for r in self.results if r.status == "PASS"]
        failed = [r for r in self.results if r.status != "PASS"]
        
        latencies = [r.latency_seconds for r in self.results]
        latencies.sort()
        
        resource_stats = self.monitor.get_summary_stats()
        
        summary = LoadTestSummary(
            total_prompts=len(self.results),
            concurrent_workers=self.concurrent_workers,
            total_duration_seconds=total_duration,
            successful_prompts=len(successful),
            failed_prompts=len(failed),
            avg_latency_seconds=statistics.mean(latencies) if latencies else 0,
            median_latency_seconds=statistics.median(latencies) if latencies else 0,
            min_latency_seconds=min(latencies) if latencies else 0,
            max_latency_seconds=max(latencies) if latencies else 0,
            p95_latency_seconds=latencies[int(len(latencies) * 0.95)] if latencies else 0,
            p99_latency_seconds=latencies[int(len(latencies) * 0.99)] if latencies else 0,
            throughput_per_second=len(self.results) / total_duration if total_duration > 0 else 0,
            avg_cpu_percent=resource_stats.get('avg_cpu_percent', 0),
            max_cpu_percent=resource_stats.get('max_cpu_percent', 0),
            avg_memory_percent=resource_stats.get('avg_memory_percent', 0),
            max_memory_percent=resource_stats.get('max_memory_percent', 0),
            avg_memory_mb=resource_stats.get('avg_memory_mb', 0),
            max_memory_mb=resource_stats.get('max_memory_mb', 0),
        )
        
        return summary
    
    def _save_results(self):
        """Save all results to files"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save detailed results
        results_file = os.path.join(self.output_dir, f"results_{timestamp}.csv")
        with open(results_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=[
                'iteration', 'prompt_id', 'prompt', 'response', 'status', 'session_id',
                'latency_seconds', 'start_time', 'end_time', 'worker_id', 'iterations_count'
            ])
            writer.writeheader()
            for result in self.results:
                writer.writerow(asdict(result))
        print(f"\n💾 Detailed results saved to {results_file}")
        
        # Save resource snapshots
        resource_file = os.path.join(self.output_dir, f"resources_{timestamp}.csv")
        self.monitor.save_snapshots(resource_file)
        
        # Save summary
        summary_file = os.path.join(self.output_dir, f"summary_{timestamp}.json")
        summary = self._generate_summary(
            sum(r.latency_seconds for r in self.results)
        )
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(asdict(summary), f, indent=2)
        print(f"💾 Summary saved to {summary_file}")
    
    def print_summary(self, summary: LoadTestSummary):
        """Print formatted summary to console"""
        print("\n" + "="*80)
        print("📊 LOAD TEST SUMMARY - CONCURRENT LOAD")
        print("="*80)
        print(f"\n📈 EXECUTION METRICS:")
        print(f"  Total Prompts Processed: {summary.total_prompts}")
        print(f"  Successful: {summary.successful_prompts} ({summary.successful_prompts/summary.total_prompts*100:.1f}%)")
        print(f"  Failed: {summary.failed_prompts} ({summary.failed_prompts/summary.total_prompts*100:.1f}%)")
        print(f"  Concurrent Requests: {summary.concurrent_workers}")
        print(f"  Total Duration: {summary.total_duration_seconds:.2f}s")
        print(f"  Throughput: {summary.throughput_per_second:.2f} prompts/sec")
        
        print(f"\n⏱️  LATENCY METRICS:")
        print(f"  Average: {summary.avg_latency_seconds:.2f}s")
        print(f"  Median: {summary.median_latency_seconds:.2f}s")
        print(f"  Min: {summary.min_latency_seconds:.2f}s")
        print(f"  Max: {summary.max_latency_seconds:.2f}s")
        print(f"  P95: {summary.p95_latency_seconds:.2f}s")
        print(f"  P99: {summary.p99_latency_seconds:.2f}s")
        
        print(f"\n💻 RESOURCE USAGE:")
        print(f"  CPU Usage:")
        print(f"    Average: {summary.avg_cpu_percent:.2f}%")
        print(f"    Peak: {summary.max_cpu_percent:.2f}%")
        print(f"  Memory Usage:")
        print(f"    Average: {summary.avg_memory_mb:.2f} MB ({summary.avg_memory_percent:.2f}%)")
        print(f"    Peak: {summary.max_memory_mb:.2f} MB ({summary.max_memory_percent:.2f}%)")
        
        print("="*80 + "\n")

# ============================
# MAIN EXECUTION
# ============================

def main():
    """Main entry point for load testing"""
    
    # ============================
    # PARSE COMMAND LINE ARGUMENTS
    # ============================
    parser = argparse.ArgumentParser(
        description='Concurrent Load Testing Framework',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Use defaults (20 workers, 3 iterations)
  python load_test_wrapper.py
  
  # Custom workers and iterations
  python load_test_wrapper.py --workers 10 --iterations 5
  
  # Light test
  python load_test_wrapper.py -w 5 -i 2
        """
    )
    
    parser.add_argument(
        '-w', '--workers',
        type=int,
        default=20,
        help='Number of concurrent requests per iteration (default: 20)'
    )
    
    parser.add_argument(
        '-i', '--iterations',
        type=int,
        default=1,
        help='Number of iterations to run (default: 3)'
    )
    
    parser.add_argument(
        '-f', '--file',
        type=str,
        default='100prompts_for_automation.csv',
        help='Input CSV file with prompts (default: 100prompts_for_automation.csv)'
    )
    
    parser.add_argument(
        '-o', '--output',
        type=str,
        default='load_test_results',
        help='Output directory for results (default: load_test_results)'
    )
    
    args = parser.parse_args()
    
    # ============================
    # LOAD TEST CONFIGURATION
    # ============================
    
    # Input/Output
    INPUT_FILE = args.file
    OUTPUT_DIR = args.output
    
    # Concurrency Settings - SIMULTANEOUS CONCURRENT REQUESTS WITH ITERATIONS
    CONCURRENT_WORKERS = args.workers
    ITERATIONS = args.iterations
    MAX_PROMPTS = None       # Not used - uses CONCURRENT_WORKERS × ITERATIONS prompts
    
    # Monitoring Settings
    RESOURCE_MONITOR_INTERVAL = 1.0  # Check resources every 1 second
    
    # ============================
    
    print("\n" + "="*80)
    print("🔬 TRUE CONCURRENT LOAD TESTING WITH ITERATIONS")
    print("="*80)
    print(f"Configuration:")
    print(f"  Input: {INPUT_FILE}")
    print(f"  Output: {OUTPUT_DIR}/")
    print(f"  Concurrent Requests per Iteration: {CONCURRENT_WORKERS}")
    print(f"  Iterations: {ITERATIONS}")
    print(f"  Total Requests: {CONCURRENT_WORKERS * ITERATIONS}")
    print(f"  Test Mode: {ITERATIONS} waves of {CONCURRENT_WORKERS} concurrent requests")
    print("="*80 + "\n")
    
    # Initialize and run load test
    orchestrator = LoadTestOrchestrator(
        input_file=INPUT_FILE,
        output_dir=OUTPUT_DIR,
        concurrent_workers=CONCURRENT_WORKERS,
        max_prompts=MAX_PROMPTS,
        iterations=ITERATIONS,
        resource_monitor_interval=RESOURCE_MONITOR_INTERVAL
    )
    
    try:
        summary = orchestrator.run_load_test()
        orchestrator.print_summary(summary)
        
        print("✅ Load test completed successfully!")
        print(f"📂 Results saved in: {OUTPUT_DIR}/")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Load test interrupted by user")
        orchestrator.monitor.stop()
    except Exception as e:
        print(f"\n\n❌ Load test failed: {e}")
        import traceback
        traceback.print_exc()
        orchestrator.monitor.stop()

if __name__ == "__main__":
    main()