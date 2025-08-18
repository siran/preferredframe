% resta efecto de temperatura

razont2 = (134.9-197.5)/(34.02-33.88) %pixeles / grados
razont = (85.66-134.9)/(34.21-34.02) %pixeles / grados
razont = (razont+razont2)/1.5

pendiente = 0; %(190-252)/(735760.0271064815 - 735762.0566666666); %pixeles / dias
% tprom = 33.6;

[tmu,tmi,tmui] = unique(tm, 'stable');
tempint = pchip(tmu, temp(tmi), xts);

% p = sig2;
if ~exist('curvaNum') || isnan(curvaNum)
    findbettercol
%     curvaNum = input('Especifique el número de curva que desea usar: ');
end
if ~exist('ps')
    fprintf('Variable "ps" no encontrada. Por favor, ejecute primero el programa findbettercol para encontrar una linea y suavizarla.\n');
    return;
end
padj3c = ps + (xts - xts(1))*pendiente - (tempint-mean(tempint))*razont;
p = padj3c;
pc = p;

figure
plot(xts, padj3c,'x-',xts, ps,'linewidth',1,'markersize',2)
xlim([startDate endDate+1/2]);
set(gca,'XTick',startDate:endDate+1/2)
set(gca,'XMinorTick','on')
set(gca,'Box','off');
datetick('x','dd/mm HH:MM','keepticks')

lineasestelares

legend('franjas corregida','franja original')

% hold on
% grafico_max_hip54217

graficar_temp_con_ejes

% legend('franjas corregida','franja original','temperatura')

% legend('franjas corregida','franja original','temperatura')
% temp = temp_original;
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