try:
    from .cpi_model import CPIexecution
except ImportError:
    from cpi_model import CPIexecution


def _print_header(title, width=68, char="="):
    line = char * width
    print(line)
    print(title.center(width))
    print(line)


def _print_row(label, value, label_width=20):
    print(f"{label:<{label_width}}: {value}")


def print_summary(tag, obj: CPIexecution, show_stall_metrics=True):
    print()
    _print_header(tag)
    _print_row("Type", obj.getType())
    _print_row("AMAT", f"{obj.getAMAT():.4f} cycles")
    _print_row("MAPI", f"{obj.getMAPI():.4f} accesses/instr")
    _print_row("MemStall", f"{obj.stallMem():.4f} cycles/access")
    if show_stall_metrics:
        _print_row("CPI Stall", f"{obj.stallCPI():.4f}")
        _print_row("CPI Execution", f"{obj.getCPIexec():.4f}")
        _print_row("Speedup", f"{obj.speedup():.4f}x")
    print()


def print_write_buffer_scenarios(obj: CPIexecution):
    load = float(obj.percent.get("load", 0.0))
    store = float(obj.percent.get("store", 0.0))
    m1 = float(obj.miss_rate.get("L1", 0.0))
    M = float(obj.miss_penalty)
    mapi = float(obj.getMAPI())
    elim = float(obj.percent.get("elim_frac", 0.0))

    pct_read = (1.0 + load) / mapi
    pct_write = store / mapi

    def _scenario(title, memstall):
        cpi_stall = mapi * memstall
        cpi_exec = float(obj.ideal_cpi) + cpi_stall
        speedup = cpi_exec / float(obj.ideal_cpi) if float(obj.ideal_cpi) != 0 else float("inf")

        print()
        _print_header(title, width=68, char="-")
        _print_row("m1", f"{m1:.4f}")
        _print_row("M", f"{M:.2f}")
        _print_row("%load", f"{load:.4f}")
        _print_row("%store", f"{store:.4f}")
        _print_row("%elim", f"{elim:.4f}")
        _print_row("%read", f"{pct_read:.6f}")
        _print_row("%write", f"{pct_write:.6f}")
        _print_row("MemStall", f"{memstall:.6f} cycles/access")
        _print_row("CPIStall", f"{mapi:.6f} * {memstall:.6f} = {cpi_stall:.6f}")
        _print_row("CPIExec", f"{cpi_exec:.6f}")
        _print_row("Speedup", f"{speedup:.6f}x")

    pwb_memstall = (pct_read * m1) * M
    _scenario("Perfect Write Buffer (PWB)", pwb_memstall)

    rwb_memstall = (pct_read * m1 + pct_write * (1.0 - elim)) * M
    _scenario("Realistic Write Buffer (RWB)", rwb_memstall)

    nwb_memstall = (pct_read * m1 + pct_write) * M
    _scenario("No Write Buffer (NWB)", nwb_memstall)