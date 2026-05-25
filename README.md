# CPI Execution Model

A comprehensive cache performance modeling system for analyzing CPU execution metrics across various cache architectures and policies.

## Overview

This project computes **Cycles Per Instruction (CPI)** execution time and memory access metrics for different cache configurations. It supports analysis of unified/separate caches, write-through/write-back policies, two-level hierarchies, and write buffer scenarios.

## Core Concepts

### Key Metrics

- **AMAT**: Average Memory Access Time = 1 + MemStall
- **MAPI**: Memory Accesses Per Instruction = 1 + %load + %store
- **MemStall**: Expected stall cycles per memory access (varies by cache type)
- **CPI Stall**: MAPI × MemStall
- **CPI Execution**: Ideal CPI + CPI Stall
- **Speedup**: CPI Execution / Ideal CPI

### Cache Types Supported

1. **No Cache** - Every access is a miss
2. **Unified** - Single I/D cache with unified miss rate
3. **Separate** - Split instruction and data caches with different miss rates
4. **Write-Through** - Writes go to both cache and memory immediately
5. **Write-Back** - Dirty blocks written back on eviction
6. **Two-Level** - L1 + L2 cache hierarchy

## Project Structure

### `cpi_model.py`
Core computational engine with the `CPIexecution` class.

**Main Methods:**
- `getCPIexec()` - Compute CPI execution time
- `getAMAT()` - Compute average memory access time
- `getMAPI()` - Compute memory accesses per instruction
- `stallMem()` - Compute memory stall per access
- `stallCPI()` - Display cache type, memory stall, and compute CPI stall
- `getEffectiveMissRate()` - Get effective L1 miss rate
- `speedup(exec_cpi)` - Compute speedup vs ideal or another configuration

**Cache Configuration Methods:**
- `no_cache()` - Set to no cache model
- `unified()` - Set to unified cache
- `separate(inst_miss_rate, data_miss_rate, load, store)` - Configure separate caches
- `write_thru(elim_frac, write_buffer_type)` - Configure write-through policy
- `write_back(dirty_frac)` - Configure write-back policy
- `two_level(miss_rate, stall_cycle)` - Configure L1+L2 hierarchy

### `cpi_utils.py`
Utility functions for analysis and reporting.

**Functions:**
- `print_summary(tag, obj, show_stall_metrics)` - Print formatted metrics summary
- `print_write_buffer_scenarios(obj)` - Analyze PWB, RWB, NWB scenarios

### `cpi_tests.py`
Test suite with comprehensive cache configuration scenarios.

**Function:**
- `run_tests()` - Execute full test suite across different configurations

### `CPI.py`
Entry point for running the test suite.

## Usage

### Running Tests
```bash
python CPI.py
```

### Creating and Analyzing a Cache Model

```python
from cpi_model import CPIexecution

# Initialize model
cpi = CPIexecution(
    ideal_cpi=1.25,
    l1_miss_rate=0.08,
    percent_list=[0.2, 0.25],    # [%load, %store]
    miss_penalty=100,
    l1_stall_cycle=1,
    fetch_cycle=1
)

# Configure unified cache
cpi.unified()
print(f"CPI Execution: {cpi.getCPIexec():.4f}")
print(f"AMAT: {cpi.getAMAT():.4f} cycles")
print(f"Speedup: {cpi.speedup():.4f}x")

# Display stall computation
cpi.stallCPI()  # Prints cache type, calculated values, and memory stall

# Switch to separate caches
cpi.separate(inst_miss_rate=0.05, data_miss_rate=0.09)
print(f"CPI with Separate: {cpi.getCPIexec():.4f}")

# Compare speedup
print(f"Speedup vs Ideal: {cpi.speedup():.4f}x")
```

### Analyzing Write Buffer Scenarios

```python
from cpi_model import CPIexecution
from cpi_utils import print_write_buffer_scenarios

cpi = CPIexecution(1.25, 0.08, [0.2, 0.25], 100)
cpi.write_thru(elim_frac=0.8)
print_write_buffer_scenarios(cpi)  # Shows PWB, RWB, NWB comparisons
```

