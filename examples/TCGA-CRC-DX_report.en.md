# PathTrove Full-Field Dataset Report Example: TCGA-CRC-DX

> **Full-field example / 全字段样例** · [中文版本](./TCGA-CRC-DX_report.md)  
> This example contains all 38 fields in the PathTrove dataset-report contract. Every field is verified directly against primary sources.  
> 
> *Note: This is a representative demonstration of the schema and format, not the final complete release.* / *注：本文件为展示结构与规范的代表性样例，非最终完整版本。*

## Usage notice

This report sample is governed by the [PathTrove Research Use Terms](../TERMS_OF_USE.md) and is excluded from the repository-wide CC BY 4.0 documentation license. It may be viewed, cited, and quoted to a limited extent for non-commercial research. Commercial use or republishing, mirroring, packaging, or redistributing this report or a substantial portion of it requires prior permission from the PathTrove contributors.

The license values recorded in individual fields describe upstream resources; they do not license the PathTrove report itself.

---

## Executive Summary

On Zenodo, CRC-MSI is formally named TCGA-CRC-DX (record 3832231, titled “Histological image tiles for TCGA-CRC-DX, color-normalized, sorted by MSI status, train/test split”). Tiles are cut from the tumor regions of TCGA colorectal cancer H&E whole-slide images for microsatellite instability (MSI) classification, released as two archives, TRAIN.zip and TEST.zip. Each tile covers 256 μm, is saved at 512 × 512 pixels (0.5 μm/pixel) and is color-normalized; every tile inherits its patient's MSI status. Counted from the archive file listings, there are 423 patients, 428 slides and 51,918 tiles.

---

## Basic record

### Dataset name

**Value**: `TCGA-CRC-DX`

Both the Zenodo title and the README of the official DeepHistology repository use TCGA-CRC-DX. CRC-MSI is an alias used for the MSI task, not the official name.

> **Source**: SourceZenodo record 3832231 · title / page title  
> *""Histological image tiles for TCGA-CRC-DX, color-normalized, sorted by MSI status, train/test split""*

### Resource type

**Value**: `Dataset`

Zenodo registers it as a dataset; it has none of the submission portal, leaderboard, hidden test labels or evaluation protocol a challenge or benchmark would have.

> **Source**: SourceZenodo API record 3832231 · metadata.resource_type / status  
> *""resource_type": {"title": "Dataset", "type": "dataset"}"; ""status": "published"""*

### Release date

**Value**: `2020-05`

The Zenodo release date, 2020-05-18, is used. The related paper was published in October 2020 and is not taken as the data release date.

> **Source**: SourceZenodo API record 3832231 · metadata.publication_date  
> *""publication_date": "2020-05-18"""*

### Dataset homepage

**Value**: `https://zenodo.org/records/3832231`

DOI 10.5281/zenodo.3832231 points to the same record.

> **Source**: SourceZenodo record 3832231 · canonical / citation_abstract_html_url  
> *""https://zenodo.org/records/3832231""*

### Access status

**Value**: `Fully open`

Zenodo marks it as open access; TRAIN.zip and TEST.zip can both be downloaded directly, without approval, registration or a data use agreement.

> **Source**: SourceZenodo API record 3832231 · metadata.access_right / files  
> *""access_right": "open""; ""key": "TEST.zip""; ""key": "TRAIN.zip"""*

### Access notes

The public content is the two archives TRAIN.zip and TEST.zip. The data license is CC BY 4.0; the accompanying DeepHistology code repository uses the MIT license, which covers only the code.

> **Source**: SourceZenodo record 3832231 / Zenodo API record 3832231 / GitHub API jnkather/DeepHistology · rights / access status / license  
> *""The record and files are publicly accessible."; ""license": {"id": "cc-by-4.0"}"; ""name": "MIT License"""*

### Paper title

**Value**: `Clinical-Grade Detection of Microsatellite Instability in Colorectal Tumors by Deep Learning`

The titles recorded by the DOI, PubMed and PMC agree.

> **Source**: SourcePubMed metadata / DOI metadata · TI / title  
> *""Clinical-Grade Detection of Microsatellite Instability in Colorectal Tumors by Deep Learning.""*

### Paper link

**Value**: `https://doi.org/10.1053/j.gastro.2020.06.021`

The DOI is the main entry point and can be cross-checked against the PubMed and PMC pages.

