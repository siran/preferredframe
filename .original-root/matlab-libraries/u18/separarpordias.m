%% separo la data 
clc
clear xtsi xtsic xtsics pci pcic pcics tempi tempic tempics int c lags lege dialege

int = 1/24/60/60*30;

xtsi = min(xts):int:max(xts);

pci = pchip(xts, pc, xtsi);
tempi = pchip(tm, temp, xtsi);

inicio = int:int:(min(xtsi)-floor(min(xtsi)));

xtsic = horzcat(inicio, xtsi-floor(min(xtsi)));
pcic = horzcat(nan(size(inicio)), pci);
tempic = horzcat(nan(size(inicio)), tempi);

%% separo franjas en dias y grafico
i=1;
ini=1;
while true
    [row col] = find(xtsic > i, 1);
    if isempty(col)
        i=i-1;
        break
    end
    fprintf('limites: %d %d\n',ini,col-1);
    fprintf('size: %d \n', size(xtsi(1,ini:col-1),2));
    
    if ~exist('xtsics')
        xtsics = xtsic(ini:col-1);
    end
    
    pcics(i,:) = pcic(ini:ini+size(xtsics,2)-1);
    tempics(i,:) = tempic(ini:ini+size(xtsics,2)-1);
    i=i+1; 
    ini=col;
end

%% pongo el primer día como nulo
pcics(1,:) = nan(1,size(xtsics,2));
tempics(1,:) = nan(1,size(xtsics,2));


%% grafico normalizado
figure
subplot(2,1,1)
hold on
colores = {'r-' 'k-' 'b-' 'r--' 'k--' 'b--' 'r:' 'k:' 'b:' 'r.' 'g.' 'b.'};
for n=1:i
    dialege{n} = ['dia' int2str(n)];
    pcicsnorm(n,:) = pcics(n,:)/max(pcics(n,:));
    plot(xtsics, pcicsnorm(n,:), colores{n},'markerSize',2);
end
legend(dialege, 'Location', 'EastOutside');
title('Movimiento de franjas, dia a dia, normalizado')
xlabel('Hora')
ylabel('Pixeles (normalizado con máximo)')
datetick('x','HH:MM','keepticks')
subplot(2,1,2)
hold on
for n=1:i
    tempicsnorm(n,:) = tempics(n,:)/max(tempics(n,:));
    plot(xtsics, tempicsnorm(n,:), colores{n})
end
datetick('x','HH:MM','keepticks')
legend(dialege, 'Location', 'EastOutside');
title('Temperatura, dia a dia, normalizado')
xlabel('Hora')
ylabel('ºC (normalizado con máximo)')

%% grafico sin normalizar
figure
subplot(2,1,1)
hold on
for n=1:i
    dialege{n} = ['dia' int2str(n)];
    plot(xtsics, pcics(n,:), colores{n});
end
legend(dialege, 'Location', 'EastOutside');
title('Movimiento de franjas, dia a dia, SIN normalizar')
xlabel('Hora')
ylabel('Pixeles')
datetick('x','HH:MM','keepticks')
subplot(2,1,2)
hold on
for n=1:i
    plot(xtsics, tempics(n,:), colores{n})
end
datetick('x','HH:MM','keepticks')
legend(dialege, 'Location', 'EastOutside');
title('Temperatura, dia a dia, SIN normalizar')
xlabel('Hora')
ylabel('ºC')

%% grafico promedio
figure
subplot(2,1,1)
plot(xtsics, nanmean(pcics),'linewidth',1,'markersize',2)
datetick('x','HH:MM','keepticks')
title('Promedio de franjas')
xlabel('Hora')
ylabel('Pixeles')
subplot(2,1,2)
plot(xtsics, nanmean(tempics), 'o','linewidth',1,'markersize',2)
datetick('x','HH:MM','keepticks')
title('Promedio de temperatura')
xlabel('Hora')
ylabel('ºC')

%% grafico con barras de error

figure
subplot(2,1,1)
sem=nanstd(pcics)/sqrt(length(pcics)); % standard error of the mean
errorbar(xtsics, nanmean(pcics),sem,'o','linewidth',1,'markersize',1)
xlim([min(xtsics) max(xtsics)])
datetick('x','HH:MM','keepticks')
title('Promedio de franjas, con barra de error')
xlabel('Hora')
ylabel('Pixeles')
subplot(2,1,2)
semt=nanstd(pcics)/sqrt(length(tempics)); % standard error of the mean
errorbar(xtsics, nanmean(tempics), semt,'o','linewidth',1,'markersize',2)
xlim([min(xtsics) max(xtsics)])
datetick('x','HH:MM','keepticks')
title('Promedio de temperatura, con barra de error')
xlabel('Hora')
ylabel('ºC')

