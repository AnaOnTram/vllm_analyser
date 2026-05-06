# VLLM Performance Analyser
A automated script that extract key performance metrics from vllm serving logs.

## Quick Start
```
git clone https://github.com/AnaOnTram/vllm_analyser.git #clone the directory
cd vllm_analyser
```
Copy your vllm log and save it a txt file. 
```
python log_analysis.py #for vllm
#or
python engine.py #for vllm & sglang
```

## Sample Outputs
1. basic statistics
```bash
Average Decode Speed: 16.272289156626506
Decode Speed Standard Deviation: 6.470727957935853
MTP Avarage Acceptance Rate: 40.05802469135803%
MTP Acceptance Rate Standard Deviation: 14.989561903183919%
You may consider decrease "num_speculative_tokens" value to increase decode performance.
```
2. plot
<img src='Assets/nvidia_NVIDIA-Nemotron-3-Super-120B-A12B-NVFP4_perf.png'>

3. [sorted csv](Assets/nvidia_NVIDIA-Nemotron-3-Super-120B-A12B-NVFP4_performance.csv)

## Model inference engine support
- [x] vllm
- [x] sglang
- [ ] llama.cpp
