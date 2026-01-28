#!/bin/bash
# Quick Load Test Runner
# Usage: ./quick_test.sh [concurrent_workers] [iterations]
#
# Examples:
#   ./quick_test.sh              # Use defaults (20 workers, 3 iterations)
#   ./quick_test.sh 10 5         # 10 workers, 5 iterations
#   ./quick_test.sh 5 2          # 5 workers, 2 iterations (light test)

echo "🚀 Quick Load Test Runner"
echo "========================="

# Parse arguments with defaults
WORKERS=${1:-20}
ITERATIONS=${2:-1}

echo "Configuration:"
echo "  Concurrent Workers: $WORKERS"
echo "  Iterations: $ITERATIONS"
echo "  Total Requests: $((WORKERS * ITERATIONS))"
echo ""

# Check dependencies
echo "Checking dependencies..."
python3 -c "import psutil" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "⚠️  Installing psutil..."
    pip install psutil
fi

python3 -c "import requests" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "⚠️  Installing requests..."
    pip install requests
fi

echo "✅ Dependencies OK"
echo ""

# Run load test with arguments
echo "Starting load test..."
python3 load_test_wrapper.py --workers $WORKERS --iterations $ITERATIONS

# Check if visualization is possible
echo ""
echo "Generating analysis..."
python3 -c "import matplotlib" 2>/dev/null
if [ $? -eq 0 ]; then
    python3 visualize_load_test.py
else
    echo "⚠️  matplotlib not installed. Skipping visualizations."
    echo "   Install with: pip install matplotlib"
fi

echo ""
echo "✅ Test complete!"
echo "📂 Results saved in: load_test_results/"
