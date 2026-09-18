# PathTrove Download Guide Example: Ovarian-Bevacizumab-Response

> **Download Guide / 下载指南样例** · [English version](./Ovarian-Bev_download_guide.en.md)  
> 本样例展示 PathTrove 面向公开数据源（TCIA）实测整理的合规下载与校验指南。基于中国大陆实际网络环境实测，明确各文件的获取方式与环境配置。
> 
> *Note: This is a representative demonstration of the schema and format, not the final complete release. / 注：本文件为展示结构与规范的代表性样例，非最终完整版本。*

## Usage notice / 使用说明

This download guide sample is governed by the [PathTrove Research Use Terms](../TERMS_OF_USE.md) and is excluded from the repository-wide CC BY 4.0 documentation license.  
本指南样例适用 [PathTrove 科研使用条款](../TERMS_OF_USE.md)，不适用仓库文档的 CC BY 4.0 许可。

---

## 一、数据集概况

- **数据集名称**：Ovarian-Bevacizumab-Response（卵巢癌贝伐珠单抗疗效）
- **数据规模**：286 张 H&E 全切片图像（WSI，约 253.8 GB），来自 78 名患者
- **数据许可**：CC BY 4.0（由 TCIA 官方托管）
- **访问要求**：完全开放，无需账号、审批或签署数据使用协议

> **口径校准**：官方页面和原论文早期记载为 288 张（有效 162、无效 126）。当前 TCIA Version 2 官方已移除 `414056O.svs` 与 `414056P.svs` 两张切片，实为 286 张（有效 160、无效 126）。

---

## 二、获取清单与获取方式

| 文件 | 内容说明 | 体积 | 获取方式 |
| :--- | :--- | :--- | :--- |
| **病理切片** | 286 个 `.svs` 文件；H&E 染色，20× 放大率（0.5 µm/px） | 约 253.8 GB | 使用 Aspera 官方命令行工具 `ascli` 整包高速传输 |
| `new_CA125-data_20230207.xlsx` | 每张切片的疗效标签（effective / invalid）及治疗前后 CA-125 | 26 KB | HTTP 直链 / curl 直接下载 |
| `Final-patient_list.xlsx` | 患者临床特征（年龄、分期、用药、手术及生存随访日期） | 18 KB | HTTP 直链 / curl 直接下载 |
| 切片清单 CSV | 切片编号与对应患者编号映射清单 | 18 KB | HTTP 直链 / curl 直接下载 |

---

## 三、表格获取方式（curl 示例）

临床与标签表格体积小，可通过 HTTP 直连获取：

```bash
# 下载标签与 CA-125 表格
curl -fL -o new_CA125-data_20230207.xlsx \
  "https://public.cancerimagingarchive.net/nbia-api/services/v1/download?manifestUrl=..."

# 下载患者临床信息表
curl -fL -o Final-patient_list.xlsx \
  "https://public.cancerimagingarchive.net/nbia-api/services/v1/download?manifestUrl=..."
```

---

## 四、大规模切片下载（Aspera ascli 命令行实测）

TCIA 的切片数据通过 IBM Aspera 分发。为避免浏览器插件在服务器端无法使用的痛点，推荐使用 Aspera 官方命令行工具 `ascli`：

```bash
# 1. 配置 Aspera 秘钥与凭据
ascli conf global set bypass_keys=true

# 2. 批量整包下载切片（需设置限速参数 --ts 避免被限流至 0 字节）
ascli faspex packages download \
  --url "https://faspex.cancerimagingarchive.net" \
  --user "guest" \
  --package-id "..." \
  --ts "200m" \
  --to-folder "./ovarian_bev_wsi/"
```

*实测注意*：
1. 若网络中断，重跑同一命令即可断点续传；
2. 传输完成后，建议使用 `md5sum -c *.sums` 针对官方散列值逐文件核验完整性。

---

## 五、表格与切片的对应关系及排查

- **样本标识对齐**：标签表中的 `Image No.` 字段对应切片文件名（如 `1612595C.svs`）。
- **患者级映射**：5 例切片存在命名微小差异（如扩展名大小写或末尾空格），已核实对应同一患者 ID。
- **冲突排除**：对于两份官方表格中记录存在歧义或同时标注为有效与无效的极端争议病例，在构建实验基准时予以单独列出并暂不纳入建模。
