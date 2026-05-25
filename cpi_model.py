class CPIexecution:

    def __init__(self, ideal_cpi, l1_miss_rate, percent_list, miss_penalty,
                 l1_stall_cycle=0, fetch_cycle=1):
        self.ideal_cpi = float(ideal_cpi)
        self.miss_rate = {'L1': float(l1_miss_rate)}
        self.percent = {
            'load': float(percent_list[0]) if len(percent_list) > 0 else 0.0,
            'store': float(percent_list[1]) if len(percent_list) > 1 else 0.0
        }
        self.miss_penalty = float(miss_penalty)
        self.stall_cycle = {'L1': float(l1_stall_cycle)}
        self.fetch_cycle = float(fetch_cycle)
        self.typ = "unified"
        self.exec_cpi = 0.0

    @property
    def ideal_CPI(self):
        return self.ideal_cpi
    
    @property
    def exec_CPI(self):
        return self.exec_cpi

    def _load_store(self):
        return float(self.percent.get("load", 0.0)), float(self.percent.get("store", 0.0))

    def getType(self):
        """Return current cache type."""
        return self.typ

    def setCPIexec(self):
        """Update cached CPI execution value."""
        self.exec_cpi = self.getCPIexec()

    def getCPIexec(self):
        """Compute CPI execution time."""
        return self.ideal_cpi + self.getMAPI() * self.stallMem()

    def getEffectiveMissRate(self):
        """Return effective L1 miss rate."""
        return 1.0 if self.typ == "no cache" else self.miss_rate.get('L1', 0.0)

    def getAMAT(self):
        """Compute average memory access time."""
        return 1.0 + self.stallMem()

    def getMAPI(self):
        """Compute memory accesses per instruction."""
        load, store = self._load_store()
        return 1.0 + load + store

    def stallCPI(self):
        """Print cache type and memory stall, return CPI stall value."""
        memstall = self.stallMem()
        print(f"{'cache type':<20}: {self.typ}")
        print(f"{'memory stall':<20}: {memstall:.4f}")
        return self.getMAPI() * memstall

    def stallMem(self):
        """Calculate and return memstall per memory access for current cache type."""
        M = float(self.miss_penalty)
        load, store = self._load_store()
        mapi = self.getMAPI()

        if self.typ == "no cache":
            memstall = 1.0 * M

        elif self.typ == "unified":
            m1 = float(self.miss_rate.get('L1', 0.0))
            memstall = m1 * M

        elif self.typ == "separate":
            Im1 = float(self.miss_rate.get('instruction', 0.0))
            Dm1 = float(self.miss_rate.get('data', 0.0))
            pct_inst, pct_data = 1.0 / mapi, (load + store) / mapi
            memstall = (pct_inst * Im1 + pct_data * Dm1) * M

        elif self.typ == "write through":
            m1 = float(self.miss_rate.get('L1', 0.0))
            elim = float(self.percent.get('elim_frac', 0.0))
            pct_read, pct_write = (1.0 + load) / mapi, store / mapi
            memstall = (pct_read * m1 + pct_write * (1.0 - elim)) * M

        elif self.typ == "write back":
            m1 = float(self.miss_rate.get('L1', 0.0))
            dirty = float(self.percent.get("dirty_frac", 0.2))
            clean = 1.0 - dirty
            memstall = m1 * (clean + 2.0 * dirty) * M

        elif self.typ == "two level":
            m1 = float(self.miss_rate.get('L1', 0.0))
            m2 = float(self.miss_rate.get('L2', 0.0))
            h2 = float(self.percent.get('h2', 1.0 - m2))
            T2 = max(0.0, float(self.stall_cycle.get('L2_access', 0.0)) - 1.0)
            memstall = m1 * (h2 * T2 + m2 * M)
        else:
            memstall = 0.0

        return memstall

    def speedup(self, exec_cpi="ideal"):
        """Compute speedup vs ideal CPI or other cache configuration."""
        current = self.getCPIexec()
        if current == 0:
            return float('inf')
        if exec_cpi == "ideal":
            return current / self.ideal_cpi if self.ideal_cpi != 0 else float('inf')
        return float(exec_cpi) / current

    def no_cache(self):
        self.typ = "no cache"
        self.setCPIexec()

    def unified(self):
        self.typ = "unified"
        self.setCPIexec()

    def separate(self, inst_miss_rate, data_miss_rate, load=None, store=None):
        self.typ = "separate"
        self.miss_rate['instruction'] = float(inst_miss_rate)
        self.miss_rate['data'] = float(data_miss_rate)
        if load is not None:
            self.percent['load'] = float(load)
        if store is not None:
            self.percent['store'] = float(store)
        self.setCPIexec()

    def write_thru(self, elim_frac=0.0, write_buffer_type="realistic write buffer"):
        self.typ = "write through"
        self.percent['elim_frac'] = float(elim_frac)
        self.percent['write_buffer_type'] = str(write_buffer_type)
        self.setCPIexec()

    def write_back(self, dirty_frac=0.2):
        self.typ = "write back"
        self.percent['dirty_frac'] = float(dirty_frac)
        self.percent['clean_frac'] = 1.0 - float(dirty_frac)
        self.setCPIexec()

    def two_level(self, miss_rate, stall_cycle):
        self.typ = "two level"
        self.miss_rate['L2'] = float(miss_rate)
        self.percent['h2'] = 1.0 - float(miss_rate)
        self.stall_cycle['L2_access'] = float(stall_cycle)
        self.setCPIexec()