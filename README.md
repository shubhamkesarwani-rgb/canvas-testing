# Concurrent Load Testing for Rule Processor Agent

Complete framework for testing how your Rule Processor Agent handles concurrent user load.

## 🚀 Quick Start for Testers

**Brand new?** Ultra-quick guide: **[TESTING_QUICKSTART.md](TESTING_QUICKSTART.md)** ⚡  
Just want to run the test? This is for you!

**Need full instructions?** Complete guide: **[TESTER_INSTRUCTIONS.md](TESTER_INSTRUCTIONS.md)** 📖  
Step-by-step guide with detailed explanations.

**Already familiar?** Quick reference: **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** 📋  
One-page cheat sheet for quick testing.

## 📚 Documentation

### For Testers
- **[TESTING_QUICKSTART.md](TESTING_QUICKSTART.md)** ⭐ - Ultra-fast start
  - Absolute quickest way to get started
  - Two commands: navigate + run
  - Perfect for first-time users
  
- **[TESTER_INSTRUCTIONS.md](TESTER_INSTRUCTIONS.md)** - Complete testing guide
  - How to run tests using quick_test.sh
  - How to change concurrent requests
  - Detailed results interpretation
  - Troubleshooting
  
- **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** - Quick reference card
  - Commands at a glance
  - Metrics interpretation
  - Troubleshooting table

### For Technical Users
- **[ITERATIONS_GUIDE.md](ITERATIONS_GUIDE.md)** ⭐ NEW! - Sustained load with iterations
  - What iterations are and why use them
  - Detecting performance degradation
  - Finding memory leaks
  - Example configurations
  
- **[CONCURRENT_LOAD_TEST_GUIDE.md](CONCURRENT_LOAD_TEST_GUIDE.md)** - Technical deep dive
  - How concurrent testing works
  - Threading vs multiprocessing
  - System behavior analysis
  
- **[20_USER_CONCURRENCY_TEST.md](20_USER_CONCURRENCY_TEST.md)** - 20-user test guide
  - Specific guidance for 20 concurrent users
  - Performance targets
  - Troubleshooting scenarios

- **[LOAD_TEST_README.md](LOAD_TEST_README.md)** - Original framework docs
  - Complete feature list
  - Advanced configuration
  - Architecture details

### Technical References
- **[FIX_SUMMARY.md](FIX_SUMMARY.md)** - Import issue fix documentation
- **[TESTING_SETUP_SUMMARY.md](TESTING_SETUP_SUMMARY.md)** - Setup guide

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

### Advanced Configuration
Edit defaults in `load_test_wrapper.py` or use Python directly:

```bash
python load_test_wrapper.py --workers 20 --iterations 3
python load_test_wrapper.py -w 10 -i 5
python load_test_wrapper.py --help  # See all options
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

## 🛠️ Troubleshooting

| Issue | Solution |
|-------|----------|
| Module not found | `pip install -r load_test_requirements.txt` |
| CSV file not found | Ensure you're in correct directory |
| All requests fail | Check network/API status |
| High latency | Reduce concurrent requests |

## 📖 Where to Start

1. **New testers**: Read [TESTING_QUICKSTART.md](TESTING_QUICKSTART.md) ⚡
2. **Run test**: Execute `./quick_test.sh`
3. **Need details**: Read [TESTER_INSTRUCTIONS.md](TESTER_INSTRUCTIONS.md)
4. **Quick lookup**: Use [QUICK_REFERENCE.md](QUICK_REFERENCE.md)
5. **Technical deep dive**: Read [CONCURRENT_LOAD_TEST_GUIDE.md](CONCURRENT_LOAD_TEST_GUIDE.md)

## 💡 Testing Strategy

### Progressive Testing
1. **Start small**: Test with 5 concurrent requests
2. **Increase gradually**: 10, then 20, then 30
3. **Find sweet spot**: Where performance is good
4. **Find breaking point**: Where it starts failing
5. **Document findings**: Record optimal concurrency

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
