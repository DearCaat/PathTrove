"""Chinese display of categorical values.

The Chinese table of the data package stores most categorical values in English (the source table has them that way), so a Chinese answer
would mix languages. For lang=zh the plugin shows these values in Chinese; filters accept both spellings. Only categorical values are
mapped (no prose, no names, no quotations). Abbreviations that are used as such in Chinese (H&E, IHC, WSI, ROI, FFPE ...) are kept.
The map is static (the en/zh snapshot pair only holds two such pairs, merged in `data.py`); test_zh_values.py checks that every value of
every categorical column is covered and that each column's map is one-to-one.
"""
from __future__ import annotations

import re
from typing import Any

NS = "未说明"
KEEP = "="   # marker: shown unchanged

ZH_VALUES: dict[str, dict[str, str]] = {
    "3-1": {"Fully Open": "完全开放", "Partially Open": "部分开放", "Closed": "封闭", "Not Specified": NS},
    "6-1": {"Breast": "乳腺", "Lung": "肺", "Colorectum": "结直肠", "Brain": "脑", "Kidney": "肾", "Prostate": "前列腺", "Liver": "肝",
            "Lymph Node": "淋巴结", "Skin": "皮肤", "Bladder": "膀胱", "Stomach": "胃", "Cervix": "宫颈", "Bone": "骨", "Esophagus": "食管",
            "Blood": "血液", "Ovary": "卵巢", "Pancreas": "胰腺", "Adrenal Gland": "肾上腺", "Heart": "心脏", "Uterus": "子宫",
            "Head and Neck": "头颈", "Soft Tissue": "软组织", "Bile Duct": "胆管", "Eye": "眼", "Spleen": "脾", "Pleura": "胸膜",
            "Testis": "睾丸", "Thyroid": "甲状腺", "Thymus": "胸腺", "Gastrointestinal Tract": "胃肠道"},
    "7-1": {"H&E": KEEP, "IHC": KEEP, "IF": KEEP, "mIF": KEEP, "mIHC": KEEP, "Special stain": "特殊染色", "Pap-smear": "巴氏涂片",
            "EM": "电镜", "Not Specified": NS},
    "9-1": {"Morphology WSI": "形态学 WSI", "Morphology Patch Images": "形态学图块图像", "Segmentation Masks": "分割掩码",
            "Morphology ROI Images": "形态学 ROI 图像", "Clinical Variables": "临床变量", "Polygon/XML Annotations": "多边形/XML 标注",
            "Cytology Images": "细胞学图像", "Fluorescence Microscopy Images": "荧光显微图像", "Point Annotations": "点标注",
            "DNA / Mutation Data": "DNA / 突变数据", "Conversation / QA Text": "对话 / 问答文本",
            "Spatial Transcriptomics Count Matrices": "空间转录组计数矩阵", "Pathology Report Text": "病理报告文本",
            "3D Fluorescence Microscopy Volumes": "三维荧光显微体数据", "RNA Expression Matrices": "RNA 表达矩阵",
            "Radiology Images": "放射影像", "3D Volumes": "三维体数据", "Histopathology Image": "组织病理图像",
            "Landmark Annotations": "地标标注", "Radiology Report Text": "放射报告文本", "Protein / Proteomics Data": "蛋白质 / 蛋白质组数据",
            "IHC Image": "IHC 图像", "Cytology Image": "细胞图像", "IF/mIF Image": "IF/mIF 图像", "Protein": "蛋白质"},
    "11-1": {"Single-center": "单中心", "Multi-center": "多中心", "Not Specified": NS},
    "12-1": {"Glioblastoma (ORPHA:360)": "胶质母细胞瘤 (ORPHA:360)", "Cholangiocarcinoma (ORPHA:70567)": "胆管癌 (ORPHA:70567)",
             "Thymoma (ORPHA:99867)": "胸腺瘤 (ORPHA:99867)", "Diffuse large B-cell lymphoma (ORPHA:544)": "弥漫大 B 细胞淋巴瘤 (ORPHA:544)",
             "Uveal melanoma (ORPHA:39044)": "葡萄膜黑色素瘤 (ORPHA:39044)", "Adrenocortical carcinoma (ORPHA:1501)": "肾上腺皮质癌 (ORPHA:1501)",
             "Multiple myeloma (ORPHA:29073)": "多发性骨髓瘤 (ORPHA:29073)",
             "Cervical squamous cell carcinoma (ORPHA:213767)": "宫颈鳞状细胞癌 (ORPHA:213767)", "Ependymoma (ORPHA:251636)": "室管膜瘤 (ORPHA:251636)",
             "Clear cell ovarian carcinoma (ORPHA:398971)": "卵巢透明细胞癌 (ORPHA:398971)",
             "Endometrioid ovarian carcinoma (ORPHA:454723)": "卵巢子宫内膜样癌 (ORPHA:454723)",
             "Mucinous adenocarcinoma (ORPHA:398961)": "黏液腺癌 (ORPHA:398961)",
             "Precursor B-cell acute lymphoblastic leukemia (B-ALL) (ORPHA:99860)": "前体 B 细胞急性淋巴细胞白血病 (B-ALL) (ORPHA:99860)",
             "Testicular seminomatous germ cell tumor (ORPHA:842)": "睾丸精原细胞瘤型生殖细胞肿瘤 (ORPHA:842)",
             "Pleural mesothelioma (ORPHA:50251)": "胸膜间皮瘤 (ORPHA:50251)", "Small cell lung cancer (ORPHA:70573)": "小细胞肺癌 (ORPHA:70573)",
             "Phyllodes tumor of the breast (ORPHA:180261)": "乳腺叶状肿瘤 (ORPHA:180261)", "Kaposi sarcoma (ORPHA:33276)": "卡波西肉瘤 (ORPHA:33276)",
             "Cutaneous neuroendocrine carcinoma (ORPHA:79140)": "皮肤神经内分泌癌 (ORPHA:79140)",
             "Malignant epithelial tumor of ovary (ORPHA:398934)": "卵巢恶性上皮性肿瘤 (ORPHA:398934)",
             "MALT lymphoma (ORPHA:52417)": "MALT 淋巴瘤 (ORPHA:52417)",
             "Adenocarcinoma of the oesophagus and oesophagogastric junction (ORPHA:99976)": "食管及食管胃交界处腺癌 (ORPHA:99976)",
             "Acute promyelocytic leukemia (ORPHA:520)": "急性早幼粒细胞白血病 (ORPHA:520)", "不包含": KEEP},
    "16-2": {"slides": "切片", "roi": "ROI", "patches": "图块", "volumes_3d": "三维体数据", "tma": "TMA", "fov": "视野"},
    "17-1": {"WSI": KEEP, "Patch": "图块", "ROI": KEEP, "FOV": "视野", "Cell Image": "细胞图像", "3D Volume": "三维体数据", "TMA": KEEP,
             "Not Specified": NS},
    "18-1": {"Not Specified": NS, "FFPE": KEEP, "Surgical Resection": "手术切除", "Biopsy": "活检", "Frozen Section": "冰冻切片",
             "Tissue Section": "组织切片", "Bone Marrow Aspirate Smear": "骨髓穿刺涂片", "Peripheral Blood Smear": "外周血涂片",
             "Cell Block": "细胞蜡块", "TMA": KEEP},
    "21-1": {"Manual QC": "人工质控", "Automated QC": "自动质控", "Manual + Automated QC": "人工 + 自动质控", "Partial QC": "部分质控",
             "Not Specified": NS},
    "21-2": {"Annotation Quality": "标注质量", "Staining Quality": "染色质量", "Focus/Blur": "对焦/模糊", "Registration Quality": "配准质量",
             "Metadata/Label Consistency": "元数据/标签一致性", "Tissue Completeness": "组织完整性", "Pen Marking": "笔迹标记",
             "Tissue Fold": "组织折叠", "Scanner Artifact": "扫描仪伪影", "Bubble": "气泡"},
    "23-1": {"Classification": "分类", "Segmentation": "分割", "Detection": "检测", "Survival": "生存分析", "Regression": "回归",
             "Generation": "生成", "Retrieval": "检索", "Registration": "配准", "VQA": "视觉问答 (VQA)", "Counting": "计数",
             "Caption": "图像描述", "Staining": "染色", "Molecular Prediction": "分子预测", "Treatment Response": "治疗反应", "Reasoning": "推理"},
    "24-1": {"New": "新建", "Derived from Existing": "衍生自已有数据", "Reorganized Existing": "重组已有数据", "Hybrid": "混合", "Not Specified": NS},
    "25-1": {"New": "新建", "Derived from Existing": "衍生自已有数据", "Reorganized Existing": "重组已有数据", "Hybrid": "混合", "Not Specified": NS},
    "27-1": {"Pixel-level Alignment": "像素级对齐", "Sparse Alignment": "稀疏对齐", "Case-level Pairing": "病例级配对",
             "Same-section Multi-marker": "同切片多标记", "Synthetic or Derived Pairing": "合成或衍生配对", "Not Aligned": "未对齐",
             "N/A": "不适用", "Not Specified": NS},
    "36-1": {"Challenge Resource": "挑战赛资源", "benchmark": "基准测试", "Benchmark": "基准测试", "Dataset": "数据集", "数据集": KEEP},
}
# License names are identifiers or document titles and stay as they are; only the placeholder words are translated.
ZH_VALUES["32-1"] = {"Not Specified": NS, "other": "其他", "other-nc": "其他（非商业）",
                     "Custom (non-commercial, no redistribution)": "自定义（非商业，禁止再分发）"}
