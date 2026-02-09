# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2026-02-09

### Fixed
- **CRITICAL:** Corrected ANSI escape sequence filtering to include VT100 codes (`ESC 7`, `ESC 8`)
- Fixed spurious empty line appearing at start of every streaming command
- Resolved issue where streaming data appeared all at once instead of line-by-line
- Fixed parsing error "z78" (command echo concatenating with first data line)
- Corrected prompt detection in buffer (now works with or without `\n` after prompt)

### Added
- **Hardware Integration Tests:** Complete test suite with real ADMX2001 device (`test_streaming_real_device.py`)
  - Scale tests: 1, 10, 50, and 100 data points
  - Display mode validation: modes 0, 6, 7, and 9
  - Performance metrics with throughput reporting
- **Continuous Stress Test:** Long-running stability validation (`test_continuous_performance.py`)
  - Configurable iteration count (default: 100)
  - Memory leak detection
  - Sustained performance measurement (achieved 100% stability over 20 iterations)
- **Complete Documentation:** Test results and findings documented in `TEST_RESULTS.md`
  - Performance metrics (9.0 lines/second average)
  - Hardware limitations discovered (~100 point maximum per sweep)
  - Configuration recommendations

### Changed
- **Improved ANSI regex** in `lib/device_state.py` (lines 248-259)
  - Now captures: CSI sequences, OSC sequences, and VT100 single-character escapes
  - Pattern: `[0-9@-_]` to include digits for VT100 cursor save/restore codes
- Echo filtering logic now handles both exact match and concatenated cases
- Streaming timeout increased to 3600s for large-scale tests
- Added detailed logging for empty line detection (warning level)

### Validated
- ✅ Real-time streaming with hardware: **100% success rate**
- ✅ Graph data persistence between polling intervals
- ✅ Automatic graph clearing on new sweep start  
- ✅ Throughput: **9.0 lines/second** (stable)
- ✅ All ANSI codes filtered correctly (including VT100)
- ✅ Second command execution works without hanging
- ✅ Prompt detection reliable in all scenarios

### Technical Details
- FTDI USB-UART connection validated (TTL-232R-3V3 @ 115200 baud)
- Linux environment tested (`/dev/ttyUSB1`)
- Python 3.8+ compatibility maintained

---

## [1.0.0] - 2026-01-23

### Added
- Initial release of ZORIA
- Web-based dashboard for EVAL-ADMX2001 impedance analyzer
- Real-time impedance measurement interface
- Automatic frequency sweep functionality (linear and logarithmic)
- Interactive Bode plots (magnitude and phase)
- Interactive Nyquist plots (complex plane visualization)
- RLC circuit simulator with series and parallel configurations
- Support for R, L, C, RC, RL, LC, and RLC circuit calculations
- Session persistence with automatic graph restoration
- CSV data export with timestamps
- Responsive design for desktop, tablet, and mobile devices
- Integrated documentation with user guides
- Multi-language support (English/Spanish)
- Automatic device detection and connection handling
- Calibration management system (open, short, load)
- Parameter control interface (frequency, amplitude, averaging)
- Error handling and validation system

### Technical Details
- Python 3.8+ compatibility
- Dash-SPA framework for single-page application
- Serial communication via PySerial
- Plotly for interactive visualizations
- Bootstrap (Volt theme) for UI components

### Supported Features
- Frequency range: 0.2 Hz to 10 MHz
- Measurement modes: Z-θ, R-X, Cp-D, Cs-D, Lp-Q, Ls-Q, Y-θ
- Automatic ranging and averaging
- Real-time data streaming
- Browser-based session storage

## [Unreleased]

### Planned for v1.1.0
- Automated calibration wizard with step-by-step guide
- Advanced curve fitting tools (Cole-Cole, Randles circuit)
- Batch measurement processing for multiple samples
- REST API for remote control and automation
- Extended file format support (JSON, HDF5)
- Data analysis tools (FFT, filtering, smoothing)
- Measurement templates and presets
- Cloud storage integration
- Multi-device support
- Advanced plotting options (3D plots, waterfalls)

### Planned for v1.2.0
- Machine learning-based component identification
- Automated report generation (PDF, HTML)
- Database integration for measurement history
- User account system for multi-user environments
- Collaborative features (shared measurements, annotations)
- Mobile app companion
- Hardware trigger support
- External sensor integration

---

## Version Numbering

- **Major version (X.0.0)**: Incompatible API changes or major redesigns
- **Minor version (0.X.0)**: New features, backward compatible
- **Patch version (0.0.X)**: Bug fixes, backward compatible

## Links

- [Repository](https://github.com/mario1027/ZORIA)
- [Issues](https://github.com/mario1027/ZORIA/issues)
- [Releases](https://github.com/mario1027/ZORIA/releases)
