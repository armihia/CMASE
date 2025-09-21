# CMASE — Computational Multi-Agent Society Experiment

**CMASE (Computational Multi-Agent Society Experiment)** is a research framework for studying the emergence and evolution of **social structures, identities, and trust dynamics** in generative multi-agent systems.
The framework integrates generative agents, virtual ethnography, and reproducible experimental workflows, supporting both qualitative and computational analysis.

<img width="3345" height="2796" alt="fig-framwork" src="https://github.com/user-attachments/assets/aaf797cb-9d51-46cd-9f7f-a06d9eb72c00" />

---

## Research Background

In response to the growing complexity of human–AI interaction and the demand for socially capable agents, CMASE introduces a **researcher-as-participant paradigm**. Human researchers embed themselves within a generative agent society to conduct immersive observation, participatory intervention, and cultural event triggering. This approach enables the study of language practices, power relations, trust mechanisms, and institutional emergence in virtual social fields.

---

## Overview

CMASE supports configurable experimental environments and outputs both raw logs and structured data designed for virtual ethnographic analysis.

---

## Quick Start

```bash
# Clone the repository
git clone https://github.com/armihia/cmase.git
cd cmase

# Install dependencies
pip install -r requirements.txt
```

---

## Setup

Before running CMASE, you must configure your LLM settings. Open `BaseLLM.py` and update your keys and URLs in the `LLM` class:

```python
class LLM:
    def __init__(self):
        self.api_version = "2024-12-01-preview"

        self.openai_api_pool = [
            {
                "openai_api_4o": "Your API Key",
                "azure_endpoint_4o": "Your Azure Endpoint"
            }
        ]

        self.ollama_server_url = "Your Ollama Url"

        self.third_party_url = "Your Third Party LLM Url"
        self.third_party_api = "Your Third Party LLM API Key"
```

You must also build a map before running a simulation. Use the provided script:

```bash
python build_map_demo.py
```

---

## Example Run

After building the map, you can start a demo simulation:

```bash
python start_demo.py
```

![exp3-1_small](https://github.com/user-attachments/assets/ca126ea8-ea05-4937-a4d5-72fd6005e757)


---

## Citation

If you use CMASE in your research, please cite the project or related paper:

```bibtex
@article{zhang2025evolving,
  title={Evolving Collective Cognition in Human-Agent Hybrid Societies: How Agents Form Stances and Boundaries},
  author={Zhang, Hanzhong and Huang, Muhua and Wang, Jindong},
  journal={arXiv preprint arXiv:2508.17366},
  year={2025}
}
```

---

## Contact

Author: **Hanzhong Zhang**
Email: `armihia@foxmail.com`
