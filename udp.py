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
            received_array = np.frombuffer(data, dtype=np.float32)

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
                fft_max = np.max(positive_fft)
                fft_min = np.min(positive_fft)
                fft_range = fft_max - fft_min

                # Avoid division by zero if all FFT values are the same
                if fft_range == 0:
                    scaled_magnitudes = np.zeros_like(positive_fft)
                else:
                    # Normalize and clip the values to be between 0 and 255
                    scaled_magnitudes = ((positive_fft - fft_min) / fft_range) * 255
                    scaled_magnitudes = np.clip(scaled_magnitudes, 0, 255)

                # Debugging: Print scaled magnitudes before conversion
                print("Scaled FFT magnitudes (0-255):")
                print(scaled_magnitudes[:10])  # Print first 10 values for inspection

                # Convert to uint8 for UDP transmission
                uint8_magnitudes = scaled_magnitudes.astype(np.uint8)

                freqs = np.fft.fftfreq(len(last_five_seconds_data), 1 / fs)[:len(positive_fft)]
                peak_indices, _ = find_peaks(positive_fft)
                peak_freqs = freqs[peak_indices]
                magnitudes = positive_fft[peak_indices]

                # Filter peaks in the 6-20 Hz range
                valid_indices = np.where((peak_freqs >= low_cutoff) & (peak_freqs <= high_cutoff))
                filtered_freqs = peak_freqs[valid_indices]
                filtered_magnitudes = magnitudes[valid_indices]

                if len(filtered_freqs) > 0:
                    # Sort by magnitude
                    sorted_indices = np.argsort(filtered_magnitudes)[-3:][::-1]  # Top 3 peaks
                    print("Top 3 peak frequencies (6-20 Hz) over the last 5 seconds:")

                    if mean_peak_cnt == 20:  # Moving average?
                        mean_peak = 0
                        mean_peak_cnt = 0

                    for i, idx in enumerate(sorted_indices):
                        print(f"Peak {i+1}: {filtered_freqs[idx]:.2f} Hz with magnitude {filtered_magnitudes[idx]:.2f}")
                        mean_peak_cnt += 1
                        mean_peak += filtered_freqs[idx]
                        print(f"Total mean peak : {mean_peak // mean_peak_cnt} Hz")
                else:
                    print("No peaks detected in the 6-20 Hz range.")

        except Exception as e:
            print(f"Error: {e}")

except KeyboardInterrupt:
    print("\nTerminated by user.")
