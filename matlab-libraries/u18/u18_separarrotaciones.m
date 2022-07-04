clear legends
% determino el angulo 0
[rotation0_pks,rotation0_locs]=findpeaks(azimuthvar,'minpeakdistance',40);

tm=xts;

if ~(min(rotation0_pks) < 10 && max(rotation0_pks) > 350)
    fprintf('\nWARNING: no rotations detected. No analysis of rotation will be done.\n\n')
    return
end

if ~exist('rotation0_locs')
    fprintf('hacen falta las posiciones "rotation0_locs" de las rotaciones\n');
    return
end

figure
hold on

i = 0;
clear YY
colors = {'r' 'b' 'g' 'y' 'k'};
rotacionini=2;
% if ~exist('rotacionini')
%     rotacionini = 6;
% end
rotacionfin = size(rotation0_locs,1 )-1;

numrotaciones = rotacionfin - rotacionini;
for k=rotacionini:rotacionfin
    i = i+1;
    rango = xts(rotation0_locs(k-1):rotation0_locs(k));
    
    inicio = rango(1);
    fin = rango(length(rango));
    pasos = (fin-inicio)/360;
    XX = inicio:pasos:fin;

%     plot( ...
%          xts(xts>tm(rotation0_locs(k-1)) & xts<tm(rotation0_locs(k))), ...
%         pfit(xts>tm(rotation0_locs(k-1)) & xts<tm(rotation0_locs(k))), ...
%         'color', colors{mod(k,5)+1} ...
%     );

    
    YY(i,:) = pchip( ...
        xts(rotation0_locs(k-1):rotation0_locs(k)), ...
        pfit(rotation0_locs(k-1):rotation0_locs(k)), ...
        XX ...
    );
    legends{i} = int2str(k);
%     plot(pchip(xts(xts>tm(rotation0_locs(k-1)) & xts<tm(rotation0_locs(k))), pfit(xts>tm(rotation0_locs(k-1)) & xts<tm(rotation0_locs(k))), XX));
%     YY(i,:) = pchip(xts(xts>tm(rotation0_locs(k-1)) & xts<tm(rotation0_locs(k))), pfit(xts>tm(rotation0_locs(k-1)) & xts<tm(rotation0_locs(k))), XX);
    
