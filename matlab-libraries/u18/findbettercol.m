%find column with more values

padj = p_adjusted;
padjn = padj;

% ordeno las dimensiones del arreglo en las que tengan mayor cantidad de
% puntos
[cuentaPuntos, posicionCuenta] = sort(sum(~isnan(p_adjusted),1),2,'DESCEND');

% veo cuales cuentas son adyacentes
adyacentes = diff(posicionCuenta(1:15));

% plot(xts, padj(:, posicionCuenta(adyacentes==1 | adyacentes==-1)));

filasRecomendadas = posicionCuenta(adyacentes==1 | adyacentes==-1);
legend(int2str(filasRecomendadas'))

startDate = xts(1);
endDate = xts(size(xts,1));

puntosSuavizado = nan;
curvaNum = nan;

lineaPreferidaSeparacionFranja = filasRecomendadas(1);
if filasRecomendadas(1) == 1 || (sum(~isnan(padj(:,filasRecomendadas(1)+1))) >= sum(~isnan(padj(:,filasRecomendadas(1)-1))))
    sign = 1;
else
    sign = -1;
end
separacionFranjas = abs(nanmean(padj(:,lineaPreferidaSeparacionFranja) - padj(:,lineaPreferidaSeparacionFranja+sign)));
if separacionFranjas > 55
    separacionFranjas = separacionFranjas/2;
end
errorSeparacionFranjas = nanstd(padj(:,lineaPreferidaSeparacionFranja) - padj(:,lineaPreferidaSeparacionFranja+sign)) / ...
    nanmean(sqrt(abs(padj(:,lineaPreferidaSeparacionFranja) - padj(:,lineaPreferidaSeparacionFranja+sign))));


plot(xts,padj(:,lineaPreferidaSeparacionFranja), 'x', xts,padj(:,lineaPreferidaSeparacionFranja+sign),'.')
hold on
plot(xts,padj,'-')
legend({['linea' num2str(lineaPreferidaSeparacionFranja)], ['linea ' num2str(lineaPreferidaSeparacionFranja + sign)], 'todas las lineas'})
title({'la "separacion entre franjas"', 'es el promedio de la diferencia entra las lineas resatadas'})
ylabel('pixel')
ylabel('tiempo')
set(gca,'XLim', [startDate endDate])
datetick('x','dd/mm HH:MM','keepticks')
saveFigureToFile('separacion-franjas-lineas')
hold off

figure
restaLineas = padj(:,lineaPreferidaSeparacionFranja) - padj(:,lineaPreferidaSeparacionFranja+sign);
plot(xts,restaLineas,'.')
title({'la "separacion entre franjas"', 'es el promedio de estos valores'})
ylabel('pixel')
ylabel('tiempo')
datetick('x','dd/mm HH:MM','keepticks')
set(gca,'XLim', [startDate endDate])
set(gca,'YLim', [min(nanmean(restaLineas)/1.4, nanmean(restaLineas)*1.4) max(nanmean(restaLineas)/1.4, nanmean(restaLineas)*1.4)])
saveFigureToFile('separacion-franjas')
figure

if exist('lineaPreferida')
    curvaNum = lineaPreferida;
else
    figure
    hold off
    plot(xts, padj(:, posicionCuenta(adyacentes==1)))
    legend(int2str(posicionCuenta(adyacentes==1)'))
    curvaNum = input(['Especifique el número de curva que desea usar[' int2str(filasRecomendadas(1)) ']: ']);
end

% if exist('puntosSuavizadoPreferido')
%     puntosSuavizado = puntosSuavizadoPreferido;
% else
%     puntosSuavizado = input('Especifique los puntos del suavizado [40]: ');
% end

% if isempty(puntosSuavizado)
    puntosSuavizado = 40;
% end

if (~exist('suavizar') || suavizar == true) && ~isnan(puntosSuavizado)
    ps = smooth(padj(:,curvaNum), puntosSuavizado);    
%     ps2 = smooth(padj(:,curvaNum), puntosSuavizado, 'rloess');
    
    p=ps;    
else
    ps=p;
end

if exist('tt') && exist('temp')
    subplot(2,1,1)
%     smootht = input('especifique puntos para suavizado de temperatura: ');
    smootht = 40;
    if (~exist('suavizar') || suavizar == false) && ~isempty(smootht)
        temps = smooth(temp_orig, smootht);
        temp=temps;
    end    
end

pu = padj(:,curvaNum);


% plot(xts,padj(:,curvaNum),'.',xts,ps,'x');

% [pks, lks] = findpeaks(ps, 'minpeakdistance', 1000);

plot(xts, pu,'o','color','blue','linewidth',1,'markersize',4) 
% datetick('x','dd/mm HH:MM','keepticks')
% set(gca,'XLim', [startDate endDate])
hold on

plot(xts,ps,'-','color','red','linewidth',1,'markersize',2);
t = title({'Movement of Interference Maxima:',[' from ' datestr(x_timestamp(1)) ' to ' datestr(x_timestamp(size(p,1)))]},'FontSize', 12);
% set(gca,'XTick',startDate:endDate+1/2)
% set(gca,'XMinorTick','on')
% set(gca,'Box','off');
datetick('x','dd/mm HH:MM','keepticks')
legend('Original', 'Suavizado', 'Location', 'NorthEast');
set(gca,'XLim', [startDate endDate])


if exist('locs') & exist('tm')
    line([tm(locs) tm(locs)], ylim,'color', 'k', 'linewidth', 1)
end 

ci = nan;
% input('Make datatips export them as "ci" and press [enter]');
if isstruct(ci) 
    for i=1:size(ci,2);fprintf('%s \n', datestr(ci(i).Position(1))); end
end

if exist('tt') && exist('temp')
    mint = min(temp);
    maxt = max(temp);
    subplot(2,1,2)
    hold on
    plot(tm,temp_orig,'o','linewidth',1,'markersize',2,'color','blue');
    xlim([startDate endDate]);
    plot(tm,temp,'-','linewidth',1,'markersize',2,'color','red');
    legend('Original', 'Suavizado', 'Location',  'NorthEast');
    t = title(['Temperatura from ' datestr(x_timestamp(1)) ' to ' datestr(x_timestamp(size(p,1)))],'FontSize', 12);
    set(gca,'Visible','on',  'YAxisLocation','right', 'YLim',[mint maxt]);
     xlim([startDate endDate]);
%      set(gca,'XTick',startDate:endDate)
%     set(gca,'XMinorTick','on')
%     set(gca,'Box','off');
    datetick('x','dd/mm HH:MM','keepticks')   
    saveFigureToFile('temperatura')
end

hold off
figure

plot(xts, pu,'o','color','blue','linewidth',1,'markersize',4) 
t = title(['Movement of Interference Maxima: from ' datestr(x_timestamp(1)) ' to ' datestr(x_timestamp(size(p,1)))],'FontSize', 12);
set(gca,'XLim', [startDate endDate])
% set(gca,'XTick',startDate:endDate+1/2)
% set(gca,'XMinorTick','on')
% set(gca,'Box','off');
datetick('x','dd/mm HH:MM','keepticks')
legend('Original', 'Location', 'NorthEast');
saveFigureToFile('original')

if exist('locs') & exist('tm')
    line([tm(locs) tm(locs)], ylim,'color', 'k', 'linewidth', 1)
end 

[fitresult, gof] = fitp(pu);
title('Adjusted Movement of interference fringes')
saveFigureToFile('ajuste')

% pfit = p-fitresult(1:size(p));
pfit=p(:, 2) - fitresult(1:size(p));
% p=pfit;


figure
plot(xts,pfit, 'o');
if exist('locs') & exist('tm')
    line([tm(locs) tm(locs)], ylim,'color', 'k', 'linewidth', 1)
end
set(gca,'XLim', [startDate endDate])
datetick('x','dd/mm HH:MM','keepticks')
title('Adjusted Movement of interference fringes, with indicators of rotation')
saveFigureToFile('ajustada')



