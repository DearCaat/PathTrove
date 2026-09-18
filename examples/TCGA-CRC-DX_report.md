# PathTrove Full-Field Dataset Report Example: TCGA-CRC-DX

> **Full-field example / 全字段样例** · [English version](./TCGA-CRC-DX_report.en.md)  
> This example contains all 38 fields in the current PathTrove dataset-report contract. The authoritative report narrative is currently maintained in Chinese; structured JSON keys and many field headings retain their English terminology.  
> 本样例包含 PathTrove 当前数据集报告契约的全部 38 个字段。权威报告正文目前以中文维护，结构化 JSON 键和主要字段标题保留英文术语。
> 
> *Note: This is a representative demonstration of the schema and format, not the final complete release. / 注：本文件为展示结构与规范的代表性样例，非最终完整版本。*

## Usage notice / 使用说明

This report sample is governed by the [PathTrove Research Use Terms](../TERMS_OF_USE.md) and is excluded from the repository-wide CC BY 4.0 documentation license. It may be viewed, cited, and quoted to a limited extent for non-commercial research. Commercial use or republishing, mirroring, packaging, or redistributing this report or a substantial portion of it requires prior permission from the PathTrove contributors.

本报告样例适用 [PathTrove 科研使用条款](../TERMS_OF_USE.md)，不适用仓库文档的 CC BY 4.0 许可。用户可以阅读、正确引用，并可为非商业科研进行有限摘录；未经 PathTrove 贡献者事先许可，不得用于商业用途，也不得重新发布、镜像、打包或分发本报告或其中的实质部分。

The license values recorded in individual fields describe upstream resources; they do not license the PathTrove report itself. / 各字段记录的许可证描述上游资源，不代表相同许可证自动适用于 PathTrove 报告本身。

---

## 一、数据集综合简介
CRC-MSI 对应的公开 release 由 Zenodo 记录 `10.5281/zenodo.3832231` 承载，官方题名为 “Histological image tiles for TCGA-CRC-DX, color-normalized, sorted by MSI status, train/test split”。该资源是从 TCGA 结直肠癌全切片图像中裁出的 H&E patch 数据集，面向 MSI 状态分类，公开提供 `TRAIN.zip` 与 `TEST.zip` 两个压缩包。Zenodo 描述、论文全文与官方 ZIP archive inventory 共同表明，该 release 采用 256 um 边长、512 px、0.5 um/px 的颜色归一化肿瘤 patch，并以患者级 MSI 标签继承到 tile 级。基于官方 archive inventory，本 release 当前公开包含 423 个唯一患者条码、428 个唯一 slide 标识和 51,918 个 patch。

---

## 二、基础档案（Metadata & Open Source）
- **1. 数据集名称**:
  ```json
  {
    "Dataset_Name": "TCGA-CRC-DX"
  }
  ```
  Zenodo 官方题名和 DeepHistology README 的项目名都使用 `TCGA-CRC-DX`，因此将其作为公开来源支持的稳定主名称。`CRC-MSI` 可视为围绕 MSI 任务的工作流别名，但不是本 release 在已核验 primary sources 中的官方主名。
  > 来源：【Zenodo 记录 3832231】【标题/页面标题】【"Histological image tiles for TCGA-CRC-DX, color-normalized, sorted by MSI status, train/test split"】

- **36. 数据类型**:
  ```json
  {
    "Data_Type": "Dataset"
  }
  ```
  官方托管记录将该资源标为 `Dataset`，且已核验来源中不存在 challenge submission、leaderboard、sequestered ground truth 或 benchmark protocol 等挑战赛资源特征，因此归类为普通公开数据集。
  > 来源：【Zenodo API record 3832231】【metadata.resource_type / status】【"resource_type\": {\"title\": \"Dataset\", \"type\": \"dataset\"}"; "\"status\": \"published\""】

- **5. 发布日期**:
  ```json
  {
    "Release_Date": "2020-05"
  }
  ```
  报告对象是 Zenodo 数据 release，而不是后续论文版本；因此采用 Zenodo `publication_date = 2020-05-18` 所对应的 `2020-05`。论文正式刊期 `2020 Oct` 作为相关文献时间，不覆盖数据 release 月份。
  > 来源：【Zenodo API record 3832231】【metadata.publication_date】【"publication_date\": \"2020-05-18\""】

- **2. 数据集主页链接**:
  ```json
  {
    "Primary_URL": "https://zenodo.org/records/3832231"
  }
  ```
  当前最稳定、最官方的数据集主页是 Zenodo record 页面；其 DOI `https://doi.org/10.5281/zenodo.3832231` 会解析到同一记录。
  > 来源：【Zenodo 记录 3832231】【canonical / citation_abstract_html_url】【"https://zenodo.org/records/3832231"】

- **3. 开源情况**:
  ```json
  {
    "Open_Status": "Fully Open"
  }
  ```
  Zenodo 元数据标记 `access_right: open`，页面 UI 也声明 record 与 files 均为 public；已核验到 `TRAIN.zip` 和 `TEST.zip` 都可直接访问，无需审批、账号申请或 DUA。
  > 来源：【Zenodo API record 3832231】【metadata.access_right / files】【"access_right\": \"open\""; "\"key\": \"TEST.zip\""; "\"key\": \"TRAIN.zip\""】