%     datetick('x','dd/mm HH:MM','keepticks')
end
plot(YY','.')
promedioPicoPicoxVideo = nanmean(max(YY'))-nanmean(min(YY'));
errorPromedioPicoPicoxVideo = (nanstd(max(YY'))+nanstd(min(YY')))/sqrt(size(YY',1));
promedioDistanciasPP = nanmean( max(YY')-nanmin(YY') );
errorPromedioDistanciasPP = nanstd(max(YY')-nanmin(YY') ) /sqrt(size(promedioPicoPicoxVideo,2)) ;
legend(legends, 'Location','NorthEastOutside')
legend(legends, 'Location','NorthEastOutside')
title( ...
    { ...
        ['Fringe displacement per rotation'], ...
        ['(session name: ' videoId ')'], ...
    }, ...
    'FontSize', 16, ...
    'Interpreter', 'none' ...
)
if ~exist('limitesGraficasPromediada')
    ylim([-20 20]);
end

usb2018_saveFigureToFile('rotaciones-independientes')

figure
errorbar(nanmean(YY),nanstd(YY)/sqrt(numrotaciones))
title( ...
    { ...
        ['Mean of ' int2str(numrotaciones) ' rotations'], ...
        [int2str(rotacionini) ' through ' int2str(rotacionfin) ' out of total ' int2str(size(rotation0_locs,1))], ...
        ['(session name: ' videoId ')'], ...
    }, ...
    'FontSize', 16, ...
    'Interpreter', 'none' ...
)
if ~exist('limitesGraficasPromediada')
    ylim([-10 10]);
end

xlim([0 360])
usb2018_saveFigureToFile('rotaciones-promediadas')

if ~exist('separacionFranjas') || ~isnumeric(separacionFranjas)
    fprintf('No existe separacion entre franjas!')
else
    figure
    errorbar(nanmean(YY/separacionFranjas),nanstd(YY/separacionFranjas)/sqrt(numrotaciones))
    title( ...
        { ...
            ['Mean of ' int2str(numrotaciones) ' rotations'], ...
            [int2str(rotacionini) ' through ' int2str(rotacionfin) ' out of total ' int2str(size(rotation0_locs,1))], ...
            ['(session name: ' videoId ')'], ...
        }, ...
        'FontSize', 16, ...
        'Interpreter', 'none' ...
    )
    xlabel('Rotation angle (degrees)')
    ylabel('Displacement of fringe (normalized by fringe width)')
    if ~exist('limitesGraficasPromediada')
        ylim([-10 10]);
    end

    xlim([0 360])
    usb2018_saveFigureToFile('rotaciones-promediadas-normalizada')    
end


% [maximo, posmax] = max(mean(YY));
% [minimo, posmin] = min(mean(YY));
% picoPicoNormalizada = (max(mean(YY)) - min(mean(YY)))/separacionFranjas;
% 
% errorPicoPico = nanmean(std(YY)/sqrt(numrotaciones)*2);
% 
% picoPico = maximo - minimo;
% errorDesplazamientoNormalizado = errorPicoPico*(1/separacionFranjas) + (1/separacionFranjas)^2*errorSeparacionFranjas*picoPico;

% saveLogFile(['nombre video:\t' videoId ])
% saveLogFile(['# total rotaciones:\t' num2str(size(rotation0_locs,1 )) ])
% saveLogFile(['# rotacion inicial para el promedio:\t' num2str(rotacionini) ])
% saveLogFile(['# rotacion final para el promedio:\t' num2str(rotacionfin) ])
% saveLogFile(['maximo del promedio (px):\t' num2str(maximo) ])
% saveLogFile(['minimo del promedio (px):\t' num2str(minimo) ])
% saveLogFile(['distancia pico-pico (px) del promedio:\t' num2str(picoPico) ])
% saveLogFile(['distancia entre franjas (px):\t'  num2str(separacionFranjas) '\t'])
% saveLogFile(['distancia pico-pico promedio normalizada con distancia entre franjas:\t' num2str(picoPicoNormalizada)])
% saveLogFile(['posicion maximo (°):\t' num2str(posmax)])
% saveLogFile(['posicion minimo (°):\t' num2str(posmin)])
% saveLogFile(['hora inicio:\t' datestr(xts(1)) ])
% saveLogFile(['hora fin:\t' datestr(max(xts)) ])
% saveLogFile(['hora promedio:\t' datestr((max(xts) + xts(1))/2) ])
% saveLogFile(['error pico-pico promedio:\t' num2str(errorPicoPico) ])
% saveLogFile(['errorDesplazamientoNormalizado:\t' num2str(errorDesplazamientoNormalizado) ])
% saveLogFile(['errorAnchoFranja:\t' num2str(errorSeparacionFranjas) ])
% saveLogFile(['(promedio de maximos) - (promedio de minimos):\t' num2str(promedioPicoPicoxVideo) ])
% saveLogFile(['(promedio de maximos) - (promedio de minimos) normalizado:\t' num2str(promedioPicoPicoxVideo/separacionFranjas) ])
% saveLogFile(['error[(promedio de maximos) - (promedio de minimos)]:\t' num2str(errorPromedioPicoPicoxVideo) ])
% 
% saveLogFile(['promedio de distancias p-p normalizado:\t' num2str(promedioPicoPicoxVideo/separacionFranjas) ])
% saveLogFile(['error[promedio de distancias p-p normalizado]:\t' num2str(errorPromedioPicoPicoxVideo) ])




% figure
% plot(YY','.')
