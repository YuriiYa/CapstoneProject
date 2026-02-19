# Raspberry Pi 5 AI HAT+ Requirements

## Hardware Specifications

### Raspberry Pi 5
- **CPU**: Broadcom BCM2712 (Quad-core Cortex-A76 @ 2.4GHz)
- **RAM**: 8GB LPDDR4X
- **Storage**: microSD card (64GB+ recommended) or NVMe SSD via PCIe
- **Power**: 5V/5A USB-C power supply (27W recommended for AI HAT+)

### Power Supply Options

#### Option 1: Standard USB-C PD Power Supply
- **Specification**: 27W (5V/5A) USB-C PD adapter
- **Pros**: Simple, direct connection, widely available
- **Cons**: Requires wall outlet, no battery backup
- **Recommended for**: Desktop/stationary setups

#### Option 2: 52Pi PD Power HAT
- **Model**: RPi 5 PD Power expansion board
- **Power Output**: 40W (5V/8A MAX) via USB-C
- **Input Options**:
  - USB PD: 15V default input
  - DC Interface: 9-24V (1.3mm x 4.2mm connector)
- **Features**:
  - Always-ON switch for automatic startup on power restoration
  - Manual power control via push-button
  - Long-press shutdown capability
  - Supports PD 3.0 (5.15V@5A output)
- **Pros**: 
  - Sufficient power (40W > 27W required)
  - Flexible input options (USB PD or DC)
  - Power management features
  - Can be powered by portable battery packs with PD support
- **Cons**: 
  - Additional hardware cost
  - Requires careful installation to avoid conflicts with AI HAT+
- **Installation Note**: Use the 52Pi's USB-C output port to power the Pi 5's USB-C input, rather than stacking it on the GPIO/HAT connector. This keeps the HAT+ connector free for the AI HAT+.
- **Recommended for**: Portable setups, battery-powered applications, or systems requiring automatic power management

### AI HAT+ (Hailo-8L)
- **NPU Performance**: 26 TOPS (INT8)
- **Interface**: PCIe Gen 2.0 or Gen 3.0 (via HAT+ connector)
- **Supported Operations**: Convolutions, matrix multiplications, activation functions
- **Power Consumption**: ~2-3W under load

## Software Requirements

### Operating System
- **Raspberry Pi OS** (64-bit, Bookworm or later)
- **Kernel**: 6.1+ with Hailo driver support
- **Python**: 3.9+ for Hailo SDK compatibility

### Hailo Software Stack
- **Hailo Dataflow Compiler**: For model conversion to HEF format
- **HailoRT**: Runtime library for inference
- **Hailo Python API**: Python bindings for model deployment
- **TAPPAS** (optional): Hailo's application framework

### ML Frameworks
- **ONNX Runtime** with Hailo execution provider
- **TensorFlow Lite** (for compatible models)
- **PyTorch** (CPU fallback for unsupported operations)

## Model Requirements

### Gemma Models
- **Gemma 2B**: Quantized to INT8 or INT4
- **Context Length**: 2048-4096 tokens (memory dependent)
- **Format**: Convert to ONNX → Hailo HEF format
- **Quantization**: Post-training quantization (PTQ) required

### Model Optimization
- **Quantization**: INT8 for NPU acceleration
- **Model Pruning**: Optional, for further size reduction
- **Layer Fusion**: Automatic via Hailo compiler
- **Batch Size**: 1 (typical for edge inference)

## Configuration Requirements

### Memory Management
- **Swap**: 2GB swap file (optional with 8GB RAM)
- **Model Loading**: Lazy loading for large models
- **KV Cache**: Optimize cache size based on available RAM (up to 6GB usable)
- **Buffer Management**: Pre-allocate buffers for inference

### NPU Configuration
- **Driver Installation**: Hailo PCIe driver
- **Device Detection**: Verify `/dev/hailo0` device
- **Firmware**: Latest Hailo-8L firmware
- **Power Management**: Disable aggressive power saving for consistent performance

### Thermal Management
- **Cooling**: Active cooling (fan) recommended for sustained workloads
- **Thermal Throttling**: Monitor CPU/NPU temperatures
- **Heat Sinks**: Required for both Pi 5 and AI HAT+

## Performance Expectations

### Inference Speed
- **Gemma 2B (INT8)**: 10-30 tokens/second
- **TinyLlama 1.1B**: 30-50 tokens/second
- **Larger Models (7B+)**: 2-10 tokens/second (heavily quantized)

### Latency
- **First Token**: 200-500ms
- **Subsequent Tokens**: 30-100ms per token
- **Model Loading**: 2-10 seconds depending on model size

### Power Consumption
- **Idle**: ~3-4W (Pi 5 only)
- **Inference**: ~8-12W (Pi 5 + AI HAT+ under load)
- **Peak**: ~15W maximum

## Network Requirements

### Model Download
- **Internet Connection**: Required for initial model download
- **Bandwidth**: 1-5GB for model files
- **Storage**: Local storage for converted models

### Inference Modes
- **Local Inference**: Fully offline capable
- **Hybrid**: Local inference with cloud fallback
- **API Server**: Expose inference via REST API

## Development Environment

### Required Tools
- **Hailo Model Zoo**: Pre-optimized models
- **Hailo Dataflow Compiler**: Model conversion tool
- **Docker** (optional): For containerized deployment
- **Git**: For cloning repositories

### Development Libraries
```bash
# Core dependencies
- hailort
- hailo-platform
- numpy
- onnx
- onnxruntime

# Optional frameworks
- transformers (HuggingFace)
- torch
- tensorflow-lite
```

## Limitations and Considerations

### Hardware Limitations
- **RAM**: Limited to 8GB max, constrains model size
- **NPU**: Not all transformer operations accelerated
- **Storage I/O**: microSD slower than NVMe SSD
- **PCIe Bandwidth**: Gen 2.0 x1 may bottleneck large models

### Software Limitations
- **Model Support**: Not all architectures supported by Hailo
- **Quantization Loss**: Some accuracy degradation with INT8
- **Framework Support**: Limited compared to desktop GPUs
- **Debugging**: Less tooling than CUDA/ROCm ecosystems

### Operational Considerations
- **Model Conversion**: Requires separate compilation step
- **Calibration Data**: Needed for quantization
- **Testing**: Validate accuracy after quantization
- **Updates**: Hailo SDK updates may require model recompilation

## Recommended Configuration

### Optimal Setup
- **Hardware**: Raspberry Pi 5 (8GB) + AI HAT+ + NVMe SSD + active cooling
- **OS**: Raspberry Pi OS 64-bit (latest)
- **Model**: Gemma 2B INT8 quantized
- **Context**: 2048 tokens
- **Deployment**: Docker container with HailoRT

### Alternative Setup
- **Hardware**: Raspberry Pi 5 (8GB) + AI HAT+ + microSD
- **OS**: Raspberry Pi OS 64-bit
- **Model**: TinyLlama 1.1B INT8 or Gemma 2B INT8
- **Context**: 2048 tokens
- **Deployment**: Native Python application

## Next Steps

1. **Hardware Setup**: Assemble Pi 5 + AI HAT+ with proper cooling
2. **Software Installation**: Install Raspberry Pi OS and Hailo SDK
3. **Model Preparation**: Download and convert Gemma model to HEF format
4. **Testing**: Validate inference performance and accuracy
5. **Optimization**: Tune configuration for your specific use case
6. **Deployment**: Package as service or API endpoint
