"""Render chart PDFs through a grayscale print simulation for visual review."""
from pathlib import Path
import fitz

ROOT = Path(__file__).resolve().parents[1]

def main():
    folder = ROOT / 'reports/chart-sheets/grayscale'
    folder.mkdir(parents=True, exist_ok=True)
    sources = sorted((ROOT / 'figures').glob('ch*/fig-*.pdf'))
    sheets = fitz.open()
    for start in range(0, len(sources), 12):
        page = sheets.new_page(width=960, height=1000)
        for slot, source in enumerate(sources[start:start+12]):
            x, y = (slot % 3)*320, (slot // 3)*250
            page.insert_text((x+8, y+14), source.stem, fontsize=10)
            with fitz.open(source) as figure:
                page.show_pdf_page(fitz.Rect(x+5, y+24, x+315, y+245), figure, 0)
        page.get_pixmap(matrix=fitz.Matrix(1.5, 1.5), colorspace=fitz.csGRAY).save(
            folder / f'charts-{start//12+1:02d}.png')
    print(f'Rendered {len(sources)} figures in grayscale across {len(sheets)} sheets.')

if __name__ == '__main__':
    main()
