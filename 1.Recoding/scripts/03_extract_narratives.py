"""Extract per-trip narratives from the 4 .docx files.
Splits on lines beginning with 'ID' (e.g. 'ID : #Psilocybe_01').
Writes one plain-text file per trip into data/trips/<trip_id>.txt plus an index CSV.
"""
import os, re, csv
import docx

PROJECT_ROOT = "../.."
DOCX_FILES = [
    ("psilocybin", "Psilocybin_source_coding/Psilocybe_01-10.docx"),
    ("psilocybin", "Psilocybin_source_coding/Psilocybe_11-20.docx"),
    ("brugmansia", "Brugmansia_source_coding/Brugmansia_01-10.docx"),
    ("brugmansia", "Brugmansia_source_coding/Brugmansia_11-20.docx"),
]
OUT_DIR = "../data/trips"
INDEX_OUT = "../data/trips_index.csv"

ID_RE = re.compile(r"^\s*ID\s*:?\s*#?\s*(\w+_\d+)\s*$", re.IGNORECASE)
DOSE_RE = re.compile(r"^\s*Dose\s*:?\s*(.*)$", re.IGNORECASE)


def parse_docx(path):
    """Return list of (trip_id, dose, narrative_text)."""
    d = docx.Document(path)
    lines = [p.text for p in d.paragraphs]
    trips = []
    cur_id = None
    cur_dose = None
    cur_buf = []
    for ln in lines:
        m = ID_RE.match(ln)
        if m:
            # flush previous
            if cur_id is not None:
                trips.append((cur_id, cur_dose, "\n".join(cur_buf).strip()))
            cur_id = m.group(1)
            # normalise: some docx have lowercase 'brugmansia', etc.
            cur_id = cur_id[0].upper() + cur_id[1:]
            # Psilocybe / Brugmansia with trailing _NN → ensure 2-digit padding
            parts = cur_id.split('_')
            if len(parts) == 2 and parts[1].isdigit():
                cur_id = f"{parts[0]}_{int(parts[1]):02d}"
            cur_dose = None
            cur_buf = []
            continue
        m2 = DOSE_RE.match(ln)
        if m2 and cur_id is not None and not cur_buf:
            cur_dose = m2.group(1).strip() or None
            continue
        if cur_id is not None:
            cur_buf.append(ln)
    if cur_id is not None:
        trips.append((cur_id, cur_dose, "\n".join(cur_buf).strip()))
    return trips


def main():
    here = os.path.dirname(__file__)
    outdir = os.path.join(here, OUT_DIR)
    os.makedirs(outdir, exist_ok=True)
    index_rows = []
    for substance, path in DOCX_FILES:
        full = os.path.join(here, PROJECT_ROOT, path)
        trips = parse_docx(full)
        for tid, dose, text in trips:
            wc = len(text.split())
            out_path = os.path.join(outdir, f"{tid}.txt")
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(text)
            index_rows.append({"trip_id": tid, "substance": substance,
                               "dose_raw": dose, "word_count": wc,
                               "source_docx": path})
            print(f"  {tid}: dose={dose} words={wc}")
    with open(os.path.join(here, INDEX_OUT), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["trip_id","substance","dose_raw","word_count","source_docx"])
        w.writeheader()
        for r in index_rows:
            w.writerow(r)
    print(f"\nwrote {len(index_rows)} trips + index")


if __name__ == "__main__":
    main()