### Analyzing Two-Level Cache

```python
from cpi_model import CPIexecution

cpi = CPIexecution(1.25, 0.08, [0.2, 0.25], 100)
cpi.two_level(miss_rate=0.4, stall_cycle=4.0)
print(f"L1+L2 CPI: {cpi.getCPIexec():.4f}")
print(f"L1+L2 AMAT: {cpi.getAMAT():.4f}")
```

## Model Formulas

### Memory Stall Calculations

**Unified Cache:**
```
MemStall = m1 × M
```

**Separate I/D Cache:**
```
MemStall = (%inst × Im1 + %data × Dm1) × M
```
where %inst = 1/MAPI, %data = (%load + %store)/MAPI

**Write-Through (with write elimination):**
```
MemStall = (%read × m1 + %write × (1 - %elim)) × M
```
where %read = (1 + %load)/MAPI, %write = %store/MAPI

Note: For write-through scenarios, `print_write_buffer_scenarios()` compares:
- Perfect Write Buffer (PWB): Only reads stall
- Realistic Write Buffer (RWB): Controlled write stalls
- No Write Buffer (NWB): All writes stall

**Write-Back:**
```
MemStall = m1 × (%clean + 2×%dirty) × M
```

**Two-Level Cache:**
```
MemStall = m1 × (h2×T2 + m2×M)
```
where T2 = L2_access_time - 1, h2 = 1 - m2 (L2 hit rate)

## Implementation Details

### Attribute Structure

```
CPIexecution
├── ideal_cpi: float              # Ideal CPI (no memory stalls)
├── miss_rate: dict               # Miss rates by cache level
│   ├── L1: float                 # L1 miss rate
│   ├── L2: float                 # (two-level only)
│   ├── instruction: float        # (separate only)
│   └── data: float               # (separate only)
├── percent: dict                 # Fractions
│   ├── load: float               # % load instructions
│   ├── store: float              # % store instructions
│   ├── elim_frac: float          # (write-through only)
│   ├── dirty_frac: float         # (write-back only)
│   ├── clean_frac: float         # (write-back only)
│   └── h2: float                 # (two-level only)
├── miss_penalty: float           # Main memory miss penalty (cycles)
├── stall_cycle: dict             # Stall cycles by cache level
│   ├── L1: float
│   └── L2_access: float          # (two-level only)
├── typ: str                      # Current cache type
├── exec_cpi: float               # Cached execution CPI
├── ideal_CPI: property           # Alias for ideal_cpi
└── exec_CPI: property            # Alias for exec_cpi
```

## Output Example

```
cache type: unified
cpi_stall = 1.5 * 0.08 * 100 = 12.0
memory stall: 8.0

CPI Execution: 13.25
AMAT: 9.0 cycles
MAPI: 1.45 accesses/instr
Speedup: 10.6x (vs ideal)
```

## Error Handling

- Division by zero returns `float('inf')`
- Invalid cache types default to 0 MemStall
- Missing dictionary keys default to 0.0
- All inputs converted to float automatically

# Configure cache type
cpi.unified()

# Get metrics
print(f"CPI Execution: {cpi.getCPIexec()}")
print(f"AMAT: {cpi.getAMAT()}")
print(f"Speedup: {cpi.speedup()}")
```

## Benefits of Modular Design

1. **Separation of Concerns** - Core model logic is isolated from utilities and tests
2. **Reusability** - Easy to import just the model class in other projects
3. **Maintainability** - Easier to locate and modify specific functionality
4. **Testability** - Utilities and tests are independently verifiable
5. **Readability** - Each file has a clear, focused purpose

## Cache Types Supported

- **No Cache** - Baseline with 100% miss rate
- **Unified Cache** - Single cache for all accesses
- **Separate Cache** - Separate instruction and data caches
- **Write-Through** - Write-through cache policy
- **Write-Back** - Write-back cache policy
- **Two-Level** - L1 and L2 cache hierarchy
