Fsh = 1000;                    % Sampling frequency
Th = 1/Fsh;                     % Sample time
Lh = 1000;                     % Length of signal
th = (0:Lh-1)*Th;                % Time vector
% Sum of a 50 Hz sinusoid and a 120 Hz sinusoid
xh = 0.7*sin(2*pi*50*th) + sin(2*pi*120*th); 
yh = xh + 2*randn(size(th));     % Sinusoids plus noise
plot(Fsh*th,yh)
title('Signal Corrupted with Zero-Mean Random Noise')
xlabel('time (milliseconds)')


NFFTh = 2^nextpow2(Lh); % Next power of 2 from length of y
Yh = fft(yh,NFFTh)/Lh;
fh = Fsh/2*linspace(0,1,NFFTh/2+1);

% Plot single-sided amplitude spectrum.
plot(fh,2*abs(Yh(1:NFFTh/2+1))) 
title('Single-Sided Amplitude Spectrum of y(t)')
xlabel('Frequency (Hz)')
ylabel('|Y(f)|')