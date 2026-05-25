try:
    from .cpi_model import CPIexecution
    from .cpi_tests import run_tests
except ImportError:
    from cpi_model import CPIexecution
    from cpi_tests import run_tests

__all__ = ['CPIexecution', 'run_tests']


if __name__ == "__main__":
    run_tests()