- **4. 开源说明**:
  该 release 公开开放的核心数据对象是两个压缩包：`TRAIN.zip` 与 `TEST.zip`。数据集 record 本身使用 CC BY 4.0；与之配套的 DeepHistology 代码仓库是独立的 MIT 许可证组件，不应与数据许可混淆。当前已核验来源未显示需要申请访问、签署 DUA 或使用专用客户端下载；主访问方式是直接从 Zenodo record 页面下载压缩包。
  > 来源：【Zenodo 记录 3832231 / Zenodo API record 3832231 / GitHub API jnkather/DeepHistology】【rights / access status / license】【"The record and files are publicly accessible."; "\"license\": {\"id\": \"cc-by-4.0\"}"; "\"name\": \"MIT License\""】

- **28. 论文标题**:
  ```json
  {
    "Paper_Title": "Clinical-Grade Detection of Microsatellite Instability in Colorectal Tumors by Deep Learning"
  }
  ```
  该题名由 DOI metadata、PubMed metadata 与 PMC 正文页一致支持。
  > 来源：【PubMed metadata / DOI metadata】【TI / title】【"Clinical-Grade Detection of Microsatellite Instability in Colorectal Tumors by Deep Learning."】

- **29. 论文链接**:
  ```json
  {
    "Primary_URL": "https://doi.org/10.1053/j.gastro.2020.06.021"
  }
  ```
  采用 DOI 作为主论文入口；PMC 页面和 PubMed 页面是可交叉核验的官方镜像/索引入口。
  > 来源：【PubMed metadata】【LID】【"10.1053/j.gastro.2020.06.021 [doi]"】

- **30. 下载链接**:
  ```json
  {
    "Primary_URL": "https://zenodo.org/records/3832231"
  }
  ```
  由于公开数据分成 `TRAIN.zip` 与 `TEST.zip` 两个组件，单个 JSON 主值采用能稳定列出两个文件的 Zenodo record 页面；具体组件级下载在开放文本中说明。
  `TRAIN.zip` 与 `TEST.zip` 的内容链接分别位于该 record 下，对应官方 content URL 为 `https://zenodo.org/api/records/3832231/files/TRAIN.zip/content` 和 `https://zenodo.org/api/records/3832231/files/TEST.zip/content`。
  > 来源：【Zenodo API record 3832231】【files / links.self_html】【"links\": {\"self_html\": \"https://zenodo.org/records/3832231\"}"; "\"key\": \"TRAIN.zip\""; "\"key\": \"TEST.zip\""】

- **31. 引用 (BibTeX)**:
  ```bibtex
  @article{Echle_2020, title={Clinical-Grade Detection of Microsatellite Instability in Colorectal Tumors by Deep Learning}, volume={159}, ISSN={0016-5085}, url={http://dx.doi.org/10.1053/j.gastro.2020.06.021}, DOI={10.1053/j.gastro.2020.06.021}, number={4}, journal={Gastroenterology}, publisher={Elsevier BV}, author={Echle, Amelie and Grabsch, Heike Irmgard and Quirke, Philip and van den Brandt, Piet A. and West, Nicholas P. and Hutchins, Gordon G.A. and Heij, Lara R. and Tan, Xiuxiang and Richman, Susan D. and Krause, Jeremias and Alwers, Elizabeth and Jenniskens, Josien and Offermans, Kelly and Gray, Richard and Brenner, Hermann and Chang-Claude, Jenny and Trautwein, Christian and Pearson, Alexander T. and Boor, Peter and Luedde, Tom and Gaisa, Nadine Therese and Hoffmeister, Michael and Kather, Jakob Nikolas}, year={2020}, month=Oct, pages={1406–1416.e11} }
  ```
  采用 DOI content negotiation 返回的正式文章 BibTeX。
  > 来源：【DOI content negotiation】【application/x-bibtex】【"@article{Echle_2020, title={Clinical-Grade Detection of Microsatellite Instability in Colorectal Tumors by Deep Learning}"】

- **32. 开源许可证**:
  ```json
  {
    "License": "CC-BY-4.0"
  }
  ```
  数据集 record 明确声明为 `cc-by-4.0`。需要区分：DeepHistology GitHub 仓库的 MIT 许可证只约束代码，不替代数据集许可。
  > 来源：【Zenodo API record 3832231】【metadata.license】【"license\": {\"id\": \"cc-by-4.0\"}"】

- **34. 影响力指标 (Paper Citations & GitHub Stars)**:
  ```json
  {
    "Paper_Citations": 387,
    "Citation_Source": "Google Scholar",
    "GitHub_Stars": 68,
    "GitHub_Repo": "https://github.com/jnkather/DeepHistology",
    "Retrieved_Date": "2026-07-04"
  }
  ```
  本轮 `2026-07-04` live 浏览器复核已恢复到字段契约优先链路：Google Scholar exact-paper query 命中原始论文并显示 `被引用次数：387`，同日 GitHub 仓库页显示 `68` stars。字段事实来源仍以 Scholar 结果页与 GitHub 仓库页为准。
  > 来源：【Google Scholar exact-paper query / GitHub repo page】【browser replay on 2026-07-04 / repository header】【"被引用次数：387"; "68 stars"】