# Licence values that are kept as written (identifiers, names of agreements); listed so the coverage test can tell them from a miss.
LICENSE_KEEP_PATTERN = re.compile(r"^(?!Not Specified$|other$|other-nc$|Custom \(non-commercial, no redistribution\)$).+$")

PLACEHOLDERS = {"not specified": NS, "n/a": "不适用"}

# Value-layer keys of the report JSON blocks that hold the same values as a table column: (field id, key) -> column id.
REPORT_KEYS: dict[tuple[int, str], str] = {
    (3, "Open_Status"): "3-1", (6, "Organs"): "6-1", (7, "Family"): "7-1", (9, "Modalities"): "9-1", (11, "Center_Type"): "11-1",
    (16, "Unit"): "16-2", (17, "Image_Format_Families"): "17-1", (18, "Preparation_Formats"): "18-1", (21, "QC_Status"): "21-1",
    (21, "QC_Tags"): "21-2", (24, "Origin_Status"): "24-1", (25, "Origin_Status"): "25-1", (27, "Alignment_Label"): "27-1",
    (32, "License"): "32-1", (36, "Data_Type"): "36-1",
}


def _static(col_id: str) -> dict[str, str]:
    return {k: (k if v == KEEP else v) for k, v in ZH_VALUES.get(col_id, {}).items()}


