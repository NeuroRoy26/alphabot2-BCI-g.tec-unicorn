clear;
close all;
clc;

brain_areas = {'time-modell', 'time-lsl', 'EEG 1 Fz', 'EEG 2 C3', 'EEG 3 Cz', 'EEG 4 C4', 'EEG 5 Pz', 'EEG 6 PO7', 'EEG 7 Oz', 'EEG 8 PO8', 
 };

fs = 250;

data = load('Group1_Rec2_10Hz_13.12.2024.mat');
data = data.y;
trim = fs * 1; %1 sec to remove beginning artifact
data = data(:, trim+1:end);
segment_length_trimmed = size(data, 2);
time_vector = (0:segment_length_trimmed-1) / fs;

% Detrend and filter data
detrended_data(3:10, :) = detrend(data(3:10, :));

% Bandpass filter
cutoff_low = 7;
cutoff_high = 20;
bandpass = fir1(1000, [cutoff_low cutoff_high]/(fs/2), 'bandpass');

filtered_data = data;

for ch = 3:10
    filtered_data(ch, :) = filtfilt(bandpass, 1, data(ch, :));
    %filtered_data(ch, :) = filtered_data(ch, :) - mean(filtered_data(ch, :));
end

% for ch = 3:10
%     figure;
%     plot(time_vector,filtered_data(ch,:));
%     title(['Filtered and EQ Channel ', brain_areas{ch}]);
% end

%stft_eeg = zeros(10,length(filtered_data));

channel_oz = data(9, :);

win_len_s = 2;
window = hamming(fs*win_len_s);
overlap = length(window)/2;

for ch = 7:10
    filtered_data(ch, :) = filtered_data(ch, :) - mean(filtered_data(ch, :));

    [stft_eeg,f1,t1] = stft(filtered_data(ch, :),fs,Window=window,OverlapLength=overlap,FFTLength=2560,FrequencyRange="onesided");
    
    stft_eeg = abs(stft_eeg);

    figure
    imagesc(t1,f1,stft_eeg);
    title(['STFT Channel ', brain_areas{ch}]);
    xlabel('Time [s]');ylabel('Frequency [Hz]');
    ylim([cutoff_low cutoff_high]);
end