- **35. 信息来源记录 (Source Provenance)**:
  ```json
  {
    "Official_Website": {
      "url": "https://zenodo.org/records/3832231",
      "accessed_date": "2026-05-29"
    },
    "Paper": {
      "title": "Clinical-Grade Detection of Microsatellite Instability in Colorectal Tumors by Deep Learning",
      "identifier": "doi:10.1053/j.gastro.2020.06.021; pmid:32562722; pmcid:PMC7578071",
      "version": "Gastroenterology 159(4), 2020 Oct; PMCID PMC7578071",
      "url": "https://doi.org/10.1053/j.gastro.2020.06.021"
    },
    "Repository_or_Hosting": {
      "platform": "Zenodo",
      "record_or_version": "record 3832231, version v1",
      "url": "https://doi.org/10.5281/zenodo.3832231"
    },
    "Primary_Metadata_Files": [
      "Zenodo API record 3832231 metadata",
      "TRAIN.zip official ZIP central directory",
      "TEST.zip official ZIP central directory",
      "DeepHistology README (TCGA-CRC-DX example data structure)",
      "Supplementary Table S1 (clinico-pathological features of each cohort)"
    ]
  }
  ```
  本报告的主依据来源是 Zenodo 官方 record/API、官方 ZIP archive inventory、PMC/PubMed 论文全文与元数据，以及官方 GitHub README。`Supplementary Table S1` 需要显式登记为主 metadata 来源之一，因为它公开承载了 TCGA 子队列的年龄、性别、部位、分期和 BRAF/KRAS 汇总统计；README 则主要补充项目级 `CLINI`/`SLIDE` 表结构线索，不替代 Zenodo 的数据发布事实。
  > 来源：【Zenodo 记录 3832231 / PubMed metadata / PMC HTML 全文 / GitHub README / Supplementary Table S1】【Published May 18, 2020 | Version v1 / PMID metadata / PMCID block / TCGA-CRC-DX example / clinico-pathological features】【"Published May 18, 2020 | Version v1"; "PMID- 32562722"; "PMCID: PMC7578071"; "An example for a possible data structure (project TCGA-CRC-DX) is"; "Table S1: Clinico-pathological features of each cohort."】

---

## 三、临床与病理特征（Clinical & Pathology）
- **6. 器官 (Organ)**:
  ```json
  {
    "Organs": ["Colorectum"]
  }
  ```
  来源明确支持该数据集来自结直肠癌病例；补充表进一步说明 TCGA 子队列中既包含 colon cancer 也包含 rectal cancer，因此器官层级采用 `Colorectum`。
  > 来源：【Zenodo 记录 3832231 / Supplementary Table S1】【description / cohort table】【"These are histological images of colorectal cancer"; "colon cancer ... 321 (75.4%)"; "rectal cancer ... 105 (24.6%)"】

- **8. 肿瘤类型 (Cancer Type)**:
  ```json
  {
    "Tumor_Types": ["Colorectal adenocarcinoma"]
  }
  ```
  - **总体癌种/疾病范围**: 公开 release 面向 colorectal cancer；论文方法部分把 TCGA 子队列描述为 `colorectal adenocarcinoma patients`。
  - **细粒度亚型/病理类别列表**: 已核验来源支持的最细病理实体是 `colorectal adenocarcinoma`；补充表仅额外给出 colon/rectal site 分布，而未进一步公开 mucinous 等组织学亚型 roster。
  - **证据边界**: `MSIH / NonMSIH` 是分子状态/任务标签，不作为肿瘤组织学实体写入本字段。
  > 来源：【PMC HTML 全文】【Materials and methods】【"We retrospectively collected anonymized H&E stained tissue slides of colorectal adenocarcinoma patients"】

- **37. 主要分类学字段 (Primary Taxonomy Fields)**:
  ```json
  {
    "Official_Main_Task": "MSI status classification from histology tiles",
    "Primary_Taxonomy_Fields": [
      {
        "Field_Name": "MSI_Status",
        "Field_Semantics": "每个 tile 继承其父患者的 MSI 状态，用于 MSIH 与非 MSI-H 的二分类任务。",
        "Values": ["MSIH", "nonMSIH"]
      }
    ]
  }
  ```
  Zenodo 描述明确说明全部 tile 继承父患者的 MSI 标签；官方 archive inventory 进一步证实公开目录按 `MSIH` 与 `nonMSIH` 两个值组织。需要注意，Zenodo 描述把阴性类写成 `NonMSIH`，而当前 archive 实际目录名是 `nonMSIH`；本字段的结构化值优先遵循实际 released archive 的标签值。
  > 来源：【Zenodo 记录 3832231 / TRAIN.zip 与 TEST.zip 官方 ZIP central directory】【description / archive entries】【"patients with MSI-H = MSIH; patients with MSI-L and MSS = NonMSIH"; "TRAIN/MSIH"; "TRAIN/nonMSIH"; "TEST/MSIH"; "TEST/nonMSIH"】

