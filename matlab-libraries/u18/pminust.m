% resta efecto de temperatura

razon = (53-17)/(33.9-33.4); %pixeles / grados
tprom = 33.6;

[tmu,tmi,tmui] = unique(tm, 'stable');
tempint = pchip(tmu, smooth(temp(tmi),20), x_timestamp);

% p = sig2;
padj3c = padj(:,3) - (tempint'-tprom)*razon;

% x = xts(8690:size(xts));
% y = p(8690:size(xts));

plot(x_timestamp, padj3c,'.-')
hold on
plot(x_timestamp, padj(:,3), 'color','red')
hold off
temp_original = temp;
temp = smooth(temp,20);
graficar_temp_con_ejes
temp = temp_original;
% plot(x_timestamp, tempint, 'color','blue')

% L = size(x,1); % Length of signal 
% 
% Fs = 24*60*2; %veces por dia                   % Sampling frequency
% T = 1/Fs;                     % Sample time
% 
% t = (0:L-1)*T;                % Time vector
% 
% % y = y ;%+ sin(2*pi*1.1*t)';
% 
% NFFT = 2^nextpow2(L); % Next power of 2 from length of y
% Y = fft(y,NFFT)/L;
% f = Fs/2*linspace(0,1,NFFT/2+1);
% 
% % Plot single-sided amplitude spectrum.
% plot(f,2*abs(Y(1:NFFT/2+1))) 
% title('Transformada de Fourier')
% xlabel('Frecuencia (veces por dia)')
% ylabel('|Y(f)|')
% xlim([0.7 2]);


% 
% grafico_max_hip54217
% hold on

% p = smooth(p,120);
% grafico_max_hip54217

% for i = 1 : size(x_timestamp,2)
%     pmt = p(i) - (tempint(i)-tprom) * razon;
% end