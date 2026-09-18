# PathTrove Data-Source Report Example: TCGA

> **Data-Source Report / 数据源报告样例**  
> 本样例展示 PathTrove 对上游大型综合数据平台（The Cancer Genome Atlas，TCGA）项目架构、数据分发口径、切片模态与获取条件的系统梳理。
> 
> *Note: This is a representative demonstration of the schema and format, not the final complete release. / 注：本文件为展示结构与规范的代表性样例，非最终完整版本。*

## Usage notice / 使用说明

This data-source report sample is governed by the [PathTrove Research Use Terms](../TERMS_OF_USE.md) and is excluded from the repository-wide CC BY 4.0 documentation license.  
本报告样例适用 [PathTrove 科研使用条款](../TERMS_OF_USE.md)，不适用仓库文档的 CC BY 4.0 许可。

---

## 一、数据源概览

- **官方名称**：The Cancer Genome Atlas（TCGA）
- **支持机构**：美国国家癌症研究所（NCI）与国家人类基因组研究所（NHGRI）
- **覆盖规模**：33 个癌症项目（Disease Projects），跨越 20 余个主要解剖部位
- **主分发入口**：NCI Genomic Data Commons (GDC) Data Portal，下游平台包括 cBioPortal PanCancer Atlas 与 UCSC Xena
- **定位**：癌症多组学与数字病理重要源头。部分项目包含 SVS 格式数字病理切片（WSI）。项目级数据不预设单一的视觉分类标签，亦无官方预划分的训练/测试集。

---

## 二、来源与开放状态

| 项目 | 内容说明 |
| :--- | :--- |
| **官方入口** | GDC Data Portal (`portal.gdc.cancer.gov`) |
| **开放模式** | 分级开放：Open Access（开放数据）与 Controlled Access（受控数据） |
| **病理图像权限** | Diagnostic Slides (DX) 与 Tissue Slides (TS) 全切片图像属于 **Open Access**，无需申请 dbGaP 权限即可合规下载 |
| **受控内容** | 种系突变（Germline variants）、未遮蔽突变（Raw SNP/Indel）与原始测序 BAM 文件需申请 dbGaP 授权 |

---

## 三、项目组成与切片规模（GDC Release 口径）

TCGA 共包含 33 个肿瘤子项目，总计收录 11,428 例病例与 30,326 张全切片图像（Slide Images）。常见重点项目概览如下：

| 项目 ID | 主要癌种 / 解剖部位 | 代表病例数 | 全切片图像数 (SVS) |
| :--- | :--- | :--- | :--- |
| **TCGA-BRCA** | 乳腺浸润癌 (Breast) | 1,098 | 2,132 |
| **TCGA-LUAD** | 肺腺癌 (Lung Adenocarcinoma) | 585 | 1,063 |
| **TCGA-LUSC** | 肺鳞癌 (Lung Squamous) | 504 | 1,046 |
| **TCGA-COAD** | 结肠腺癌 (Colon) | 460 | 973 |
| **TCGA-READ** | 直肠腺癌 (Rectum) | 171 | 374 |
| **TCGA-GBM** | 多形性胶质母细胞瘤 (Brain) | 617 | 1,061 |
| **TCGA-OV** | 卵巢浆液性囊腺癌 (Ovary) | 585 | 1,098 |
| **TCGA-KIRC** | 肾透明细胞癌 (Kidney) | 537 | 1,023 |

> **口径提示**：上述统计为 GDC 当前数据 Release 下的动态快照。各类已发表研究论文中报告的样本规模往往对应特定历史数据冻结期（Frozen Cohort），与当前 GDC 最新库容可能存在正常差异，在学术论文中应分别注明数据版本。

---

## 四、病理图像与多组学特征

1. **切片类型区分**：
   - **DX (Diagnostic Slides)**：常规术后石蜡切片（FFPE），通常保留较完整的组织结构，为计算病理研究的核心首选；
   - **TS (Tissue Slides)**：术中或冰冻组织切片，背景冰晶伪影较明显，通常用于分子取材确认。
2. **多模态配对**：
   大部分病例同时具备匹配的外显子测序、RNA-seq、DNA 甲基化及结构化临床随访数据，为弱监督病理基因组学（Pathogenomics）与预后建模提供了标准基准。

---

## 五、获取与复用建议流程

1. **项目与数据范围确认**：根据研究问题在 GDC 选定目标 Project ID（如 TCGA-CRC 包括 COAD 与 READ 两项目）；
2. **获取清单 Manifest**：通过 GDC API 或 GDC Data Transfer Tool 导出符合筛选条件（如仅 DX 切片、Primary Tumor）的 Manifest 清单；
3. **患者级独立划分**：TCGA 存在一例患者多张切片或多次活检情况，必须以 Case Barcode（前 12 位，如 `TCGA-XX-XXXX`）为单位严格划分训练集与测试集，严禁切片级随机打乱造成数据泄露。