- **38. 临床 metadata (Clinical Metadata)**:
  ```json
  {
    "Metadata_Availability": "Partially Available",
    "Metadata_Sources": [
      "Zenodo 记录 3832231 description",
      "TRAIN.zip official ZIP central directory",
      "TEST.zip official ZIP central directory",
      "DeepHistology README",
      "Supplementary Table S1"
    ],
    "Metadata_Fields": [
      {
        "Field_Name": "MSI_Status",
        "Field_Semantics": "患者级 MSI 分子状态，公开 release 中由父患者标签继承到全部 tile。",
        "Values": ["MSIH", "NonMSIH/nonMSIH"]
      },
      {
        "Field_Name": "UICC_Stage",
        "Field_Semantics": "TCGA 子队列公开的分期分布。",
        "Values": ["Stage I 67 (15.7%)", "Stage II 154 (36.2%)", "Stage III 133 (31.2%)", "Stage IV 59 (13.8%)"]
      },
      {
        "Field_Name": "BRAF_Mutation_Status",
        "Field_Semantics": "TCGA 子队列公开的 BRAF 分子状态统计。",
        "Values": ["mutant 56 (13.1%)", "wildtype 370 (86.9%)"]
      },
      {
        "Field_Name": "KRAS_Mutation_Status",
        "Field_Semantics": "TCGA 子队列公开的 KRAS 分子状态统计。",
        "Values": ["mutant 192 (45.1%)", "wildtype 234 (54.9%)"]
      }
    ]
  }
  ```
  已核验来源表明，公开可复核的临床/分子 metadata 主要分成两层：一层是 Zenodo release 直接暴露并继承到 tile 级的 `MSI_Status` 标签；另一层是 `Supplementary Table S1` 提供的 TCGA 子队列 cohort-level `UICC_Stage`、`BRAF_Mutation_Status` 与 `KRAS_Mutation_Status` 汇总统计。`Age_at_Diagnosis`、`Sex`、`Primary_Site` 与 `Cohort_Region` 虽然也由 `Supplementary Table S1` 公开，但其 primary semantics 已分别由字段 20 与字段 6 承载，因此本字段不再在 `Metadata_Fields` 中重复，只把这些项目作为 exclusion boundary 保留在开放文本中。README 中出现的 `TCGA-CRC-DX_CLINI.xlsx` 与 `TCGA-CRC-DX_SLIDE.csv` 只公开了 `PATIENT` 与 `FILENAME` 这类技术性链接列名，没有进一步公开逐例临床值域；这些技术列以及 `WSI format = SVS` 等成像字段继续留在字段 10/17 的对象与格式说明中。
  > 来源：【Zenodo 记录 3832231 / GitHub README / Supplementary Table S1】【description / example data structure / clinico-pathological features】【"all tiles inherited the label of the parent patient"; "CLINI table 'TCGA-CRC-DX_CLINI.xlsx'"; "SLIDE table 'TCGA-CRC-DX_SLIDE.csv'"; "mean age at Dx | 65.6"; "male | 211 (49.5%)"; "Region | US"; "BRAF mutant | 56 (13.1%)"; "KRAS mutant | 192 (45.1%)"】

- **7. 染色 (Staining)**:
  ```json
  {
    "Stains": [
      {
        "Family": "H&E",
        "Technique_or_Platform": "N/A",
        "Specific_Stain_or_Marker": "Hematoxylin and eosin (H&E)"
      }
    ]
  }
  ```
  论文与 Zenodo 描述都明确该资源来自常规 H&E histology / H&E stained slides；未见 IHC/IF/mIF 等额外公开 stain family。
  > 来源：【Zenodo 记录 3832231 / PMC HTML 全文】【description / Methods】【"hematoxylin and eosin-stained slides"; "routine H&E histology"】

- **12. 罕见病属性**:
  ```json
  {
    "Rare_Disease_Status": "No"
  }
  ```
  已按 ORDO/Orphanet 流程对 `colorectal adenocarcinoma` 与 `colorectal cancer` 执行查询。OLS4 ORDO `2026-05-22` 载入的 `ORDO 4.8` 中，这两个输入都没有 exact match；宽松搜索返回的近似候选是 `Familial colorectal cancer Type X` 与 `Hereditary nonpolyposis colon cancer` 等遗传性癌症易感综合征，它们与本数据集的普通 `colorectal adenocarcinoma` / `colorectal cancer` 范围不构成 exact 或 stable-equivalent match，因此不能驱动 rare-disease positive decision。
  - Lookup_Batch_Metadata
    Source: OLS4 ORDO
    Version: ORDO 4.8
    Loaded_or_Release_Date: 2026-05-22T00:09:34.488720207
    Version_URL_or_File: https://www.orphadata.com/data/ontologies/ordo/last_version/ORDO_en_4.8.owl
    Accessed_Date: 2026-05-29
  - Lookup_Input: Colorectal adenocarcinoma
    Query_Term: colorectal adenocarcinoma
    Lookup_Source: OLS4 search + OLS4 term
    Search_or_File: https://www.ebi.ac.uk/ols4/api/search?q=colorectal%20adenocarcinoma&ontology=ordo
    Term_Record: N/A
    Disease_Detail_URL: N/A
    Synonym_Source: N/A
    Match_Status: no_match
    Matched_Name: N/A
    Matched_ID: N/A
    Match_Level: N/A
    Decision: does_not_drive_positive_rare_disease_decision
  - Lookup_Input: Colorectal cancer
    Query_Term: colorectal cancer
    Lookup_Source: OLS4 search + OLS4 term
    Search_or_File: https://www.ebi.ac.uk/ols4/api/search?q=colorectal%20cancer&ontology=ordo
    Term_Record: http://www.orpha.net/ORDO/Orphanet_440437 ; http://www.orpha.net/ORDO/Orphanet_443909
    Disease_Detail_URL: https://www.orpha.net/en/disease/detail/440437 ; https://www.orpha.net/en/disease/detail/443909
    Synonym_Source: N/A
    Match_Status: ambiguous_match
    Matched_Name: Familial colorectal cancer Type X ; Hereditary nonpolyposis colon cancer
    Matched_ID: ORPHA:440437 ; ORDO:443909
    Match_Level: syndrome / broader family
    Decision: does_not_drive_positive_rare_disease_decision
  > 来源：【OLS4 ORDO ontology metadata / OLS4 ORDO search / OLS4 ORDO term detail】【version / search / term detail】【"version\": \"4.8\""; "\"numFound\": 0"; "\"label\": \"Familial colorectal cancer Type X\""; "\"label\": \"Hereditary nonpolyposis colon cancer\""】

