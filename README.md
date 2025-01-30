# Auto-OPS

[![Documentation](https://img.shields.io/badge/docs-available-brightgreen.svg)](https://pflammarion.github.io/Auto-OPS/)
[![GitHub Actions](https://github.com/pflammarion/Auto-OPS/actions/workflows/test.yml/badge.svg?branch=master)](https://github.com/pflammarion/Auto-OPS/actions/workflows/test.yml)
[![DOI](https://zenodo.org/badge/DOI/10.1109/LES.2024.3513638.svg)](https://doi.org/10.1109/LES.2024.3513638)

## Overview

**Auto-OPS** is a security evaluation framework that automates Optical Probing (OP) attack simulations on full GDS-II design files. It extracts active region geometries of logic cells to evaluate security robustness, eliminating manual and error-prone processes. Auto-OPS enables large-scale OP attack assessments in simulation, making security analysis more efficient and accessible.

## Documentation

Full documentation is available at:  
👉 **[Auto-OPS Documentation](https://pflammarion.github.io/Auto-OPS/)**

## Installation

To install Auto-OPS, follow these steps:

```bash
git clone https://github.com/pflammarion/Auto-OPS.git
cd Auto-OPS
pip install -r requirements.txt
```

## Usage

To run Auto-OPS, use the following command:

```bash
python main.py gui
```

For additional options and configurations, refer to the [Quick Start](https://pflammarion.github.io/Auto-OPS/getting_started/quick-start.html).

## Auto-OPS Paper

You can find the paper at the following link:
[Auto-OPS on IEEE Xplore](https://ieeexplore.ieee.org/document/10793101)

This paper have been published in the 7th International Workshop on Secure Hardware, Architectures, and Software, Barcelona, Spain (**SeHAS 2025**) in
collaboration with IEEE Embedded Systems Letters Journal (**IEEE ESL**) and received the **Best Paper Award**.

## Citing Auto-OPS

If you use Auto-OPS in your research, please cite:

```bibtex
@ARTICLE{10793101,
    author={Flammarion, Paul and Parvin, Sajjad and Torres, Frank Sill and Drechsler, Rolf},
    journal={IEEE Embedded Systems Letters},
    title={Auto-OPS: A Framework For Automated Optical Probing Simulation on GDS-II},
    year={2024},
    doi={10.1109/LES.2024.3513638}
}
```

## Composition Example


https://github.com/user-attachments/assets/5e5c429f-2e1e-4f9a-837b-6c8cc5d8015c

