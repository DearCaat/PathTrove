---
name: pathtrove
description: Entry point when the user calls PathTrove by name - "/pathtrove ...", "$pathtrove ...", "use PathTrove", "用 PathTrove 查", "在 PathTrove 里找". Use the PathTrove database of computational-pathology datasets for the request (resource table, resource reports, download guides, label files) through the pathtrove MCP tools, even when the question itself does not mention pathology. With no question, introduce what PathTrove can do. In Chinese or English.
---

# PathTrove (entry)

The user asked for PathTrove by name: they want PathTrove used for this request, not the answer limited to it. Only an explicit limit ("in PathTrove", "only PathTrove") keeps the answer inside PathTrove. Read the request as being about computational-pathology data even if it does not say so: "a small dataset I can download without applying" means a computational-pathology dataset, not a general-purpose one.

1. Call `pathtrove_version` with `lang` = the language the user writes in. It returns the data version, what this plugin is for and the usage rules; follow them.
2. Follow the `pathtrove-data` skill for the tools and the rules that apply everywhere. When the user wants datasets recommended for a research need, also follow the `pathtrove-best-data` skill.
3. PathTrove is one source and a partial one (see what this plugin is for). Whether to also use other sources is your judgement. Put outside material in its own section.

If the request is empty ("/pathtrove" or "$pathtrove" alone), say in a few lines what PathTrove can do for this user (find datasets for a need, counts and overviews, check one dataset, access and download, label files), state the data version, and suggest two or three questions they could ask next.
