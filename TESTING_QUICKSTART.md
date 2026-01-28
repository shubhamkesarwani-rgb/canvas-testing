# Quick Start - For New Testers

## The Easiest Way to Run Load Tests

### Step 1: Open Terminal
```bash
cd /Users/shubhamkesarwani/projects/concurrency_testing
```

### Step 2: Run the Test

**Default (20 workers, 3 iterations = 60 requests):**
```bash
./quick_test.sh
```

**Custom configuration:**
```bash
./quick_test.sh [workers] [iterations]
```

**Examples:**
```bash
./quick_test.sh 10 5     # 10 workers, 5 iterations = 50 requests
./quick_test.sh 5 2      # 5 workers, 2 iterations = 10 requests (light)
./quick_test.sh 30 3     # 30 workers, 3 iterations = 90 requests (stress)
```

That's it! 🎉

---

## What Happens

The script will:
1. ✅ Check if required packages are installed
2. ✅ Install any missing packages automatically
3. ✅ Run the load test with configured settings
4. ✅ Show results in real-time
5. ✅ Generate visualizations (charts)
6. ✅ Save everything to `load_test_results/`

**Total time:** About 10-20 seconds

---

## If You Get "Permission Denied"

Run this once:
```bash
chmod +x quick_test.sh
```

Then run the test again:
```bash
./quick_test.sh
```

**Or simply:**
```bash
bash quick_test.sh
```

---

## Changing Configuration

### Easy Way (Recommended)
Just pass numbers when running the script:
```bash
./quick_test.sh [workers] [iterations]
```

**Examples:**
```bash
./quick_test.sh 10 5     # 10 workers × 5 iterations = 50 requests
./quick_test.sh 5 2      # 5 workers × 2 iterations = 10 requests
```

### Alternative Way
Edit `load_test_wrapper.py` lines 481-482:
```python
CONCURRENT_WORKERS = 20  # Default if not specified on command line
ITERATIONS = 3           # Default if not specified on command line
```

---

## Understanding Your Results

After the test completes, you'll see:

### Success Rate
```
Successful: 20 (100.0%)
```
- **100%** = Perfect! ✅
- **95-99%** = Good ✅
- **<95%** = Problem ❌

### Latency
```
Average: 4.22s
P95: 4.55s
```
- **P95 < 8 seconds** = Good ✅
- **P95 > 12 seconds** = Problem ❌

### CPU Usage
```
Peak: 178.50%
```
- **<180%** = Good ✅ (your pod has 2 cores = 200% max)
- **>190%** = Near limit ⚠️

---

## Where Are My Results?

All saved in `load_test_results/` folder:
- `results_*.csv` - Open in Excel to see all details
- `summary_*.json` - Summary statistics
- `analysis_*.png` - Charts (if created)

---

## Common Test Values

| Value | What it tests |
|-------|---------------|
| `CONCURRENT_WORKERS = 5` | Light load |
| `CONCURRENT_WORKERS = 10` | Normal load |
| `CONCURRENT_WORKERS = 20` | Heavy load |
| `CONCURRENT_WORKERS = 30` | Stress test |

Start with **5**, then increase to **10**, **20**, etc.

---

## Need More Help?

📖 **Full Instructions:** Read `TESTER_INSTRUCTIONS.md`  
📋 **Quick Reference:** See `QUICK_REFERENCE.md`  
❓ **Troubleshooting:** Check the Troubleshooting section in `TESTER_INSTRUCTIONS.md`

---

**Happy Testing! 🚀**

The quickest way: `./quick_test.sh`
