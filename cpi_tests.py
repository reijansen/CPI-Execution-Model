try:
    from .cpi_model import CPIexecution
    from .cpi_utils import print_summary, print_write_buffer_scenarios
except ImportError:
    from cpi_model import CPIexecution
    from cpi_utils import print_summary, print_write_buffer_scenarios


def run_tests():
    cpi = CPIexecution(
        ideal_cpi=1.25,
        l1_miss_rate=0.08,
        percent_list=[0.2, 0.25],
        miss_penalty=100,
        l1_stall_cycle=1,
        fetch_cycle=1
    )

    print("\n" + "="*70)
    print("CPI EXECUTION MODEL - COMPREHENSIVE TEST SUITE".center(70))
    print("="*70 + "\n")

    groups = [
        (100.0, "No Policy (no cache / unified / separate)"),
        (150.0, "With Policy (write-back / write-through / buffers)"),
        (200.0, "Two-Level Cache (L1+L2)")
    ]

    baseline_load = cpi.percent.get('load', 0.0)
    baseline_store = cpi.percent.get('store', 0.0)

    for penalty, label in groups:
        cpi.percent['load'] = baseline_load
        cpi.percent['store'] = baseline_store

        print(f"\n-- {label} [Miss Penalty: {penalty}] --\n")

        if penalty not in [150.0, 200.0]:
            cpi.miss_penalty = penalty
            cpi.no_cache()
            print_summary(f"No Cache", cpi)

            cpi.miss_penalty = penalty
            cpi.unified()
            print_summary(f"Unified Cache", cpi)

            cpi.miss_penalty = penalty
            cpi.separate(inst_miss_rate=0.05, data_miss_rate=0.10, load=0.2, store=0.25)
            print_summary(f"Separate I/D Cache", cpi)

        if penalty == 150.0:
            cpi.miss_penalty = penalty
            cpi.write_back(dirty_frac=0.1)
            print_summary(f"Write-Back Cache", cpi)

            cpi.miss_penalty = penalty
            cpi.write_thru(elim_frac=0.8, write_buffer_type="realistic write buffer")
            print_summary(f"Write-Through + Realistic Buffer", cpi, show_stall_metrics=False)

            print("\n-- Write Buffer Comparison --")
            print_write_buffer_scenarios(cpi)

        if penalty == 200.0:
            cpi.miss_penalty = penalty
            cpi.two_level(miss_rate=0.4, stall_cycle=3.0)
            print_summary(f"Two-Level Cache (L1 + L2)", cpi)

    print("\n" + "="*70)
    print("ALL TESTS COMPLETED SUCCESSFULLY".center(70))
    print("="*70 + "\n")


if __name__ == "__main__":
    run_tests()