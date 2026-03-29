# BCI Pipeline to control Raspberry Pi in real-time

This project implements a real-time Brain-Computer Interface (BCI) to control the **Waveshare Alphabot2-Pi** using **Steady-State Visually-Evoked Potential (SSVEP)** patterns. The system utilizes an **8-channel g.Tec Unicorn Hybrid EEG headset** to record brain activity, which is then transmitted via a **UDP port** to a **RaspberryPi-integrated Waveshare Alphabot2 robot** for processing and control.

## How It Works

### 1. SSVEP Stimuli Generation
A set of flickering checkerboard patterns is generated using a Python script, `ssvep_generator.py`, to:
- Create flickering visual stimuli at specific frequencies.
- Run stimuli in a frame-locked mode (display-limited) for improved timing stability.

### 2. EEG Signal Acquisition
- The **occipital region** of the brain responds to the flickering stimuli with a corresponding harmonic frequency.
- This signal is captured using the **g.Tec Unicorn Hybrid EEG headset** (sampling rate: **250 Hz**).
- The EEG data can be synchronized via the **LabStreamingLayer (LSL) framework** and recorded using **Simulink**.

### 3. Signal Processing & Robot Control
- The EEG signals are recorded and processed in two ways: 1) Offline processing to get an idea of how the data looks like. 2) Online processing to utilize the data in real-time.
- Frequency analysis (can be changed to Power Spectral Density or Welch Periodogram for better results) to identify the dominant frequency corresponding to the visual stimulus.
- For real-time, processed signal is transmitted via a **UDP socket** to the Raspberry Pi controlling the **Waveshare Alphabot2**.
- Based on the detected frequency, appropriate movement commands are sent to the robot.

## Dependencies

### Hardware:
- g.Tec Unicorn Hybrid EEG Headset
- Waveshare Alphabot2-Pi (Raspberry-Pi enabled)

### Software & Libraries:
- Python (see `requirements.txt`)
- Unicorn Hybrid Suite software (Available from g.Tec website)
- Unicorn Hybrid Suite LSL API (Available from the software bundle)
- LabStreamingLayer (LSL) for MATLAB (Available here: https://github.com/labstreaminglayer/liblsl-Matlab.git)
- MATLAB & Simulink (`DSP System Toolbox`, `Signal Processing Toolbox`, `Simulink Real-Time`)

## Getting Started (Stimulus Only)

```bash
python ssvep_generator.py --fullscreen --fps 60
```

Controls:
- `SPACE`: cycle target (fixation, up, right, down, left)
- `A`: toggle auto-switch
- `F`: toggle fullscreen
- `ESC`: quit

## Getting Started (For Real-Time Processing)

1. Run the SSVEP stimulus script (above).
2. Ensure the **g.Tec Unicorn Headset** is properly calibrated and connected using the software suite.
3. Start Simulink and open the model file **`record_realtime_model.slx`** for signal acquisition (real-time processing).
   - **Note:** `record_realtime_model.slx` is not included in this repository.
4. Configure the UDP port and the MATLAB Function block.
5. Run the Simulink file and the subject should focus on one of the stimulus frequency to observe the **Alphabot2 responding** to SSVEP-based commands.

## File Structure
```
├── README.md                    # Project documentation
├── ssvep_generator.py           # Python script for generating SSVEP stimuli
├── ssvep_gen_MATLAB.m           # MATLAB script for offline STFT visualization
├── udp.py                       # Python script for UDP
├── requirements.txt             # Python dependencies
```

This work was achieved because of the support from Systems Neuroscience & Neurotechnology Unit, HTW Saar.