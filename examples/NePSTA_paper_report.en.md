# PathTrove Paper Report Example: NePSTA (Nature Cancer, 2025)

> **Paper Report Sample** · [中文版本](./NePSTA_paper_report.md)  
> This sample demonstrates PathTrove's data-centric breakdown of peer-reviewed literature (*Nature Cancer*, 2025), deconstructing 8 tasks, cohort sizes, label sources, and experimental split designs.  
> 
> *Note: This is a representative demonstration of the schema and format, not the final complete release.*

## Usage notice

This paper report sample is governed by the [PathTrove Research Use Terms](../TERMS_OF_USE.md) and is excluded from the repository-wide CC BY 4.0 documentation license.

---

## 1. Study Background and Core Data

- **Paper Title**: *Spatially resolved transcriptomics and graph-based deep learning improve accuracy of routine CNS tumor diagnostics*
- **Journal & Year**: *Nature Cancer*, 2025 (DOI: `10.1038/s43018-024-00904-z`)
- **Primary Cohort**: NePSTA cohort comprising 107 brain tumor samples across 4 German medical centers (Heidelberg 50, Freiburg 41, Mannheim 15, Memmingen 1), profiled with 10x Visium spatial transcriptomics, H&E slides, and EPIC methylation arrays.
- **Openness**: The paper states that the validation cohort is publicly deposited on Zenodo (DOI: `10.5281/zenodo.14064047`); the full training cohort is not openly deposited due to ethics restrictions.

---

## 2. Overview of the 8 Tasks and Split Designs

Before reuse, tasks must be strictly differentiated: **Tasks 1–4 perform quality control and exploratory comparisons without training models; Tasks 5–8 train Graph Isomorphism Networks (GIN) under patient-level data partitions**.

| Task # | Task Name | Cohort & Scale | Label / Ground Truth | Data Partition | Core Metric |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **01** | **Spatial Transcriptomics QC** | 107 NePSTA samples + 11 external controls | No task labels (grouped by processing method) | No split | No significant UMI differences per spot |
| **02** | **Virtual Immunohistochemistry** | 12 participants with adjacent IHC | Consecutive section IHC signal intensity | No split (correlation analysis) | Correlation: Ki67 0.47, NeuN 0.57 |
| **03** | **Copy Number Variation (CNV)** | Participants with methylation array CNV | Methylation-based CNV calls | No split (chromosome-arm stratified) | Overall agreement 81.2%, AUC 80.37% |
| **04** | **Cell Composition & Microenvironment** | All samples + GBMap single-cell atlas | GBMap reference cell signatures | No split | Characterized Mesenchymal immunosuppressive profile |
| **05** | **Tissue Region Segmentation** | Cohort 1 (41 patients) + Cohort 2 (27 patients) | Neuropathologist manual H&E annotations | Patient-level: 41 train, 27 validation | Validation accuracy 87.43% |
| **06** | **Methylation Subclass Classification** | 107 EPIC samples, 97k tumor subgraphs | EPIC array methylation subclass | Patient-level 5-fold cross-validation | Patient-level accuracy 0.893 (subgraph 0.999) |
| **07** | **MGMT Promoter Methylation** | 53 patients with confirmed MGMT | Array MGMT methylation status | Cross-cohort: 30 train, 23 eval | Subgraph accuracy 99%, F1 1.0 |
| **08** | **CDKN2A/B Deletion Detection** | 53 patients with confirmed CDKN2A/B | Array CDKN2A/B status | Cross-cohort: 30 train, 23 eval | Subgraph classification accuracy 85.4% |

---

## 3. Critical Caveats for Reuse and Benchmarking

1. **Publicly Accessible Scope**: Although the study encompasses 107 patients, only the validation cohort (approx. 41 cases) is deposited openly on Zenodo. The actual availability of raw files must be audited before designing training tasks.
2. **Intersection Across Modalities**: Usable sample sizes vary significantly across individual tasks (e.g. only 53 patients have confirmed MGMT array ground truth, and only 12 have paired adjacent IHC). The study's total sample count cannot be assumed as the training size for each task.
3. **Metric Granularity (Subgraph vs. Patient-Level)**: Metrics such as `0.999` in Task 6 and `99%` in Task 7 are computed at the local spot subgraph level; the clinically relevant patient-level accuracy for Task 6 is `0.893`. Benchmarks must not conflate subgraph metrics with case-level diagnostic accuracy.
