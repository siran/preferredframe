% para interpolar
xp = x'; 

if size(ys,1) < size(ys,2)
    yp = ys'; 
else
    yp = ys; 
end
xi = (xp(1):30/(24*60*60):xp(length(xp)))'; 
yi = interp1(x,y,xi,'spline'); 

% figure
% plot(x,y,'.')
% plot(xi,yi,'.')



Fs = 2*60*24;                    % Sampling frequency
T = 1/Fs;                     % Sample time
L = length(yi);                     % Length of signal
t = (0:L-1)*T;                % Time vector


ys=yi;
if size(ys,1) > size(ys,2)
    yp = ys'; 
else
    yp = ys; 
end


% % Sum of a 50 Hz sinusoid and a 120 Hz sinusoid
% x = 0.7*sin(2*pi*50*t) + sin(2*pi*120*t); 
% y = x + 2*randn(size(t));     % Sinusoids plus noise
% figure
% plot(Fs*t,ys,'.')
% title('Signal Corrupted with Zero-Mean Random Noise')
% xlabel('time (m)')


NFFT = 2^nextpow2(L); % Next power of 2 from length of y
Y = fft(ys,NFFT)/L;
f = Fs/2*linspace(0,1,NFFT/2+1);

% Plot single-sided amplitude spectrum.
figure
plot(f,2*abs(Y(1:NFFT/2+1))) 
title('Single-Sided Amplitude Spectrum of y(t)')
xlabel('Frequency (Hz)')
ylabel('|Y(f)|')

set(gca,'XLim', [0.25 2])