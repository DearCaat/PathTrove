# PathTrove Download Guide Example: Ovarian-Bevacizumab-Response

> **Download Guide Sample** · [中文版本](./Ovarian-Bev_download_guide.md)  
> This sample demonstrates PathTrove's tested download and verification guide for public data (TCIA), verified in practical network environments.  
> 
> *Note: This is a representative demonstration of the schema and format, not the final complete release.*

## Usage notice

This download guide sample is governed by the [PathTrove Research Use Terms](../TERMS_OF_USE.md) and is excluded from the repository-wide CC BY 4.0 documentation license.

---

## 1. Overview

- **Dataset Name**: Ovarian-Bevacizumab-Response (Ovarian cancer bevacizumab response)
- **Data Volume**: 286 H&E whole-slide images (WSI, approx. 253.8 GB) from 78 patients
- **License**: CC BY 4.0 (hosted on TCIA)
- **Access Route**: Fully open access; no login, approval, or data-use agreement required

> **Cohort Note**: The official portal page and original paper describe 288 slides (162 effective, 126 invalid). TCIA Version 2 officially removed slides `414056O.svs` and `414056P.svs`, leaving 286 slides (160 effective, 126 invalid).

---

## 2. File Inventory and Acquisition Methods

| File | Description | Size | Acquisition Route |
| :--- | :--- | :--- | :--- |
| **Pathology WSIs** | 286 `.svs` files; H&E stained, 20× magnification (0.5 µm/px) | ~253.8 GB | High-speed bulk transfer via Aspera CLI (`ascli`) |
| `new_CA125-data_20230207.xlsx` | Slide-level response labels (effective / invalid) and pre/post CA-125 | 26 KB | Direct HTTP download via `curl` |
| `Final-patient_list.xlsx` | Clinical features (age, FIGO stage, therapy, surgery, follow-up) | 18 KB | Direct HTTP download via `curl` |
| Slide manifest CSV | Slide-to-patient barcode mapping list | 18 KB | Direct HTTP download via `curl` |

---

## 3. Direct Table Downloads (curl Example)

Small clinical and label tables can be downloaded directly over HTTP:

```bash
# Download label and CA-125 spreadsheet
curl -fL -o new_CA125-data_20230207.xlsx \
  "https://public.cancerimagingarchive.net/nbia-api/services/v1/download?manifestUrl=..."

# Download patient clinical info
curl -fL -o Final-patient_list.xlsx \
  "https://public.cancerimagingarchive.net/nbia-api/services/v1/download?manifestUrl=..."
```

---

## 4. Bulk Slide Download (Aspera ascli Command-Line Route)

TCIA WSI packages are distributed via IBM Aspera. To support headless server environments, PathTrove standardized on the official Aspera CLI (`ascli`):

```bash
# 1. Configure Aspera credentials and bypass local key prompts
ascli conf global set bypass_keys=true

# 2. Download the package (set transfer rate with --ts to avoid throttling)
ascli faspex packages download \
  --url "https://faspex.cancerimagingarchive.net" \
  --user "guest" \
  --package-id "..." \
  --ts "200m" \
  --to-folder "./ovarian_bev_wsi/"
```

*Tested notes*:
1. Rerunning the command automatically resumes interrupted transfers;
2. After download, verify file integrity against official hashes using `md5sum -c *.sums`.

---

## 5. Table-to-Slide Mapping and Edge Cases

- **Identifier Alignment**: The `Image No.` column in the label table corresponds directly to the slide filename (e.g. `1612595C.svs`).
- **Patient Mapping**: Five slides have minor naming discrepancies in official tables (e.g., casing or trailing whitespace); all have been verified and mapped to consistent patient IDs.
- **Conflict Handling**: Controversial slides with ambiguous records across official sheets are isolated into an excluded list and withheld from benchmark splits to prevent label leakage.
