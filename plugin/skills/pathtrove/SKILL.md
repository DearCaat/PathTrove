---
name: pathtrove
description: Entry point when the user calls PathTrove by name - "/pathtrove ...", "$pathtrove ...", "use PathTrove", "用 PathTrove 查", "在 PathTrove 里找". Answer the request from the PathTrove database of computational-pathology datasets (resource table, resource reports, download guides, label files) through the pathtrove MCP tools, even when the question itself does not mention pathology. With no question, introduce what PathTrove can do. In Chinese or English.
---

# PathTrove (entry)

The user asked for PathTrove by name, so answer from PathTrove. Read the request as being about computational-pathology data even if it does not say so: "a small dataset I can download without applying" means a PathTrove resource, not a general-purpose dataset.

1. Call `pathtrove_version` with `lang` = the language the user writes in. It returns the data version, the usage rules and the external-search policy; follow them.
2. Follow the `pathtrove-data` skill for the tools and the rules that apply everywhere. When the user wants datasets recommended for a research need, also follow the `pathtrove-best-data` skill.
3. Go outside PathTrove only as that policy allows, and label what you found outside as not curated by PathTrove.

If the request is empty ("/pathtrove" or "$pathtrove" alone), say in a few lines what PathTrove can do for this user (find datasets for a need, counts and overviews, check one dataset, access and download, label files), state the data version, and suggest two or three questions they could ask next.
