# Real-time BCI Control of Waveshare Alphabot2-Pi using g.Tec Unicorn Hybrid EEG Headset

This project implements a real-time Brain-Computer Interface (BCI) to control the **Waveshare Alphabot2-Pi** using **Steady-State Visually-Evoked Potential (SSVEP)** patterns. The system utilizes an **8-channel g.Tec Unicorn Hybrid EEG headset** to record brain activity, which is then transmitted via a **UDP port** to a **Raspberry Pi-enabled Waveshare Alphabot2 robot** for processing and control.

## How It Works

### 1. SSVEP Stimuli Generation
A set of flickering checkerboard patterns is generated using a Python script, [`ssvep_bci.py`](ssvep_bci.py), which leverages python package to:
- Create flickering visual stimuli at specific frequencies.
- **Lock** the display monitor's frames per second (FPS) to maintain precise stimulus frequencies.

### 2. EEG Signal Acquisition
- The **occipital region** of the brain responds to the flickering stimuli with a corresponding harmonic frequency.
- This signal is captured using the **g.Tec Unicorn Hybrid EEG headset** (sampling rate: **250 Hz**).
- The EEG data is synchronized via the **LabStreamingLayer (LSL) framework** and recorded using **Simulink**.

### 3. Signal Processing & Robot Control
- The EEG signals are recorded and processed in two ways: 1) Offline processing to get an idea of how the data looks like. 2) Online processing to utilize the data in real-time.
- Frequency analysis (can be changed to Power Spectral Density or Welsh Periodogram for better results) to identify the dominant frequency corresponding to the visual stimulus.
- For real-time, processed signal is transmitted via a **UDP socket** to the Raspberry Pi controlling the **Waveshare Alphabot2**.
- Based on the detected frequency, appropriate movement commands are sent to the robot.

## Dependencies

### Hardware:
- g.Tec Unicorn Hybrid EEG Headset
- Waveshare Alphabot2-Pi (Raspberry-Pi enabled)

### Software & Libraries:
- Python (`pygame`, `numpy`, `scipy.signal`, `socket`)
- Unicorn Hybrid Suite software (Available from g.Tec website)
- Unicorn Hyrbid Suite LSL API (Available from the software bundle, Guide: https://github.com/unicorn-bi/Unicorn-Network-Interfaces-Hybrid-Black/blob/main/LSL/unicorn-lsl-interface.md)
- Built LabStreamingLayer (LSL) framework (for MATLAB) for the Unicorn software (Available here: https://github.com/labstreaminglayer/liblsl-Matlab.git)
- MATLAB & Simulink (`DSP System Toolbox`, `Signal Processing Toolbox`, `Simulink Real-Time`)
- Alternatively, Unicron UDP interface can also be used. **(NOT USED IN THIS REPOSITORY)** (Guide on how to use it: https://github.com/unicorn-bi/Unicorn-Network-Interfaces-Hybrid-Black/blob/main/UDP/unicorn-udp-interface.md)

## Getting Started (For Real-Time Processing)

1. Run the **SSVEP stimulus generation script**:
   ```bash
   python ssvep_bci.py
   ```

2. Ensure the **g.Tec Unicorn Headset** is properly calibrated and connected using the software suite.

3. Start Simulink and open the model file **`record_realtime_model.slx`** for signal acquisition (real-time processing).

4. Configure the UDP port and the MATLAB Function block.
  
5. Run the Simulink file and the subject should focus on one of the stimulus frequency to observe the **Alphabot2 responding** to SSVEP-based commands.

## File Structure
```
├── ssvep_bci.py                 # Python script for generating SSVEP stimuli
├── README.md                    # Project documentation
├── udp.py                       # Using UDP on python script (requires Unicorn Python API )
```

