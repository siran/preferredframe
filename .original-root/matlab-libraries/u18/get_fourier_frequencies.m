% Parameters
L = length(xts);  % Length of signal (use all data points)
Fs = 1/3;  % Sampling frequency (1 pic every 3 sec)
T = 1/Fs;  % Sample time
t = (0:L-1)*T;  % Time vector

% Replace NaN values with 0
p(isnan(p)) = 0;

% Select all data points
x = xts;
y = p;

% Compute Fourier transform
NFFT = 2^nextpow2(L);  % Next power of 2 from length of y
Y = fft(y, NFFT) / L;
f = Fs * (0:NFFT-1) / NFFT;

% Convert frequency to period (in seconds)
period = 1 ./ f;

% Plot single-sided amplitude spectrum
figure;
plot(period(2:NFFT/2), abs(Y(2:NFFT/2)))
set(gca, 'YScale', 'log')  % Set y-axis to log scale

title('Fourier Transform')
xlabel('Period (seconds)')
ylabel('|Y(f)|')
xlim([0, 200])  % Zoom in to display periods from 2.5 minutes to 5 minutes (150 to 300 seconds)
