# ZORIA

**Web-Based Interactive Dashboard for Impedance Analysis and Circuit Characterization**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Dash](https://img.shields.io/badge/Dash-SPA-green.svg)](https://dash.plotly.com/)

---

## 📋 Overview

ZORIA is an open-source web platform that transforms the **EVAL-ADMX2001** impedance analyzer (Analog Devices) into a modern measurement system with real-time scientific visualization. It integrates a **measurement dashboard** and an **RLC simulator** in a responsive web interface built with Dash-SPA.

### Key Features
- 🔌 **Automatic communication** with EVAL-ADMX2001 via serial port
- 📊 **Real-time visualization** with Bode and Nyquist diagrams
- 🔄 **Automatic frequency sweeps** (linear/logarithmic, 0.2 Hz - 10 MHz)
- 💾 **Session persistence** with automatic graph restoration
- 📤 **CSV export** for post-processing and external analysis
- 🧮 **RLC simulator** for circuit design and experimental planning
- 📱 **Responsive design** optimized for desktop, tablet, and mobile
- 📖 **Integrated documentation** with comprehensive user guides
- 🌐 **Multi-language support** (English/Spanish)

---

## 🚀 Quick Start

### Prerequisites

#### Hardware
- **EVAL-ADMX2001** Evaluation Kit:
  - ADMX2001B impedance analyzer module
  - EVAL-ADMX2001EBZ evaluation board
  - UART-to-USB cable (included)
  - LCR test probes

#### Software
- Python 3.8 or higher
- Operating System: Linux, Windows, or macOS
- Serial port access permissions

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/mario1027/ZORIA.git
cd ZORIA
```

2. **Create and activate virtual environment**
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

### Running the Application

```bash
python app.py
```

The application will be available at: **http://localhost:8050**

---

## 🏗️ Architecture

ZORIA implements a modular three-layer architecture for scalability and maintainability:

### 1. Hardware Layer
- Serial communication with EVAL-ADMX2001 via UART protocol
- Command parsing and validation
- Data acquisition and sweep control
- Automatic device detection and connection handling

### 2. Backend (Python)
```
lib/
├── admx2001.py       # Main device control class with UART interface
├── calibration.py    # Calibration management (open/short/load)
├── utils.py          # Validation, parsing, and processing utilities
├── enums.py          # Constants, modes, and configuration enums
└── exceptions.py     # Custom exception hierarchy
```

### 3. Frontend (Dash-SPA)
```
pages/
├── dashboard/        # Real-time measurement interface
├── simulator/        # RLC impedance calculator
├── documentation/    # Integrated user documentation
└── common/          # Reusable UI components (sidebar, navigation, footer)
```

---

## 📊 Features

### Measurement Dashboard
- ✅ Automatic device connection with error handling
- ✅ Single-point impedance measurements
- ✅ Frequency sweeps (linear/logarithmic, 0.2 Hz - 10 MHz)
- ✅ Interactive Bode plots (magnitude and phase)
- ✅ Interactive Nyquist plots (complex plane)
- ✅ Real-time parameter control (frequency, amplitude, averaging)
- ✅ Data export to CSV format with timestamps
- ✅ Browser session persistence and graph restoration

### RLC Simulator
- ✅ Theoretical impedance calculation for circuit design
- ✅ Series and parallel configurations
- ✅ Individual components: R, L, C
- ✅ Combined circuits: RC, RL, LC, RLC
- ✅ Outputs: magnitude, phase, real/imaginary parts
- ✅ Side-by-side comparison with experimental measurements
- ✅ Interactive Bode and Nyquist visualization

### Integrated Documentation
- ✅ Quick start guide with hardware setup
- ✅ Hardware specifications and limitations
- ✅ Command reference and API documentation
- ✅ Calibration procedures (open, short, load)
- ✅ Practical measurement examples
- ✅ External resources and references

---

## 📁 Project Structure

```
ZORIA/
├── app.py                      # Application entry point
├── requirements.txt            # Python dependencies
├── themes.py                   # Bootstrap theme configuration
│
├── lib/                        # ADMX2001 control library
│   ├── __init__.py
│   ├── admx2001.py            # Main device class
│   ├── calibration.py         # Calibration manager
│   ├── enums.py               # Constants and enums
│   ├── exceptions.py          # Custom exceptions
│   └── utils.py               # Utility functions
│
├── pages/                      # Application pages
│   ├── dashboard/             # Measurement dashboard
│   │   └── dashboard_page.py
│   ├── simulator/             # RLC simulator
│   │   ├── simulator_page.py
│   │   ├── impedance_calculator.py
│   │   └── components.py
│   ├── documentation/         # Integrated docs
│   │   └── documentation_page.py
│   └── common/                # Shared components
│       ├── sidebar.py
│       ├── mobile_nav.py
│       ├── footer.py
│       └── bread_crumbs.py
│
├── assets/                     # Static resources
│   ├── css/                   # Custom stylesheets
│   │   ├── navigation.css
│   │   ├── mobile-nav.css
│   │   └── sweep-controls.css
│   └── images/                # Images and logos
│
├── config/                     # Configuration files
│   └── spa_config.ini
│
└── data/                       # Data storage (auto-generated)
    └── sweep_data_*.csv       # Exported measurements
```

---

## 🔧 Usage

### 1. Connect to Device

```python
from lib import ADMX2001

# Initialize and connect to device
device = ADMX2001(port='/dev/ttyUSB0', baudrate=115200)
device.connect()

# Verify connection
identity = device.get_identity()
print(f"Connected to: {identity}")
```

### 2. Perform Single Measurement

```python
# Configure measurement parameters
device.set_frequency(1000)      # 1 kHz
device.set_magnitude(1.0)       # 1 V peak
device.set_average(10)          # Average 10 samples

# Measure impedance
measurement = device.measure_impedance()
print(f"Z = {measurement['magnitude']:.2f} Ω")
print(f"θ = {measurement['phase']:.2f}°")
print(f"R = {measurement['real']:.2f} Ω")
print(f"X = {measurement['imaginary']:.2f} Ω")
```

### 3. Execute Frequency Sweep

```python
from lib import SweepType, SweepScale

# Configure logarithmic frequency sweep
device.configure_sweep(
    sweep_type=SweepType.FREQUENCY,
    scale=SweepScale.LOGARITHMIC,
    start=100,          # 100 Hz
    stop=100000,        # 100 kHz
    points=100
)

# Execute sweep and get results
results = device.execute_sweep()

# Export to CSV
device.export_csv('measurement_data.csv', results)
```

### 4. Use RLC Simulator

```python
from pages.simulator.impedance_calculator import ImpedanceCalculator

# Create calculator with frequency range
calc = ImpedanceCalculator(
    freq_start=10,
    freq_end=100000,
    points=1000
)

# Calculate impedance for RC series circuit
Z = calc.rc_series(R=1000, C=1e-6)  # 1kΩ, 1µF

# Get Bode plot data
bode_data = calc.get_bode_data(Z)
magnitude = bode_data['magnitude']
phase = bode_data['phase']

# Get Nyquist plot data
nyquist_data = calc.get_nyquist_data(Z)
real = nyquist_data['real']
imag = nyquist_data['imaginary']
```

### 5. Calibration Procedures

```python
from lib.calibration import CalibrationManager

# Initialize calibration manager
cal_manager = CalibrationManager(device)

# Perform open calibration
print("Remove all connections from test terminals")
cal_manager.calibrate_open()

# Perform short calibration
print("Connect short circuit to test terminals")
cal_manager.calibrate_short()

# Perform load calibration (50Ω)
print("Connect 50Ω load to test terminals")
cal_manager.calibrate_load(50)

# Save calibration data
cal_manager.save_calibration('my_calibration.json')
```

---

## 🧪 Use Cases

### 1. RLC Resonator Characterization
Measure resonance frequency, quality factor (Q), and bandwidth in resonant circuits for RF applications and filter design.

**Example**: Characterize a series RLC resonator at 10 kHz with Q > 100.

### 2. Battery Analysis (EIS)
Electrochemical Impedance Spectroscopy to determine State of Health (SOH) and State of Charge (SOC) for battery management systems.

**Example**: Analyze lithium-ion battery impedance across 0.1 Hz - 10 kHz to detect aging effects.

### 3. Material Characterization
Measure dielectric properties, conductivity, and loss tangent of materials as a function of frequency.

**Example**: Characterize dielectric constant of PCB substrate material from 1 MHz to 10 MHz.

### 4. Filter and Matching Network Design
Verify characteristic impedance, insertion loss, and S-parameters of filters and impedance matching networks.

**Example**: Validate 50Ω matching network for antenna tuning in the 100-200 MHz range.

### 5. Sensor Development
Impedance-based sensor characterization for biosensors, chemical sensors, and environmental monitoring.

**Example**: Develop impedimetric biosensor with detection range optimization.

---

## 📊 Measurement Modes

ZORIA supports all EVAL-ADMX2001 measurement modes:

| Mode | Parameter 1 | Parameter 2 | Application |
|------|-------------|-------------|-------------|
| **Z-θ** | Magnitude | Phase | General impedance |
| **R-X** | Resistance | Reactance | Circuit analysis |
| **Cp-D** | Parallel C | Dissipation | Capacitor testing |
| **Cs-D** | Series C | Dissipation | Capacitor testing |
| **Lp-Q** | Parallel L | Quality factor | Inductor testing |
| **Ls-Q** | Series L | Quality factor | Inductor testing |
| **Y-θ** | Admittance | Phase | Network analysis |

---

## 🛠️ Configuration

### Serial Port Configuration

Edit `config/spa_config.ini`:

```ini
[hardware]
port = /dev/ttyUSB0  # Windows: COM3, macOS: /dev/cu.usbserial
baudrate = 115200
timeout = 1.0
```

### Application Settings

```ini
[application]
host = 127.0.0.1
port = 8050
debug = False
```

### Measurement Defaults

```ini
[measurement]
default_frequency = 1000  # Hz
default_amplitude = 1.0   # V
default_averaging = 10
auto_range = True
```

---

## 🧪 Testing

### Run Unit Tests

```bash
pytest tests/ -v
```

### Run Integration Tests

```bash
pytest tests/integration/ -v --hardware
```

Note: Integration tests require connected EVAL-ADMX2001 hardware.

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/amazing-feature
   ```
3. **Commit your changes**
   ```bash
   git commit -m 'Add amazing feature'
   ```
4. **Push to the branch**
   ```bash
   git push origin feature/amazing-feature
   ```
5. **Open a Pull Request**

### Contribution Guidelines
- Follow PEP 8 style guide for Python code
- Add unit tests for new features
- Update documentation for API changes
- Ensure all tests pass before submitting PR
- Use descriptive commit messages

---

## 📜 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

---

## 👥 Authors

- **Mario Ricardo Montero** - *Lead Developer* - [GitHub](https://github.com/mario1027)
- **Juan Carlos Alvarez** - *Contributor*
- **Francisco J. Racedo N.** - *Contributor*

---

## 📧 Contact & Support

- **Email**: mariomontero942@gmail.com
- **Issues**: [GitHub Issues](https://github.com/mario1027/ZORIA/issues)
- **Documentation**: Available at http://localhost:8050/documentation when app is running
- **Discussions**: [GitHub Discussions](https://github.com/mario1027/ZORIA/discussions)

---

## 🙏 Acknowledgments

- **Analog Devices** for the EVAL-ADMX2001 platform and documentation
- **Plotly Dash** for the excellent visualization framework
- **Bootstrap** (Volt theme) for UI components
- **Open-source community** for the tools and libraries that made this possible

---

## 📚 Citations

If you use ZORIA in your research, please cite:

```bibtex
@software{zoria2025,
  author = {Montero, Mario Ricardo and Alvarez, Juan Carlos and Racedo, Francisco J.},
  title = {ZORIA: Web-Based Interactive Dashboard for Impedance Analysis},
  year = {2025},
  publisher = {GitHub},
  url = {https://github.com/mario1027/ZORIA}
}
```

---

## 📅 Version History

### v1.0.0 (January 2026)
- ✅ Initial release
- ✅ Functional measurement dashboard
- ✅ Complete RLC simulator
- ✅ Integrated documentation
- ✅ Automatic frequency sweeps
- ✅ Real-time Bode/Nyquist visualization
- ✅ Session persistence
- ✅ CSV data export

### Roadmap (v1.1.0)
- 🔄 Automated calibration wizard
- 🔄 Advanced curve fitting tools
- 🔄 Batch measurement processing
- 🔄 REST API for remote control
- 🔄 Extended file format support (JSON, HDF5)

---

## 🔗 Related Projects

- [PyMeasure](https://github.com/pymeasure/pymeasure) - Scientific instrument automation
- [SciPy](https://scipy.org/) - Scientific computing tools
- [Plotly](https://plotly.com/) - Interactive graphing library

---

## ⚠️ Disclaimer

This software is provided "as is" without warranty of any kind. Use at your own risk. Always verify measurements with calibrated equipment for critical applications.

---

**⭐ If you find this project useful, please consider giving it a star on GitHub!**

[![Star History Chart](https://api.star-history.com/svg?repos=mario1027/ZORIA&type=Date)](https://star-history.com/#mario1027/ZORIA&Date)
