% fourier transforms a typical set of points (xts,p)
% xts: "x timestamps"
% p: "positions pixels of interference maxima in a certain timestamp"
% a tuple (xts,p) corresponds to a vector p of the position in pixels of
% interference maxima

p(isnan(p))=0;

x = xts(1:length(xts(1:512)));
y = p(1:length(xts(1:512)));

L = size(x,1); % Length of signal 

pics_per_sec = 3;
Fs = 1/20;   % Sampling frequency (1 pic every 20 sec)
T = 1/Fs;       % Sample time
t = (0:L-1)*T;  % Time vector

% NFFT = 2^nextpow2(L); % Next power of 2 from length of y
% Y = fft(y,NFFT)/L;
% f = Fs/L*linspace(0,1,NFFT/2+1);

f = Fs/L*(0:L-1)
Y = abs(Y)

% Plot single-sided amplitude spectrum.
plot(f,Y) 

title('Fourier transform')
xlabel('Times per day')
ylabel('|Y(f)|')
ylim([0,60])
