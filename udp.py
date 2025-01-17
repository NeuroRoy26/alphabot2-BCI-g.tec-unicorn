import socket
import numpy as np
from scipy.signal import find_peaks
from collections import deque

# Configure the UDP receiver
UDP_IP = "127.0.0.1"
UDP_PORT = 5005
fs = 250  # Sampling rate in Hz
time_window = 1  # Time window for averaging in seconds
samples_per_window = fs * time_window

low_cutoff = 6
high_cutoff = 20

mean_peak_cnt = 0
mean_peak = 0

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

print(f"Listening for data on {UDP_IP}:{UDP_PORT}...")

# Initialize data buffer
last_five_seconds_data = deque(maxlen=samples_per_window)
packet_count = 0

try:
    while True:
        try:
            data, addr = sock.recvfrom(8192)  # Buffer size
            if not data:
                continue

            packet_count += 1

            # Decode received data into a NumPy array
            received_array = np.frombuffer(data[:len(data) - (len(data) % 4)], dtype=np.float32)

            # Append data to the buffer
            last_five_seconds_data.extend(received_array)

            if len(last_five_seconds_data) >= samples_per_window:
                fft_data = np.array(last_five_seconds_data).reshape(-1, len(received_array))
                avg_magnitude = np.mean(np.abs(fft_data), axis=0)
                positive_fft = avg_magnitude[:len(avg_magnitude) // 2]

                # Debugging: Print out the positive_fft values before scaling
                print("Positive FFT magnitudes (before scaling):")
                print(positive_fft[:10])  # Print first 10 values for inspection

                # Scale magnitudes to 0-255 range for UDP transmission
                fft_max, fft_min = np.max(positive_fft), np.min(positive_fft)
                fft_range = max(fft_max - fft_min, 1e-10)  # Prevent division by zero
                scaled_magnitudes = ((positive_fft - fft_min) / fft_range) * 255
                scaled_magnitudes = np.clip(scaled_magnitudes, 0, 255).astype(np.uint8)

                # Debugging: Print scaled magnitudes before conversion
                print("Scaled FFT magnitudes (0-255):")
                print(scaled_magnitudes[:10])  # Print first 10 values for inspection

                # Compute frequency domain values
                freqs = np.fft.fftfreq(len(last_five_seconds_data), 1 / fs)[:len(positive_fft)]
                peak_indices, _ = find_peaks(positive_fft)
                peak_freqs, magnitudes = freqs[peak_indices], positive_fft[peak_indices]

                # Filter peaks in the 6-20 Hz range
                valid_indices = (peak_freqs >= low_cutoff) & (peak_freqs <= high_cutoff)
                filtered_freqs, filtered_magnitudes = peak_freqs[valid_indices], magnitudes[valid_indices]

                if len(filtered_freqs) > 0:
                    # Sort by magnitude and select top 3
                    sorted_indices = np.argsort(filtered_magnitudes)[-3:][::-1]
                    print("Top 3 peak frequencies (6-20 Hz) over the last 5 seconds:")

                    if mean_peak_cnt == 20:  # Reset moving average every 20 cycles
                        mean_peak, mean_peak_cnt = 0, 0

                    for i, idx in enumerate(sorted_indices):
                        freq = filtered_freqs[idx]
                        mag = filtered_magnitudes[idx]
                        print(f"Peak {i+1}: {freq:.2f} Hz with magnitude {mag:.2f}")

                        # Compute moving average properly
                        mean_peak_cnt += 1
                        mean_peak = (mean_peak * (mean_peak_cnt - 1) + freq) / mean_peak_cnt
                        print(f"Total mean peak : {mean_peak:.2f} Hz")
                else:
                    print("No peaks detected in the 6-20 Hz range.")

        except Exception as e:
            print(f"Error: {e}")