- **13. 罕见病名称**:
  ```json
  {
    "Rare_Diseases": "N/A"
  }
  ```
  字段 12 已根据 ORDO/Orphanet 查询判定为 `No`，因此本字段按契约写 `N/A`。本字段独立保留完整 lookup 边界如下，不依赖字段 12 代载：
  - Lookup_Batch_Metadata
    Source: OLS4 ORDO
    Version: ORDO 4.8
    Loaded_or_Release_Date: 2026-05-22T00:09:34.488720207
    Version_URL_or_File: https://www.orphadata.com/data/ontologies/ordo/last_version/ORDO_en_4.8.owl
    Accessed_Date: 2026-05-29
  - Lookup_Input: Colorectal adenocarcinoma
    Query_Term: colorectal adenocarcinoma
    Lookup_Source: OLS4 search + OLS4 term
    Search_or_File: https://www.ebi.ac.uk/ols4/api/search?q=colorectal%20adenocarcinoma&ontology=ordo&exact=true ; https://www.ebi.ac.uk/ols4/api/search?q=colorectal%20adenocarcinoma&ontology=ordo
    Term_Record: N/A
    Disease_Detail_URL: N/A
    Synonym_Source: N/A
    Match_Status: no_match
    Matched_Name: N/A
    Matched_ID: N/A
    Match_Level: N/A
    Decision: does_not_drive_positive_rare_disease_decision
  - Lookup_Input: Colorectal cancer
    Query_Term: colorectal cancer
    Lookup_Source: OLS4 search + OLS4 term
    Search_or_File: https://www.ebi.ac.uk/ols4/api/search?q=colorectal%20cancer&ontology=ordo&exact=true ; https://www.ebi.ac.uk/ols4/api/search?q=colorectal%20cancer&ontology=ordo
    Term_Record: http://www.orpha.net/ORDO/Orphanet_440437 ; http://www.orpha.net/ORDO/Orphanet_443909
    Disease_Detail_URL: https://www.orpha.net/en/disease/detail/440437 ; https://www.orpha.net/en/disease/detail/443909
    Synonym_Source: N/A
    Match_Status: ambiguous_match
    Matched_Name: Familial colorectal cancer Type X ; Hereditary nonpolyposis colon cancer
    Matched_ID: ORPHA:440437 ; ORDO:443909
    Match_Level: syndrome / broader family
    Decision: does_not_drive_positive_rare_disease_decision
  已检查到的候选项均为遗传性易感综合征或 broader family，不与字段 8 的 `colorectal adenocarcinoma` 实体形成 exact 或 stable-equivalent 对应关系，因此不进入 `Rare_Diseases` JSON。
  > 来源：【OLS4 ORDO ontology metadata / OLS4 ORDO search / OLS4 ORDO term detail】【version / search / term detail】【"version\": \"4.8\""; "\"numFound\": 0"; "\"label\": \"Familial colorectal cancer Type X\""; "\"label\": \"Hereditary nonpolyposis colon cancer\""】

- **20. 人口统计学与公平性**:
  ```json
  {
    "Demographics_Status": "Partially Reported",
    "Demographics_Tags": ["geography", "age", "sex"]
  }
  ```
  Supplementary Table S1 为 TCGA 子队列提供了若干公开 cohort-level 统计：地域 `US`，`mean age at Dx = 65.6`，性别分布 `male 211 (49.5%)`、`female 213 (50.0%)`，原发部位分布 `colon cancer 321 (75.4%)`、`rectal cancer 105 (24.6%)`，分期分布 `Stage I 67 (15.7%)`、`Stage II 154 (36.2%)`、`Stage III 133 (31.2%)`、`Stage IV 59 (13.8%)`，并报告了 `BRAF mutant 56 (13.1%)` 和 `KRAS mutant 192 (45.1%)`。这些信息均为公开 cohort-level demographic / clinico-molecular summary。已核验来源未公开 race/ethnicity 统计，也未在当前公开 release 中证实逐例公平性 metadata 文件。
  > 来源：【Supplementary Table S1】【TCGA cohort statistics】【"Region | US"; "mean age at Dx | 65.6"; "male | 211 (49.5%)"; "female | 213 (50.0%)"; "colon cancer | 321 (75.4%)"; "rectal cancer | 105 (24.6%)"】

