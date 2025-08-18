% calcula transformada de fourier de (xts,p)

% los primeros 8690 puntos se borran porque fueron tomados con otra
% frecuencia de sampleo
x = xts(1:size(xts));
y = p(1:size(xts));

L = size(x,1); % Length of signal 

Fs = 2*24*60;   % veces por minuto, Sampling frequency
T = 1/Fs;       % Sample time
t = (0:L-1)*T;  % Time vector

% y = y ;%+ sin(2*pi*1.1*t)';

NFFT = 2^nextpow2(L); % Next power of 2 from length of y
Y = fft(y,NFFT)/L;
f = Fs/2*linspace(0,1,NFFT/2+1);

% Plot single-sided amplitude spectrum.
plot(f,2*abs(Y(1:NFFT/2+1))) 
title('Transformada de Fourier')
xlabel('Frecuencia (veces por dia)')
ylabel('|Y(f)|')

% espero frecuencias del orden de 1 dia
xlim([0.7 2]);