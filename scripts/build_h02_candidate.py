"""Execute the two auditable role-1 notebooks from the repository root."""
from pathlib import Path
import traceback
import nbformat
from nbclient import NotebookClient

ROOT = Path(__file__).resolve().parents[1]
NOTEBOOKS = ['02-role01-order-fact-and-history.ipynb', '03-role01-h02-coverage-features-labels.ipynb']

def main():
    for name in NOTEBOOKS:
        path = ROOT / 'notebooks' / name
        notebook = nbformat.read(path, as_version=4)
        try:
            NotebookClient(notebook, timeout=240, kernel_name='olist312',
                           resources={'metadata': {'path': str(ROOT)}}).execute()
        except Exception:
            log = ROOT / 'outputs/public_learning/H02_build_failure.log'
            log.parent.mkdir(parents=True, exist_ok=True)
            with log.open('a', encoding='utf-8') as stream:
                stream.write(name + '\n' + traceback.format_exc() + '\n')
            raise
        finally:
            nbformat.write(notebook, path)
        print('Executed', name, flush=True)

if __name__ == '__main__':
    main()