> **Source**: SourcePubMed metadata · LID  
> *""10.1053/j.gastro.2020.06.021 [doi]""*

### Download link

**Value**: `https://zenodo.org/records/3832231`

Direct addresses of the two archives: https://zenodo.org/api/records/3832231/files/TRAIN.zip/content and https://zenodo.org/api/records/3832231/files/TEST.zip/content.

> **Source**: SourceZenodo API record 3832231 · files / links.self_html  
> *""links": {"self_html": "https://zenodo.org/records/3832231"}"; ""key": "TRAIN.zip""; ""key": "TEST.zip"""*

### Citation

```
@article{Echle_2020, title={Clinical-Grade Detection of Microsatellite Instability in Colorectal Tumors by Deep Learning}, volume={159}, ISSN={0016-5085}, url={http://dx.doi.org/10.1053/j.gastro.2020.06.021}, DOI={10.1053/j.gastro.2020.06.021}, number={4}, journal={Gastroenterology}, publisher={Elsevier BV}, author={Echle, Amelie and Grabsch, Heike Irmgard and Quirke, Philip and van den Brandt, Piet A. and West, Nicholas P. and Hutchins, Gordon G.A. and Heij, Lara R. and Tan, Xiuxiang and Richman, Susan D. and Krause, Jeremias and Alwers, Elizabeth and Jenniskens, Josien and Offermans, Kelly and Gray, Richard and Brenner, Hermann and Chang-Claude, Jenny and Trautwein, Christian and Pearson, Alexander T. and Boor, Peter and Luedde, Tom and Gaisa, Nadine Therese and Hoffmeister, Michael and Kather, Jakob Nikolas}, year={2020}, month=Oct, pages={1406–1416.e11} }
```

The formal BibTeX returned by the DOI.