- **11. 队列多样性与多中心**:
  ```json
  {
    "Center_Type": "Multi-center",
    "Center_Names": ["The Cancer Genome Atlas (TCGA)"]
  }
  ```
  该 release 来源于 TCGA，而论文明确把 TCGA 描述为一个 mainly from the United States 的 multicenter study。当前已核验来源未枚举具体供样医院名单，因此 JSON 只保留公开可证实的上游来源队列名 `TCGA`，并在开放文本中说明多中心边界。
  > 来源：【PMC HTML 全文】【Materials and methods】【"First, we used the publicly available Cancer Genome Atlas (TCGA, n=616 patients ...), a multicenter study with Stage I to IV patients mainly from the United States of America."】

---

## 四、数据规模与格式细节（Volume & Modalities）
- **14. 数据量**:
  ```json
  {
    "All": {
      "patients": 423,
      "wsi": 428,
      "patches": 51918
    },
    "Split": {
      "Train": {
        "patients": 281,
        "wsi": 284,
        "patches": 19557
      },
      "Test": {
        "patients": 142,
        "wsi": 144,
        "patches": 32361
      }
    },
    "Taxonomy": {
      "MSI_Status": {
        "MSIH": {
          "patients": 63,
          "wsi": 64,
          "patches": 15002
        },
        "nonMSIH": {
          "patients": 360,
          "wsi": 364,
          "patches": 36916
        }
      }
    }
  }
  ```
  公开 release 的实际数量口径优先采用官方 ZIP central directory，而不是仅复述论文实验 cohort summary。基于 archive inventory，`TRAIN.zip` 含 19,557 个 patch、284 个唯一 slide 标识、281 个唯一患者条码；`TEST.zip` 含 32,361 个 patch、144 个唯一 slide 标识、142 个唯一患者条码；两个 split 之间患者条码无重叠。与之相比，Supplementary Table S4 报告 `TCGA (N=426, 15% MSI)`，说明论文中的 TCGA cohort 总患者数与当前公开 archive inventory 存在 3 个患者级差异。按 shared source-priority，对“当前 released archive 的实际公开内容”采用 archive inventory 值，并把论文计数保留为背景口径。
  > 来源：【TRAIN.zip / TEST.zip 官方 ZIP central directory / Supplementary Table S4】【archive entries / model table】【"TRAIN/MSIH"; "TRAIN/nonMSIH"; "TEST/MSIH"; "TEST/nonMSIH"; "TCGA (N=426, 15% MSI)"】

- **15. 存储量大小**:
  ```json
  {
    "Total_Size": 3.13,
    "Unit": "GB"
  }
  ```
  Zenodo 页面 schema.org 数据给出该 release 的总体 `contentSize = 3.13 GB`。Zenodo API 文件列表进一步显示组件级大小：`TRAIN.zip = 1,279,103,781 bytes`，`TEST.zip = 2,084,051,578 bytes`；两者合计约 `3,363,155,359 bytes`。当前已核验来源未公开独立 annotation 或 metadata 附件大小，因此只能按两个图像压缩包分解。
  > 来源：【Zenodo 记录 3832231 / Zenodo API record 3832231】【schema.org / files】【"contentSize\": \"3.13 GB\""; "\"key\": \"TRAIN.zip\", \"size\": 1279103781"; "\"key\": \"TEST.zip\", \"size\": 2084051578"】

- **16. 有效图像数**:
  ```json
  {
    "Total": 51918,
    "Unit": "patches"
  }
  ```
  该 release 实际公开的可分析图像单位是 patch，而不是原始 WSI。基于官方 archive inventory，共有 51,918 个 JPEG patch；这些 patch 来源于 428 个唯一 slide 标识和 423 个唯一患者条码。补充材料中的 `TCGA N=426` 是论文 cohort 口径，不等同于当前公开 patch archive 的实际患者条码总数。
  > 来源：【TRAIN.zip / TEST.zip 官方 ZIP central directory】【archive entries】【"TRAIN/MSIH"; "TRAIN/nonMSIH"; "TEST/MSIH"; "TEST/nonMSIH"】

- **9. 数据模态 (Modalities)**:
  ```json
  {
    "Modalities": ["Morphology Patch Images"]
  }
  ```
  当前公开可直接下载并核验的 released data object 是组织病理 patch 图像。MSI 标签通过目录/患者继承关系公开，但未在已核验来源中看到独立发布的 mask、ROI polygon、病理报告 PDF 或可确认的逐例临床表文件，因此不额外扩展为其它主模态。
  > 来源：【Zenodo 记录 3832231 / TRAIN.zip 与 TEST.zip 官方 ZIP central directory】【description / archive entries】【"histological images"; "all tiles inherited the label of the parent patient"; "TRAIN/MSIH"; "TEST/nonMSIH"】

