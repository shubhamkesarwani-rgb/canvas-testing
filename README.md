# Concurrent Load Testing for Rule Processor Agent

Complete framework for testing how your Rule Processor Agent handles concurrent user load.

## 🚀 Quick Start for Testers

**Brand new?** Ultra-quick guide: **[TESTING_QUICKSTART.md](TESTING_QUICKSTART.md)** ⚡  
Just want to run the test? This is for you!



## 📚 Documentation

### For Testers
- **[TESTING_QUICKSTART.md](TESTING_QUICKSTART.md)** ⭐ - Ultra-fast start
  - Absolute quickest way to get started
  - Two commands: navigate + run
  - Perfect for first-time users
  


## 📁 Files

### Main Scripts
- `load_test_wrapper.py` - Main load testing script
- `rule_processor_v3_script.py` - Rule processor implementation
- `visualize_load_test.py` - Results visualization
- `quick_test.sh` - One-command test runner

### Configuration
- `load_test_requirements.txt` - Python dependencies
- `100prompts_for_automation.csv` - Test prompts

### Results
- `load_test_results/` - All test results saved here

## 🎯 What This Tests

- **Concurrent User Load** - Launch N requests simultaneously
- **Sustained Load (NEW!)** - Multiple waves/iterations of concurrent requests
- **System Response** - How agent handles burst traffic
- **Resource Usage** - CPU and memory under load
- **Performance Degradation** - Check if latency increases over iterations
- **Latency Distribution** - Response time consistency
- **Breaking Points** - Where system starts failing

## ⚡ Quick Commands

### Run Test (Recommended)
```bash
./quick_test.sh [workers] [iterations]
```

**Examples:**
```bash
./quick_test.sh              # Default: 20 workers × 3 iterations = 60 requests
./quick_test.sh 10 5         # Custom: 10 workers × 5 iterations = 50 requests
./quick_test.sh 5 2          # Light: 5 workers × 2 iterations = 10 requests
```

Automatically handles dependencies, runs test, and generates visualizations.

### Manual Commands
```bash
# Install dependencies manually (optional)
pip install -r load_test_requirements.txt

# Run with custom config
python load_test_wrapper.py --workers 20 --iterations 3

# Run with short options
python load_test_wrapper.py -w 10 -i 5

# See all options
python load_test_wrapper.py --help

# Generate visualizations separately
python visualize_load_test.py
```

## 🎛️ Configuration

### Quick Configuration (Recommended)
Use command line arguments:

```bash
./quick_test.sh [workers] [iterations]
```

**Recommended configurations:**
```bash
./quick_test.sh 5 2      # Light: 10 requests
./quick_test.sh 10 3     # Medium: 30 requests
./quick_test.sh 20 3     # Heavy: 60 requests (default)
./quick_test.sh 20 5     # Stress: 100 requests
./quick_test.sh 10 10    # Sustained: 100 requests in 10 waves
```


```

**See [ITERATIONS_GUIDE.md](ITERATIONS_GUIDE.md) for detailed information**

## 📊 Understanding Results

### Key Metrics

**Success Rate**
- 100% = Perfect
- 95-99% = Good
- <95% = Problem

**P95 Latency** (95% of requests faster than this)
- < 8s = Good
- 8-12s = Acceptable
- >12s = Problem

**CPU Usage** (2-core pod)
- <150% = Good
- 150-180% = High
- >180% = Near limit

**Throughput**
- >2.0 req/sec = Good
- 1.0-2.0 req/sec = Moderate
- <1.0 req/sec = Low

## 📂 Results Files

All results saved in `load_test_results/`:

- `results_TIMESTAMP.csv` - Per-request details
- `summary_TIMESTAMP.json` - Summary statistics
- `resources_TIMESTAMP.csv` - CPU/Memory over time
- `analysis_TIMESTAMP.png` - Charts (if matplotlib installed)

## 🔍 Example Results

```
📊 LOAD TEST SUMMARY
================================================================================
  Total Prompts: 20
  Successful: 20 (100.0%)
  Concurrent Requests: 20
  
  Average Latency: 4.22s
  P95 Latency: 4.55s
  
  CPU Peak: 178.50%
  Memory Peak: 823.45 MB
================================================================================
```


### Recommended Flow
```
Test 1: CONCURRENT_WORKERS = 5   → Baseline
Test 2: CONCURRENT_WORKERS = 10  → Target load
Test 3: CONCURRENT_WORKERS = 20  → Heavy load
Test 4: CONCURRENT_WORKERS = 30  → Stress test
```

## 🎓 What You'll Learn

From running these tests you'll discover:

1. **Optimal Concurrency** - How many concurrent users your system handles well
2. **Resource Limits** - CPU/Memory constraints
3. **Rate Limits** - External API limitations
4. **Performance Degradation** - Where and why performance drops
5. **System Capacity** - Production readiness

## 🤝 Support

For questions or issues:
1. Check [TESTER_INSTRUCTIONS.md](TESTER_INSTRUCTIONS.md)
2. Review [QUICK_REFERENCE.md](QUICK_REFERENCE.md)
3. Consult technical documentation

---

## 📝 Summary

This framework helps you:
- ✅ Test concurrent user load
- ✅ Monitor system resources
- ✅ Measure response latency
- ✅ Find optimal capacity
- ✅ Identify bottlenecks

**Start testing now:** `./quick_test.sh`

**Easiest way for new users:** See [TESTING_QUICKSTART.md](TESTING_QUICKSTART.md)

**Happy Testing! 🚀**
