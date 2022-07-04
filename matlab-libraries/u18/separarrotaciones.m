clear legends

if ~exist('locs')
    fprintf('hacen falta las posiciones "locs" de las rotaciones\n');
    return
end

figure
hold on

i = 0;
clear YY
colors = {'r' 'b' 'g' 'y' 'k'};
if ~exist('rotacionini')
    rotacionini = 6;
end
rotacionfin = size(locs,1 )-2;

numrotaciones = rotacionfin - rotacionini;
for k=rotacionini:rotacionfin
    i = i+1;
    rango = xts(xts>tm(locs(k-1)) & xts<tm(locs(k)));
    
    inicio = rango(1);
    fin = rango(size(rango,1));
    pasos = (fin-inicio)/360;
    XX = inicio:pasos:fin;

%     plot( ...
%          xts(xts>tm(locs(k-1)) & xts<tm(locs(k))), ...
%         pfit(xts>tm(locs(k-1)) & xts<tm(locs(k))), ...
%         'color', colors{mod(k,5)+1} ...
%     );

    
    YY(i,:) = pchip( ...
        xts(xts>tm(locs(k-1)) & xts<tm(locs(k))), ...
        p(xts>tm(locs(k-1)) & xts<tm(locs(k)),curvaNum), ...
        XX ...
    );
    legends{i} = int2str(k);
%     plot(pchip(xts(xts>tm(locs(k-1)) & xts<tm(locs(k))), pfit(xts>tm(locs(k-1)) & xts<tm(locs(k))), XX));
%     YY(i,:) = pchip(xts(xts>tm(locs(k-1)) & xts<tm(locs(k))), pfit(xts>tm(locs(k-1)) & xts<tm(locs(k))), XX);
    
%     datetick('x','dd/mm HH:MM','keepticks')
end
plot(YY','.')
promedioPicoPicoxVideo = nanmean(max(YY'))-nanmean(min(YY'));
errorPromedioPicoPicoxVideo = (nanstd(max(YY'))+nanstd(min(YY')))/sqrt(size(YY',1));
promedioDistanciasPP = nanmean( max(YY')-nanmin(YY') );
errorPromedioDistanciasPP = nanstd(max(YY')-nanmin(YY') ) /sqrt(size(promedioPicoPicoxVideo,2)) ;
legend(legends, 'Location','NorthEastOutside')
legend(legends, 'Location','NorthEastOutside')
title({['Video ' videoId ...
    ': Rotaciones normalizadas en velocidad, rotaciones '], ...
    [int2str(rotacionini) ' a la ' int2str(rotacionfin) ' de un total de ' int2str(size(locs,1))]}, ...
    'FontSize', 16)
if ~exist('limitesGraficasPromediada')
    ylim([-20 20]);
end

saveFigureToFile('rotaciones-independientes')

figure
errorbar(nanmean(YY),nanstd(YY)/sqrt(numrotaciones))
title(['Video ' videoId ...
    ': Promedio de ' int2str(numrotaciones) ' rotaciones y barra de error, de la ' ...
    int2str(rotacionini) ' a la ' int2str(rotacionfin) ' de un total de ' int2str(size(locs,1))], ...
    'FontSize', 16)
if ~exist('limitesGraficasPromediada')
    ylim([-10 10]);
end

xlim([0 360])
saveFigureToFile('rotaciones-promediadas')


[maximo, posmax] = max(mean(YY));
[minimo, posmin] = min(mean(YY));
picoPicoNormalizada = (max(mean(YY)) - min(mean(YY)))/separacionFranjas;

errorPicoPico = nanmean(std(YY)/sqrt(numrotaciones)*2);

picoPico = maximo - minimo;
errorDesplazamientoNormalizado = errorPicoPico*(1/separacionFranjas) + (1/separacionFranjas)^2*errorSeparacionFranjas*picoPico;

saveLogFile(['nombre video:\t' videoId ])
saveLogFile(['# total rotaciones:\t' num2str(size(locs,1 )) ])
saveLogFile(['# rotacion inicial para el promedio:\t' num2str(rotacionini) ])
saveLogFile(['# rotacion final para el promedio:\t' num2str(rotacionfin) ])
saveLogFile(['maximo del promedio (px):\t' num2str(maximo) ])
saveLogFile(['minimo del promedio (px):\t' num2str(minimo) ])
saveLogFile(['distancia pico-pico (px) del promedio:\t' num2str(picoPico) ])
saveLogFile(['distancia entre franjas (px):\t'  num2str(separacionFranjas) '\t'])
saveLogFile(['distancia pico-pico promedio normalizada con distancia entre franjas:\t' num2str(picoPicoNormalizada)])
saveLogFile(['posicion maximo (°):\t' num2str(posmax)])
saveLogFile(['posicion minimo (°):\t' num2str(posmin)])
saveLogFile(['hora inicio:\t' datestr(xts(1)) ])
saveLogFile(['hora fin:\t' datestr(max(xts)) ])
saveLogFile(['hora promedio:\t' datestr((max(xts) + xts(1))/2) ])
saveLogFile(['error pico-pico promedio:\t' num2str(errorPicoPico) ])
saveLogFile(['errorDesplazamientoNormalizado:\t' num2str(errorDesplazamientoNormalizado) ])
saveLogFile(['errorAnchoFranja:\t' num2str(errorSeparacionFranjas) ])
saveLogFile(['(promedio de maximos) - (promedio de minimos):\t' num2str(promedioPicoPicoxVideo) ])
saveLogFile(['(promedio de maximos) - (promedio de minimos) normalizado:\t' num2str(promedioPicoPicoxVideo/separacionFranjas) ])
saveLogFile(['error[(promedio de maximos) - (promedio de minimos)]:\t' num2str(errorPromedioPicoPicoxVideo) ])

saveLogFile(['promedio de distancias p-p normalizado:\t' num2str(promedioPicoPicoxVideo/separacionFranjas) ])
saveLogFile(['error[promedio de distancias p-p normalizado]:\t' num2str(errorPromedioPicoPicoxVideo) ])




% figure
% plot(YY','.')