def zh_map(col_id: str, snapshot_pairs: dict[str, str] | None = None) -> dict[str, str]:
    """{value as stored: Chinese display value} for one categorical column. `snapshot_pairs` = the data package's own {zh: en} pairs for
    the column; where the Chinese side is really Chinese it wins over the static map."""
    m = _static(col_id)
    for zh, en in (snapshot_pairs or {}).items():
        if re.search(r"[㐀-鿿]", zh):
            m.setdefault(zh, zh)
            m[en] = zh
    return m


def translate(col_id: str, value: Any, pairs: dict[str, str] | None = None) -> Any:
    m = zh_map(col_id, pairs)
    ci = {k.casefold(): v for k, v in m.items()}
    return ci.get(str(value).casefold(), value) if isinstance(value, str) else value


def translate_report_value(field_id: int, value: Any) -> Any:
    """A copy of a report value block with the categorical strings shown in Chinese (keys and prose untouched)."""
    def walk(v: Any, key: str | None) -> Any:
        col = REPORT_KEYS.get((field_id, key)) if key else None
        if isinstance(v, dict):
            return {k: walk(x, k) for k, x in v.items()}
        if isinstance(v, list):
            return [walk(x, key) for x in v]
        if col and isinstance(v, str):
            t = translate(col, v)
            return PLACEHOLDERS.get(v.casefold(), t) if t == v else t     # the report also writes the placeholders into free-vocabulary lists
        return v
    return walk(value, None)