- **10. 数据详情 (Data Details)**:
  该 release 由两个公开压缩包组成：`TRAIN.zip` 与 `TEST.zip`。已核验的官方 archive inventory 显示其目录结构为 `TRAIN/MSIH`、`TRAIN/nonMSIH`、`TEST/MSIH`、`TEST/nonMSIH`，文件名由 TCGA slide 标识与 tile 坐标组成，实际图像文件为 `.jpg` patch。Zenodo 描述与论文方法部分共同表明，这些 patch 来自 TCGA 结直肠癌 H&E 全切片中的肿瘤区域：肿瘤组织先由观察者在 slide 上人工勾画，再被切成 `256 um edge length`、保存为 `512 px images`、等效 `0.5 um/px` 的 tile；随后应用 Macenko color normalization。标签语义为患者级 MSI 状态继承到 tile 级，其中 `MSI-H = MSIH`，`MSI-L + MSS = NonMSIH/nonMSIH`。Zenodo 说明还指出训练集进行了随机下采样以平衡类别，而测试集未做下采样。当前已核验来源没有公开证实额外的 ROI polygon、分割 mask、bbox、逐 tile 质量标志或独立 clinical table 被一并发布。
  > 来源：【Zenodo 记录 3832231 / PMC HTML 全文 / GitHub README / TRAIN.zip 与 TEST.zip 官方 ZIP central directory】【description / Methods / TCGA-CRC-DX example / archive entries】【"Tumor tissue was outlined manually"; "cut into tiles of 256 μm edge length, saved as 512 px images"; "All image tiles were color-normalized with the Macenko method"; "TRAIN/MSIH"; "TEST/nonMSIH"】

- **17. 切片数字格式**:
  ```json
  {
    "Image_Format_Families": ["Patch"],
    "Scan_Magnification": [],
    "Scan_Resolution_MPP": ["0.5 μm/px"]
  }
  ```
  当前 release 的直接图像对象是 patch。公开文件为 `.jpg`，尺寸由来源明确支持为 `512 px`，对应 `256 um` 边长和 `0.5 um/px`；其父级原始载体在 Supplementary Table S1 中标记为 `SVS` WSI。
  > 来源：【PMC HTML 全文 / Supplementary Table S1 / TRAIN.zip 与 TEST.zip 官方 ZIP central directory】【Methods / cohort table / archive entries】【"saved at a resolution of 0.5 μm per pixel"; "512×512x input layer"; "WSI format ... SVS"; ".jpg"】

- **18. 切片制备格式**:
  ```json
  {
    "Preparation_Formats": ["Not Specified"]
  }
  ```
  已核验来源明确支持的是结直肠腺癌 H&E slide 与 TCGA 上游来源，但没有对当前公开 release 单独给出 FFPE、Frozen、Biopsy、Resection 等标准化制备短值；因此按规则保留为 `Not Specified`。开放来源只说明 TCGA cohort 涵盖 Stage I-IV 患者和至少一张 histological slide。
  > 来源：【PMC HTML 全文 / Supplementary Table S1】【Materials and methods / cohort table】【"For each patient, at least one histological slide was available"; "Stage I"; "Stage II"; "Stage III"; "Stage IV"】

- **19. 扫描器信息**:
  ```json
  {
    "Scanner_or_System": [
      {
        "Vendor": "Not Specified",
        "Model_or_System": "Not Specified"
      }
    ]
  }
  ```
  补充表只给出 TCGA 队列的 `WSI format = SVS`，并未公开扫描器 vendor、型号、扫描倍率或原始 MPP。当前公开 release 直接提供的是 JPG patch，而不是带扫描器元数据的原始 SVS 文件，因此 JSON 保持 `Not Specified`，开放文本保留已知格式边界。
  > 来源：【Supplementary Table S1】【TCGA cohort table】【"WSI format ... SVS"】

- **22. 空间组学分辨率**:
  该资源不是空间转录组或其它 ST 数据集；已核验来源仅支持 H&E 全切片衍生 patch，因此本字段不适用，按规则保留 `Not Specified`。
  > 来源：【Zenodo 记录 3832231 / PMC HTML 全文】【description / Methods】【"histological images"; "H&E stained tissue slides"】

---

## 五、标注、任务与质量控制（Annotations & Task Setup）
- **23. 任务标签**:
  ```json
  {
    "CV_Category": ["Classification"],
    "Specific_Task_Label": ["MSI status classification from histology tiles"]
  }
  ```
  数据 release 的官方标签组织方式和论文任务描述都指向 MSI 状态二分类。这里的 `CV_Category` 由 `Specific_Task_Label` 的输入输出关系归纳而来：输入为 histology tiles，输出为 `MSIH` / `nonMSIH`。
  > 来源：【Zenodo 记录 3832231 / PMC HTML 全文】【description / Methods】【"sorted by MSI status"; "all tiles inherited the label of the parent patient"; "We trained a deep-learning detector to identify samples with MSI from these slides"】

- **26. 任务描述**:
  以下为论文/官网给出的官方样例或推荐用法，仅供参考；不代表唯一可用任务，除非来源明确声明为官方 benchmark。

  1. 任务名称：MSI 状态分类
     输入（Input）：来自 TCGA 结直肠癌 H&E 全切片肿瘤区域的颜色归一化 patch（512 px，0.5 um/px）。
     输出（Output）：`MSIH` 或 `nonMSIH / NonMSIH` 二分类标签。
     说明：Zenodo release 直接按 `MSIH` 和 `nonMSIH` 目录发布 patch；论文方法部分说明所有 tile 继承父患者的 MSI 标签，并将 tile-level 预测在患者层面聚合。
  > 来源：【Zenodo 记录 3832231 / PMC HTML 全文】【description / Methods】【"sorted by MSI status"; "all tiles inherited the label of the parent patient"; "Tile-level predictions were averaged on a patient level"】

