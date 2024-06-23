% fourier transforms a typical set of points (xts,p)
% xts: "x timestamps"
% p: "positions pixels of interference maxima in a certain timestamp"
% a tuple (xts,p) corresponds to a vector p of the position in pixels of
% interference maxima

x = xts(1:size(xts));
y = p(1:size(xts));

L = size(x,1); % Length of signal 

pics_per_sec = 3;
Fs = 24*60*60/pics_per_sec;   % Sampling frequency
T = 1/Fs;       % Sample time
t = (0:L-1)*T;  % Time vector

NFFT = 2^nextpow2(L); % Next power of 2 from length of y
Y = fft(y,NFFT)/L;
f = Fs/2*linspace(0,1,NFFT/2+1);

% Plot single-sided amplitude spectrum.
plot(f,2*abs(Y(1:NFFT/2+1))) 
title('Fourier transform')
xlabel('Times per day')
ylabel('|Y(f)|')