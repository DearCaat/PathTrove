# PathTrove Data-Source Report Example: TCGA

> **Data-Source Report Sample** · [中文版本](./TCGA_source_report.md)  
> This sample demonstrates PathTrove's systematic organization of upstream data architectures, project scales, pathology modalities, and access conditions for The Cancer Genome Atlas (TCGA).  
> 
> *Note: This is a representative demonstration of the schema and format, not the final complete release.*

## Usage notice

This data-source report sample is governed by the [PathTrove Research Use Terms](../TERMS_OF_USE.md) and is excluded from the repository-wide CC BY 4.0 documentation license.

---

## 1. Source Overview

- **Official Name**: The Cancer Genome Atlas (TCGA)
- **Supporting Bodies**: National Cancer Institute (NCI) and National Human Genome Research Institute (NHGRI)
- **Scope**: 33 cancer projects across more than 20 major anatomical sites
- **Primary Distribution**: NCI Genomic Data Commons (GDC) Data Portal; downstream portals include cBioPortal PanCancer Atlas and UCSC Xena
- **Role in Computational Pathology**: Major source for multi-omics and digital pathology research. Selected projects include SVS whole-slide images (WSIs). Project-level data does not provide standardized single-task labels or official benchmark splits.

---

## 2. Sources and Access

| Item | Details |
| :--- | :--- |
| **Official Portal** | GDC Data Portal (`portal.gdc.cancer.gov`) |
| **Access Model** | Tiered access: Open Access versus Controlled Access |
| **Pathology Images** | Diagnostic Slides (DX) and Tissue Slides (TS) WSIs are **Open Access** and can be downloaded without dbGaP approval |
| **Controlled Content** | Germline variants, unmasked mutations, and raw sequencing BAM files require dbGaP authorization |

---

## 3. Project Composition and Scale (Current GDC Release Snapshot)

TCGA covers 33 project sub-cohorts, totaling 11,428 cases and 30,326 whole-slide images (Slide Images). Key representative projects include:

| Project ID | Primary Cancer / Anatomical Site | Cases | Slide Images (SVS) |
| :--- | :--- | :--- | :--- |
| **TCGA-BRCA** | Breast Invasive Carcinoma (Breast) | 1,098 | 2,132 |
| **TCGA-LUAD** | Lung Adenocarcinoma (Lung) | 585 | 1,063 |
| **TCGA-LUSC** | Lung Squamous Cell Carcinoma (Lung) | 504 | 1,046 |
| **TCGA-COAD** | Colon Adenocarcinoma (Colorectum) | 460 | 973 |
| **TCGA-READ** | Rectum Adenocarcinoma (Colorectum) | 171 | 374 |
| **TCGA-GBM** | Glioblastoma Multiforme (Brain) | 617 | 1,061 |
| **TCGA-OV** | Ovarian Serous Cystadenocarcinoma (Ovary) | 585 | 1,098 |
| **TCGA-KIRC** | Kidney Renal Clear Cell Carcinoma (Kidney) | 537 | 1,023 |

> **Cohort Caveat**: The counts above reflect dynamic project totals under the current GDC release. Numbers reported in original project marker papers reflect specific historical frozen cohorts and differ from current GDC inventories; each should be cited with its corresponding version.

---

## 4. Pathology Modalities and Imaging Structure

1. **Slide Image Types**:
   - **DX (Diagnostic Slides)**: Formalin-fixed paraffin-embedded (FFPE) routine diagnostic slides with preserved tissue architecture, serving as the primary choice for computational pathology;
   - **TS (Tissue Slides)**: Frozen section slides with visible freezing artifacts, primarily used during tissue quality control.
2. **Multimodal Pairing**:
   Most cases include matched whole-exome sequencing, RNA-seq, DNA methylation, and structured clinical follow-up, forming the standard benchmark foundation for weakly supervised pathogenomics and survival modeling.

---

## 5. Recommended Workflow and Validation Rules

1. **Confirm Scope**: Query projects and file availability through the GDC Data Portal or API;
2. **Acquire Manifest**: Export official manifest files specifying target filters (e.g., DX slides only, primary tumor);
3. **Patient-Level Splits**: A single TCGA case frequently includes multiple slides or repeat biopsies. Splits must be partitioned strictly by 12-character Case Barcode (e.g. `TCGA-XX-XXXX`) to prevent data leakage between training and testing folds.