> **Source**: SourceDOI content negotiation · application/x-bibtex  
> *""@article{Echle_2020, title={Clinical-Grade Detection of Microsatellite Instability in Colorectal Tumors by Deep Learning}""*

### Data license

**Value**: `CC BY 4.0`

> **Source**: SourceZenodo API record 3832231 · metadata.license  
> *""license": {"id": "cc-by-4.0"}""*

### Impact

**Value**: `Paper cited 337 times (Crossref) · DeepHistology repository 68 stars · counted on 2026-06-27`

> **Source**: SourceCrossref Works API / GitHub repo page / GitHub repository API · message.is-referenced-by-count / stargazer button aria-label / stargazers_count  
> *""is-referenced-by-count": 337; "68 users starred this repository"; ""stargazers_count": 68""*

### Main sources

- **Dataset homepage**: https://zenodo.org/records/3832231 (accessed 2026-05-29)
- **Paper**: Gastroenterology 159(4), October 2020 · doi:10.1053/j.gastro.2020.06.021 · PMID 32562722 · PMC7578071
- **Hosting record**: Zenodo record 3832231, version v1
- **Metadata files**: Zenodo record metadata; TRAIN.zip and TEST.zip file listings; DeepHistology README (TCGA-CRC-DX example directory); the paper's Supplementary Table S1 (clinico-pathological features of each cohort)

Supplementary Table S1 gives cohort summaries of age, sex, site, stage and BRAF/KRAS for the TCGA subcohort; the DeepHistology README only shows the structure of the project tables.

> **Source**: SourceZenodo record 3832231 / PubMed metadata / PMC HTML full text / GitHub README / Supplementary Table S1 · Published May 18, 2020 | Version v1 / PMID metadata / PMCID block / TCGA-CRC-DX example / clinico-pathological features  
> *""Published May 18, 2020 | Version v1"; "PMID- 32562722"; "PMCID: PMC7578071"; "An example for a possible data structure (project TCGA-CRC-DX) is"; "Table S1: Clinico-pathological features of each cohort.""*

---

## Clinical and pathological features

### Organ

**Value**: `Colorectum`

Supplementary Table S1 shows the TCGA subcohort includes both colon cancer (321, 75.4%) and rectal cancer (105, 24.6%).

> **Source**: SourceZenodo record 3832231 / Supplementary Table S1 · description / cohort table  
> *""These are histological images of colorectal cancer"; "colon cancer ... 321 (75.4%)"; "rectal cancer ... 105 (24.6%)""*

### Tumor type

**Value**: `Colorectal adenocarcinoma`

The paper's methods describe the TCGA subcohort as colorectal adenocarcinoma patients; the sources give no histological subtypes such as mucinous adenocarcinoma. MSIH / nonMSIH is a molecular status, not a histological subtype.

> **Source**: SourcePMC HTML full text · Materials and methods  
> *""We retrospectively collected anonymized H&E stained tissue slides of colorectal adenocarcinoma patients""*

### Main classification fields

- **Official main task**: MSI status classification from histology tiles
- **MSI_Status**: MSIH / nonMSIH; each tile inherits its patient's MSI status

The Zenodo description writes the negative class as NonMSIH, while the archive folder is named nonMSIH; this report uses the folder name.

> **Source**: SourceZenodo record 3832231 / official ZIP central directory of TRAIN.zip and TEST.zip · description / archive entries  
> *""patients with MSI-H = MSIH; patients with MSI-L and MSS = NonMSIH"; "TRAIN/MSIH"; "TRAIN/nonMSIH"; "TEST/MSIH"; "TEST/nonMSIH""*

### Clinical information

| Field | Level | Values |
| --- | --- | --- |
| MSI status | Per patient, inherited by all its tiles | MSIH / nonMSIH |
| UICC stage | Cohort summary | Stage I 67 (15.7%) · stage II 154 (36.2%) · stage III 133 (31.2%) · stage IV 59 (13.8%) |
| BRAF | Cohort summary | Mutant 56 (13.1%) · wild type 370 (86.9%) |
| KRAS | Cohort summary | Mutant 192 (45.1%) · wild type 234 (54.9%) |

Only MSI status reaches each tile; stage, BRAF and KRAS exist only as cohort summaries. The TCGA-CRC-DX_CLINI.xlsx and TCGA-CRC-DX_SLIDE.csv mentioned in the DeepHistology README only show column names such as PATIENT and FILENAME; no per-patient clinical values are public.

> **Source**: SourceZenodo record 3832231 / GitHub README / Supplementary Table S1 · description / example data structure / clinico-pathological features  
> *""all tiles inherited the label of the parent patient"; "CLINI table 'TCGA-CRC-DX_CLINI.xlsx'"; "SLIDE table 'TCGA-CRC-DX_SLIDE.csv'"; "mean age at Dx | 65.6"; "male | 211 (49.5%)"; "Region | US"; "BRAF mutant | 56 (13.1%)"; "KRAS mutant | 192 (45.1%)""*

### Stain

**Value**: `H&E (hematoxylin and eosin)`

Both the paper and the Zenodo description state routine H&E staining; no immunohistochemistry, immunofluorescence or other stains appear.

> **Source**: SourceZenodo record 3832231 / PMC HTML full text · description / Methods  
> *""hematoxylin and eosin-stained slides"; "routine H&E histology""*

### Rare disease

**Value**: `No`

Searching the Orphanet Rare Disease Ontology (ORDO 4.8) for colorectal adenocarcinoma and colorectal cancer gives no exact match; the nearest results are hereditary cancer-predisposition syndromes such as Familial colorectal cancer Type X and Hereditary nonpolyposis colon cancer, which do not correspond to this dataset's colorectal adenocarcinoma.

> **Source**: SourceOLS4 ORDO ontology metadata / OLS4 ORDO search / OLS4 ORDO term detail · version / search / term detail  
> *""version": "4.8""; ""numFound": 0"; ""label": "Familial colorectal cancer Type X""; ""label": "Hereditary nonpolyposis colon cancer"""*

### Rare disease name

**Value**: `None`

> **Source**: SourceOLS4 ORDO ontology metadata / OLS4 ORDO search / OLS4 ORDO term detail · version / search / term detail  
> *""version": "4.8""; ""numFound": 0"; ""label": "Familial colorectal cancer Type X""; ""label": "Hereditary nonpolyposis colon cancer"""*

### Demographics

- **Region**: United States
- **Mean age at diagnosis**: 65.6 years
- **Sex**: Male 211 (49.5%) · female 213 (50.0%)
- **Primary site**: Colon 321 (75.4%) · rectum 105 (24.6%)

All are cohort summaries for the TCGA subcohort from Supplementary Table S1. The sources give no race or ethnicity information and no per-patient demographics file.

> **Source**: SourceSupplementary Table S1 · TCGA cohort statistics  
> *""Region | US"; "mean age at Dx | 65.6"; "male | 211 (49.5%)"; "female | 213 (50.0%)"; "colon cancer | 321 (75.4%)"; "rectal cancer | 105 (24.6%)""*

### Centers

**Value**: `Multicenter · from TCGA`

The paper describes TCGA as a multicenter study with patients mainly from the United States; the sources do not list the contributing hospitals.

> **Source**: SourcePMC HTML full text · Materials and methods  
> *""First, we used the publicly available Cancer Genome Atlas (TCGA, n=616 patients ...), a multicenter study with Stage I to IV patients mainly from the United States of America.""*

---

## Data size and format

### Data volume

|  | Patients | Slides | Tiles |
| --- | --- | --- | --- |
| All | 423 | 428 | 51,918 |
| Training set TRAIN | 281 | 284 | 19,557 |
| Test set TEST | 142 | 144 | 32,361 |
| MSIH | 63 | 64 | 15,002 |
| nonMSIH | 360 | 364 | 36,916 |

Counted from the official archive file listings, no patient appears in both the training and test sets. The paper's Supplementary Table S4 records 426 patients for the TCGA cohort, 3 more than the archives; the file listings are used to describe the data actually released.

> **Source**: Sourceofficial ZIP central directory of TRAIN.zip / TEST.zip / Supplementary Table S4 · archive entries / model table  
> *""TRAIN/MSIH"; "TRAIN/nonMSIH"; "TEST/MSIH"; "TEST/nonMSIH"; "TCGA (N=426, 15% MSI)""*

### Storage size

**Value**: `About 3.36 GB: TRAIN.zip 1,279,103,781 bytes, TEST.zip 2,084,051,578 bytes`

The 3.13 GB shown on the Zenodo page is the same total converted in base 1024. There is no separate annotation or metadata attachment.

> **Source**: SourceZenodo record 3832231 / Zenodo API record 3832231 · schema.org / files  
> *""contentSize": "3.13 GB""; ""key": "TRAIN.zip", "size": 1279103781"; ""key": "TEST.zip", "size": 2084051578""*

### Usable images

**Value**: `51,918 tiles`

The unit of analysis is the tile, not the original whole-slide image; the tiles come from 428 slides of 423 patients.

> **Source**: Sourceofficial ZIP central directory of TRAIN.zip / TEST.zip · archive entries  
> *""TRAIN/MSIH"; "TRAIN/nonMSIH"; "TEST/MSIH"; "TEST/nonMSIH""*

### Data modality

**Value**: `Tissue morphology tiles`

The public content is only histopathology tiles, with the MSI label carried by the folder structure; no masks, ROI polygons, pathology reports or per-patient clinical tables are released.

> **Source**: SourceZenodo record 3832231 / official ZIP central directory of TRAIN.zip and TEST.zip · description / archive entries  
> *""histological images"; "all tiles inherited the label of the parent patient"; "TRAIN/MSIH"; "TEST/nonMSIH""*

### Data details

Folders are TRAIN/MSIH, TRAIN/nonMSIH, TEST/MSIH and TEST/nonMSIH; file names combine the TCGA slide ID and the tile coordinates, in .jpg format. Tumor regions were first outlined manually on the slides, then cut into tiles of 256 μm edge length, saved at 512 pixels (0.5 μm/pixel) and color-normalized with the Macenko method. Label rule: MSI-H is MSIH; MSI-L and MSS are nonMSIH. The training set was randomly downsampled to balance the classes; the test set was not.

> **Source**: SourceZenodo record 3832231 / PMC HTML full text / GitHub README / official ZIP central directory of TRAIN.zip and TEST.zip · description / Methods / TCGA-CRC-DX example / archive entries  
> *""Tumor tissue was outlined manually"; "cut into tiles of 256 μm edge length, saved as 512 px images"; "All image tiles were color-normalized with the Macenko method"; "TRAIN/MSIH"; "TEST/nonMSIH""*

### Image format

**Value**: `Tiles · .jpg · 512 pixels · 0.5 μm/pixel`

The original whole-slide images are SVS (Supplementary Table S1); what is public are the JPG tiles cut from them. The scanning magnification is not stated.

> **Source**: SourcePMC HTML full text / Supplementary Table S1 / official ZIP central directory of TRAIN.zip and TEST.zip · Methods / cohort table / archive entries  
> *""saved at a resolution of 0.5 μm per pixel"; "512×512x input layer"; "WSI format ... SVS"; ".jpg""*

### Specimen preparation

**Value**: `Not stated`

The sources only say each patient has at least one tissue slide and that stages I–IV are covered; FFPE, frozen, biopsy or resection is not stated.

> **Source**: SourcePMC HTML full text / Supplementary Table S1 · Materials and methods / cohort table  
> *""For each patient, at least one histological slide was available"; "Stage I"; "Stage II"; "Stage III"; "Stage IV""*

### Scanner

**Value**: `Not stated`

Supplementary Table S1 gives only the original whole-slide format, SVS; the scanner maker, model, magnification and native resolution are not public.

> **Source**: SourceSupplementary Table S1 · TCGA cohort table  
> *""WSI format ... SVS""*

### Spatial omics resolution

**Value**: `Not applicable`

This resource has no spatial omics data.

> **Source**: SourceZenodo record 3832231 / PMC HTML full text · description / Methods  
> *""histological images"; "H&E stained tissue slides""*

---

## Annotation, task and quality control

### Task type

**Value**: `Classification · MSI status classification from histology tiles`

The input is a tile; the output is MSIH or nonMSIH.

> **Source**: SourceZenodo record 3832231 / PMC HTML full text · description / Methods  
> *""sorted by MSI status"; "all tiles inherited the label of the parent patient"; "We trained a deep-learning detector to identify samples with MSI from these slides""*

### Task description

As used in the paper: the input is a color-normalized tile (512 pixels, 0.5 μm/pixel) from the tumor region of a colorectal cancer H&E whole-slide image, the output is MSIH or nonMSIH, and tile predictions are averaged per patient.

> **Source**: SourceZenodo record 3832231 / PMC HTML full text · description / Methods  
> *""sorted by MSI status"; "all tiles inherited the label of the parent patient"; "Tile-level predictions were averaged on a patient level""*

### Image origin

**Value**: `Derived from existing data · TCGA colorectal cancer whole-slide images · hosted on Zenodo`

The tiles were cut from existing TCGA whole-slide images and color-normalized; they are not newly acquired slides. The original SVS files are available from the GDC portal.

> **Source**: SourceZenodo record 3832231 / PMC HTML full text · description / Materials and methods  
> *""derived from the TCGA database"; "All images and data from the TCGA study are publicly available at https://portal.gdc.cancer.gov""*

### Annotation origin

**Value**: `Derived from existing data · patient-level MSI status determined by genetic testing in TCGA`

No new masks or per-tile annotations were drawn; each tile inherits its patient's MSI status.

> **Source**: SourceZenodo record 3832231 / PMC HTML full text · description / Methods  
> *""all tiles inherited the label of the parent patient"; "Specimens with MSI were identified by genetic analyses.""*

### Multi-stain alignment

**Value**: `Not applicable`

There is only one stain, H&E, so no cross-stain registration is involved.

> **Source**: SourceZenodo record 3832231 / PMC HTML full text · description / Methods  
> *""H&E stained tissue slides"; "color-normalized""*

### Quality control

**Value**: `Manual QC · exclusion reasons: insufficient quality, technical issues, no tumor tissue`

Every slide was reviewed manually by an observer under the supervision of a pathology expert to confirm it contained tumor tissue and was of diagnostic quality; cases without molecular information were also excluded. QC was applied to slides and tumor regions, not as automatic per-tile QC. The paper's discussion notes that one slide in an external test set was blurred by a technical artifact that the manual review missed.

> **Source**: SourcePMC HTML full text · Methods / Discussion  
> *""All slides were individually, manually reviewed"; "ensure that tumor tissue was present on the slide and the slide had diagnostic quality"; "excluded due to insufficient quality, technical issues, absence of tumor tissue"; "a technical artifact had resulted in a blurred image""*

---

## Notes

### Differences between sources

Two things differ: the patient count (423 in the archive file listings, 426 in the paper's Supplementary Table S4) and how the negative class is written (NonMSIH in the Zenodo description, nonMSIH as the folder name). Patients were split 2:1 into training and test sets.

> **Source**: SourceSupplementary Table S4 / Zenodo record 3832231 / official ZIP central directory of TRAIN.zip and TEST.zip · model table / description / archive entries  
> *""TCGA (N=426, 15% MSI)"; "Patients were split into training and test set in a 2:1 ratio"; "TRAIN/nonMSIH"; "TEST/nonMSIH""*

---