- **24. 图像数据来源**:
  ```json
  {
    "Origin_Status": "Derived from Existing",
    "Normalized_Source_Values": [
      "TCGA colorectal cancer whole-slide images from the TCGA database / GDC portal"
    ],
    "Hosting_or_Distribution_Platforms": [
      "Zenodo"
    ],
    "Boundary_Note": "Current release distributes color-normalized tumor tiles derived from pre-existing TCGA WSIs rather than the raw TCGA SVS files."
  }
  ```
  图像对象并非新采集原始切片，而是从既有 TCGA 结直肠癌 WSI 中裁出的衍生 patch。Zenodo 描述明确写明 `derived from the TCGA database`；论文方法进一步说明 TCGA 原始图像可在 GDC portal 获得，而当前报告对象是基于这些 WSI 的二次发布 tile resource。
  > 来源：【Zenodo 记录 3832231 / PMC HTML 全文】【description / Materials and methods】【"derived from the TCGA database"; "All images and data from the TCGA study are publicly available at https://portal.gdc.cancer.gov"】

- **25. 标注数据来源**:
  ```json
  {
    "Origin_Status": "Derived from Existing",
    "Normalized_Source_Values": [
      "Patient-level TCGA MSI status determined by genetic analyses"
    ],
    "Hosting_or_Distribution_Platforms": [
      "Zenodo"
    ],
    "Boundary_Note": "The released supervision is not a newly drawn mask set. Zenodo states that all tiles inherited the label of the parent patient, so the tile-level class labels are derived from pre-existing patient-level TCGA MSI labels rather than created de novo for this patch release."
  }
  ```
  当前公开标签不是新建的像素级或实例级标注，而是来源于既有患者级 MSI 分子标签。这里将 `Origin_Status` 保持为 `Derived from Existing`，但只把真实的既有 supervision source 写成 `Patient-level TCGA MSI status determined by genetic analyses`；`all tiles inherited the label of the parent patient` 属于标签继承机制而不是来源值，因此移入 `Boundary_Note` 和开放文本解释。当前可合法复核的 primary sources 足以支持“既有患者级 MSI 标签 -> tile 级继承发布”这一监督边界，但不足以再虚构一个额外未公开的独立 label-file 名称。
  > 来源：【Zenodo 记录 3832231 / PMC HTML 全文】【description / Methods】【"all tiles inherited the label of the parent patient"; "Specimens with MSI were identified by genetic analyses."】

- **27. 多染色对齐质量**:
  ```json
  {
    "Alignment_Label": "N/A"
  }
  ```
  该 release 是单一 H&E 染色的 patch 数据集，不存在跨染色配准、same-section multi-marker 或 synthetic stain pairing。
  > 来源：【Zenodo 记录 3832231 / PMC HTML 全文】【description / Methods】【"H&E stained tissue slides"; "color-normalized"】

- **21. 质控状态与伪影**:
  ```json
  {
    "QC_Status": "Manual QC",
    "Artifact_Tags": ["insufficient quality", "technical issues", "absence of tumor tissue"]
  }
  ```
  论文方法部分说明所有 slide 都经过观察者逐张人工复核，并由专家病理学家监督，以确认存在肿瘤组织且切片具有诊断质量；不满足条件的病例会因 `insufficient quality`、`technical issues`、`absence of tumor tissue` 或 `lack of molecular information` 被排除。该 QC target 作用于 slide / tumor-region selection，而不是 tile 级自动质控。论文讨论还额外指出，外部测试集中曾出现高倍模糊伪影漏检的个案，提示人工 QC 仍有残余风险。
  > 来源：【PMC HTML 全文】【Methods / Discussion】【"All slides were individually, manually reviewed"; "ensure that tumor tissue was present on the slide and the slide had diagnostic quality"; "excluded due to insufficient quality, technical issues, absence of tumor tissue"; "a technical artifact had resulted in a blurred image"】

---

## 六、备注
- **33. 备注**: 当前公开 release 的实际 archive inventory 与论文补充材料中的 TCGA cohort 摘要存在轻微口径差异。Supplementary Table S4 报告 `TCGA (N=426, 15% MSI)`，而官方 `TRAIN.zip` 与 `TEST.zip` central directory 当前可恢复出 `423` 个唯一患者条码、`428` 个唯一 slide 标识与 `51,918` 个 patch，且 split 间患者无重叠。按 shared source-priority，涉及“当前 released data 的真实公开内容”时，本报告采用官方 archive inventory；涉及 cohort 背景、年龄/分期/性别等论文统计时，仍保留补充材料数值。另一个需说明的边界是阴性类标签在 Zenodo 描述中写作 `NonMSIH`，而 archive 目录名实际为 `nonMSIH`，本报告在分类字段中优先保留实际 release label 值，同时在开放文本中注明该大小写差异。
  > 来源：【Supplementary Table S4 / Zenodo 记录 3832231 / TRAIN.zip 与 TEST.zip 官方 ZIP central directory】【model table / description / archive entries】【"TCGA (N=426, 15% MSI)"; "Patients were split into training and test set in a 2:1 ratio"; "TRAIN/nonMSIH"; "TEST/nonMSIH"】

---