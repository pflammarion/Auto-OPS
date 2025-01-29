# Auto-OPS

[![Documentation](https://img.shields.io/badge/docs-available-brightgreen.svg)](https://pflammarion.github.io/Auto-OPS/)

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

For additional options and configurations, refer to the [documentation](https://pflammarion.github.io/Auto-OPS/).

# Citing Auto-OPS

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
