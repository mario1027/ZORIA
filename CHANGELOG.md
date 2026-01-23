# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
