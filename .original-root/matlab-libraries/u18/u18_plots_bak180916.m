tm=xts;
[rotation90_pks,rotation90_locs]=findpeaks(sin(orientacion/360*2*pi),'minpeakdistance',40);
[rotation0_pks,rotation0_locs]=findpeaks(orientacion,'minpeakdistance',40);

tm=xts;

if min(orientacion) < 150 && max(orientacion) > 250
    rotationsFound = true
else
    rotationsFound = false
    fprintf('\nWARNING: no rotations detected. Some plots will not be made.\n\n')
end
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Grafico inicial

% figure
% fprintf('%s\n','Graficando...');
% startDate = min(x_timestamp);%datenum(files_images(1).date);
% endDate = max(x_timestamp);%datenum(files_images(size(p,1)).date);
% plot(p,'.')
% xlabel('Photo #')
% ylabel('Position of interference maximum in photo (px)')
% title(['Movement of Interference Maxima: from ' datestr(x_timestamp(1)) ' to ' datestr(x_timestamp(size(p,1)))],'FontSize', 16);
% xlabel('Photo #');
% ylabel('Position of Maxima (pixels)');

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Busqueda de rotaciones
fprintf('%d picos de rotacion encontrados. \n', size(rotation0_pks,1));
if rotationsFound && ~exist('graficoAzimuth') || graficoAzimuth == true
    figure
    oh = hampel(orientacion(10:length(orientacion)));
    plot(oh, 'b.-')
%     ylim([-2 2])
%     hold on
%     plot(rotation90_locs, rotation90_pks, 'o')
%     line([rotation90_locs rotation90_locs], ylim,'color', 'r')
    title('Compass angle vs # photo')
    xlabel('Photo #')
    ylabel('Compass angle (º)')
    legend('Angle of rotation')
    usb2018_saveFigureToFile('brujula-sesion')
end
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Separar lineas

if (exist('ajustarDefault') && ajustarDefault ~= true) || ~exist('ajustarDefault')
    ajustar = input('desea unificar en una linea la data? [s]/n: ', 's');
end

if (exist('ajustar') && (isempty('ajustar') || strcmp(ajustar, 's'))) || (exist('ajustarDefault') && ajustarDefault == true)
    p_adjusted = usb2018_adjustdata();
    p = p_adjusted;
    padj = p_adjusted;
end    
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Escoger linea

% find column with more values
% ordeno las dimensiones del arreglo en las que tengan mayor cantidad de puntos
[cuentaPuntos, posicionCuenta] = sort(sum(~isnan(p_adjusted),1),2,'DESCEND');

% filasRecomendadas = posicionCuenta(1:5);
% legend(int2str(filasRecomendadas'))

if exist('lineaPreferida')
    curvaNum = lineaPreferida;
else
    figure
    hold off
    plot(p_adjusted(:, posicionCuenta(1:5)))
    legend(int2str(posicionCuenta(1:5)'))
    curvaNum = input(['Especifique el número de curva que desea usar[' int2str(filasRecomendadas(1)) ']: ']);
end
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Quitar outliers
p_adjusted_hampel = hampel(p_adjusted);
p_adjusted_hampel_pref = p_adjusted_hampel(:,curvaNum);
p_adjusted_pref = p_adjusted(:,curvaNum);
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Plot w/o outliers
plot(p_adjusted_pref,'o','color','blue','linewidth',1,'markersize',4) 
hold on
plot(p_adjusted_hampel_pref,'-','color','red','linewidth',1,'markersize',2);
t = title({'Movement of Interference Maxima:',[' from ' datestr(x_timestamp(1)) ' to ' datestr(x_timestamp(size(p,1)))]},'FontSize', 12);
% datetick('x','dd/mm HH:MM','keepticks')
legend('Original', 'W/o outliers', 'Location', 'NorthEast');
usb2018_saveFigureToFile('wo_outliers')
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

if sum(isnan(p_adjusted_hampel_pref)) > 0
    plot(isnan(p_adjusted_hampel_pref))
    xlim([-20 length(p_adjusted_hampel_pref)+20])
    input('No puede haber NaNs en los datos. Revise y presione enter para continuar.')
    p_adjusted_hampel_pref(1)=p_adjusted_hampel_pref(2);
end

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Ajuste
[fitresult, gof] = fit((1:size(p_adjusted_hampel_pref,1))',p_adjusted_hampel_pref,'smoothingspline');
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% % Grafico mostrando puntos de rotacion y minimos en puntos de rotacion
% 
% if rotationsFound
%     [peaks_extremes, locs_extremes] = findpeaks(p_adjusted_hampel_pref*-1, 'MinPeakDistance',30);  
%     
%     figure
%     plot(fitresult(1:size(p_adjusted_hampel_pref,1)))
%     hold on
%     [ps_peaks_extremes I] = hampel(peaks_extremes);
%     plot(locs_extremes(I==false), p_adjusted_hampel_pref(locs_extremes(I==false)), 'o');
%     % plot(p_adjusted_hampel_pref(I==false), ps_extremes, 'o')
%     % plot(ps_extremes, 'o')
%     xlabel('Photo #')
%     ylabel('Fringe displacement at fringe extremes')
%     title('Minima of fringe movement')
%     usb2018_saveFigureToFile('minima')
%     orientacion_extremes = hampel(orientacion(locs_extremes));
%     
%     % Difference in minutes between minima
%     xts_extreme_diff = hampel(diff(xts(locs_extremes)))*24*60;    
%     
%     figure
%     plot(orientacion_extremes,'o-')
%     title('Angle of Minima')
%     ylabel('Angle (º)')
%     xlabel('Minima #')
%     usb2018_saveFigureToFile('angle_minima')
% 
% 
%     figure
%     plot(xts_extreme_diff,'o-')
%     title('Differece in minutes between minima')
%     ylabel('Minutes')
%     xlabel('Minima #')
%     usb2018_saveFigureToFile('min_difference_minima')
% 
%     figure
%     plot(p_adjusted_hampel_pref(1:size(p_adjusted_hampel_pref,1)))
%     hold on
%     plot(rotation90_locs, p_adjusted_hampel_pref(rotation90_locs), 'o')
%     xlabel('Photo #')
%     ylabel('Position of fringe maxima (px)')
%     title({...
%         'Position of fringe at ~90º', ...
%         ['from ' datestr(x_timestamp(1)) ' to ' datestr(x_timestamp(size(p,1)))] ...
%     })    
%     
%     usb2018_saveFigureToFile('maxima_at_90angle')
% 
%     figure
%     plot(p_adjusted_hampel_pref(rotation90_locs),'o-')
%     title({...
%         'Position of maxima for ~90º angle of rotation', ...
%         ['from ' datestr(x_timestamp(1)) ' to ' datestr(x_timestamp(size(p,1)))] ...
%     })        
%     ylabel('Position of maxima (px)')
%     xlabel('Minima #')
%     usb2018_saveFigureToFile('maxima_90angle')
% end
% %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Ajuste

figure
[fitresult, gof] = fit((1:size(p_adjusted_hampel_pref,1))',p_adjusted_hampel_pref,'poly2');
% [fitresult, gof] = fit((1:size(p_adjusted_hampel_pref,1))',p_adjusted_hampel_pref,'poly1')
plot(p_adjusted_hampel_pref)
hold on
plot(fitresult(1:size(p_adjusted_hampel_pref,1)))
xlabel('Photo #')
ylabel('Fringe displacement (px)')
title({...
    'Adjusted Movement of interference fringes', ...
    ['from ' datestr(x_timestamp(1)) ' to ' datestr(x_timestamp(size(p,1)))] ...
})
usb2018_saveFigureToFile('ajuste')
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Resta de ajuste
pfit=p_adjusted_hampel_pref - fitresult(1:size(p_adjusted_hampel_pref));

figure
plot(1:size(pfit,1),pfit,'.-');
% if exist('locs') & exist('tm')
%     line([tm(rotation90_locs) tm(rotation90_locs)], ylim,'color', 'k', 'linewidth', 1)
% end
% set(gca,'XLim', [startDate endDate])
% datetick('x','dd/mm HH:MM','keepticks')
title({...
    'Corrected Movement of interference maxima', ...
    ['from ' datestr(x_timestamp(1)) ' to ' datestr(x_timestamp(size(p,1)))] ...
}) % , 'with smoothed curve' , 'with indicators of rotation'
xlabel('Photo #')
ylabel('Corrected Movement of interference maxima (px)')
usb2018_saveFigureToFile('ajustada')
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% % Puntos notables en curva corregida
% if rotationsFound
%     figure
%     plot(pfit(1:size(p_adjusted_hampel_pref,1)))
%     hold on
%     plot(rotation90_locs, pfit(rotation90_locs), 'o')
%     title('Corrected fringe displacement at ~90º angle of each rotation')
%     legend('Corrected fringe displacement', 'Displacement at ~90º angle of rotation')
%     xlabel('Photo #')
%     ylabel('Corrected fringe displacement (px)')
%     usb2018_saveFigureToFile('90_angle_rotation_corrected')
% 
%     figure
%     plot(pfit(rotation90_locs),'o-')
%     title('Corrected fringe displacement at ~90º angle of each rotation')
%     legend('Corrected fringe displacement at ~90º angle of rotation')
%     xlabel('Rotation Maxima #')
%     ylabel('Corrected fringe displacement at ~90º angle of rotation (px)')
%     usb2018_saveFigureToFile('maxima_90_angle_rotation_corrected')
% end
% %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Separacion franjas

if ~exist('lineaPreferidaAdjunta') || ~isnumeric(lineaPreferidaAdjunta)
    lineaPreferidaAdjunta = input('Select an adyecent fringe and press enter');
end

figure
plot(p_adjusted_hampel,'g.')
hold on
plot(...
	1:length(p_adjusted_hampel(:, lineaPreferida)), ...
    p_adjusted_hampel(:, lineaPreferida), ...    
    'rX', ...    
    1:length(p_adjusted_hampel(:, lineaPreferidaAdjunta)), ...
    p_adjusted_hampel(:, lineaPreferidaAdjunta), ...
    'rX' ...
)
title({['Interference Maxima displacement with two highlighted fringes, #' int2str(lineaPreferida) ' and #' int2str(lineaPreferidaAdjunta)], ...
    'the separation between fringes is the mean difference between highlighted fringes'})
xlabel('photo #')
ylabel('Fringe displacement (px)')
usb2018_saveFigureToFile('fringes_for_difference')

if exist('puntosSeparacionFranjas')
    limiteSeparacionFranjas = min(puntosSeparacionFranjas, size(p_adjusted_hampel,1));
else
    limiteSeparacionFranjas = size(p_adjusted_hampel,1);
end

separacionFranjas = abs(nanmean(...
    hampel(p_adjusted_hampel(1:limiteSeparacionFranjas,lineaPreferida) - p_adjusted_hampel(1:limiteSeparacionFranjas,lineaPreferidaAdjunta)) ...
));


errorSeparacionFranjas = nanstd(hampel( ...
        p_adjusted_hampel(1:limiteSeparacionFranjas,lineaPreferida) - p_adjusted_hampel(1:limiteSeparacionFranjas,lineaPreferidaAdjunta) ...
    )) / ...
    sqrt(length(p_adjusted_hampel(:,lineaPreferida)));

figure
restaLineas = hampel(p_adjusted_hampel(1:limiteSeparacionFranjas,lineaPreferida) - p_adjusted_hampel(1:limiteSeparacionFranjas,lineaPreferidaAdjunta), 4,1);
plot(restaLineas,'.-')
title({'Separation between fringes la "separacion entre franjas"', 'is the mean of these values', ...
    ['d=' num2str(separacionFranjas) '+- ' num2str(errorSeparacionFranjas) 'px'], ...
    'standard error given by stddev(points)/sqrt(#points)'} ...
)
if exist('limiteSeparacionFranjas')
    legend(['Franja limitada a ' num2str(limiteSeparacionFranjas) 'puntos'])
end
ylabel('Difference of displacement between two adjacent fringess (px)')
xlabel('Photo #')
usb2018_saveFigureToFile('separacion-franjas')
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Analisis de rotaciones

if ~rotationsFound
    fprintf('\nWARNING: no rotations detected. No analysis of rotation will be done.\n\n')
    return
end

clear legends

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Rotaciones independientes

colors = {'r' 'b' 'g' 'y' 'k'};


clear XX YY
[XX, YY] = divideInChunks(xts, pfit, rotation0_locs, 360);

% rotsgroup = 1;
% rotsstep = 1;
% plotInGroups(XX, YY ...
%     ,'groupsize', rotsgroup ...
%     ,'groupstep', rotsstep ...
%     ,'saveFigures', true ...
%     ,'errorBars', false ...
%     ,'plotGroups', true ...
%     ,'hampelParams', [1] ...
%     ,'normalizeBy', nan ...
% )
% 
% rotsgroup = 10;
% rotsstep = 6;
% plotInGroups(XX, YY ...
%     ,'groupsize', rotsgroup ...
%     ,'groupstep', rotsstep ...
%     ,'saveFigures', true ...
%     ,'errorBars', true ...
%     ,'plotGroups', true ...
%     ,'hampelParams', [1] ...
%     ,'normalizeBy', nan ...
% )

% figure
% hold on

% % se grafican todas las rotaciones cada rotacion
% plot(YY','.')
% legend(legends, 'Location','NorthEastOutside')
% legend(legends, 'Location','NorthEastOutside')
% title( ...
%     { ...
%         ['Fringe displacement per rotation'], ...
%         ['(session name: ' videoId ')'], ...
%     }, ...
%     'FontSize', 16, ...
%     'Interpreter', 'none' ...
% )
% xlabel('Rotation angle (º)')
% ylabel('Fringe displacement (px)')
% if ~exist('limitesGraficasPromediada')
%     ylim([-20 20]);
% end

% usb2018_saveFigureToFile('rotaciones-independientes')

% figure
% errorbarxy( ...
%     0:359, ...
%     nanmean(YY), ...
%     ones(1,360)*2, ...
%     nanstd(YY)/sqrt(numrotaciones), ...
%     {'k.-', 'c', 'm'})
% title( ...
%     { ...
%         ['Mean of ' int2str(numrotaciones) ' rotations'], ...
%         [int2str(rotacionini) ' through ' int2str(rotacionfin) ' out of total ' int2str(size(rotation0_locs,1))], ...
%         ['(session name: ' videoId ')'], ...
%     }, ...
%     'FontSize', 16, ...
%     'Interpreter', 'none' ...
% )
% if ~exist('limitesGraficasPromediada')
%     ylim([-10 10]);
% end
% xlabel('Rotation angle (º)')
% ylabel('Fringe displacement (px)')
% xlim([0 360])
% usb2018_saveFigureToFile('rotaciones-promediadas')

if ~exist('separacionFranjas') || ~isnumeric(separacionFranjas)
    fprintf('No existe separacion entre franjas!')
else
    
    rotsgroup = 1;
    rotsstep = 1;
    plotInGroups(XX, YY ...
        ,'groupsize', rotsgroup ...
        ,'groupstep', rotsstep ...
        ,'saveFigures', true ...
        ,'errorBars', false ...
        ,'plotGroups', true ...
        ,'hampelParams', [1] ...
        ,'normalizeBy', separacionFranjas ...
    )    

    rotsgroup = 10;
    rotsstep = 6;
    plotInGroups(XX, YY ...
        ,'groupsize', rotsgroup ...
        ,'groupstep', rotsstep ...
        ,'saveFigures', true ...
        ,'errorBars', true ...
        ,'plotGroups', true ...
        ,'hampelParams', [1] ...
        ,'normalizeBy', separacionFranjas ...
    )   

%     figure
% %     errorbar( ...
% %         0:359, ...
% %         nanmean(YY/separacionFranjas), ...
% %         nanstd(YY/separacionFranjas)/sqrt(numrotaciones))    
%     errorbarxy( ...
%         0:359, ...
%         nanmean(YY/separacionFranjas), ...
%         ones(1,360)*2, ...
%         nanstd(YY/separacionFranjas)/sqrt(numrotaciones), ...
%         {'k.-', 'c', 'm'})
%     title( ...
%         { ...
%             ['Mean of ' int2str(numrotaciones) ' rotations'], ...
%             [int2str(rotacionini) ' through ' int2str(rotacionfin) ' out of total ' int2str(size(rotation0_locs,1))], ...
%             ['(session name: ' videoId ')'], ...
%         }, ...
%         'FontSize', 16, ...
%         'Interpreter', 'none' ...
%     )
%     xlabel('Rotation angle (degrees)')
%     ylabel('Displacement of fringe (normalized by fringe width)')
% %     if ~exist('limitesGraficasPromediada')
% %         ylim([-10 10]);
% %     end
% 
%     xlim([0 360])
%     usb2018_saveFigureToFile('rotaciones-promediadas-normalizada')    
end

% %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% % Analisis de rotaciones con hampel
% 
% YY_orig = YY;
% hampel_stderror = 1;
% YYh=hampel(YY_orig, size(YY_orig,1), hampel_stderror);
% % convierto valores repetidos en nan
% YYh([nan(1,size(YYh,2));diff(YYh)]==0) = nan;
% YY=YYh;
% 
% plot(1:length(YY), YY, '.')
% % legend(legends, 'Location','NorthEastOutside')
% title( ...
%     { ...
%         ['Fringe displacement per rotation w/o outliers' ' (' num2str(hampel_stderror) ' stddev)' ], ...
%         ['(session name: ' videoId ')'], ...
%     }, ...
%     'FontSize', 16, ...
%     'Interpreter', 'none' ...
% )
% xlabel('Rotation angle (º)')
% ylabel('Fringe displacement w/o outliers (px)')
% % if ~exist('limitesGraficasPromediada')
% %     ylim([-20 20]);
% % end
% 
% usb2018_saveFigureToFile('rotaciones-independientes-clean')
% 
% figure
% % errorbarxy( ...
% %     0:359, ...
% %     nanmean(YY), ...
% %     ones(1,360)*2, ...
% %     nanstd(YY)./sqrt(sum(~isnan(YY))), ...
% %     {'k.-', 'c', 'm'})
% % title( ...
% %     { ...
% %         ['Mean of ' int2str(numrotaciones) ' rotations w/o outliers' ' (' num2str(hampel_stderror) ' stddev)'], ...
% %         [int2str(rotacionini) ' through ' int2str(rotacionfin) ' out of total ' int2str(size(rotation0_locs,1))], ...
% %         ['(session name: ' videoId ')'], ...
% %     }, ...
% %     'FontSize', 16, ...
% %     'Interpreter', 'none' ...
% % )
% if ~exist('limitesGraficasPromediada')
%     ylim([-10 10]);
% end
% xlabel('Rotation angle (º)')
% ylabel('Fringe displacement w/o outliers (px)')
% xlim([0 360])
% usb2018_saveFigureToFile('rotaciones-promediadas-clean')

% if ~exist('separacionFranjas') || ~isnumeric(separacionFranjas)
%     fprintf('No existe separacion entre franjas!')
% else
%     figure
% %     errorbar( ...
% %         0:359, ...
% %         nanmean(YY/separacionFranjas), ...
% %         nanstd(YY/separacionFranjas)/sqrt(numrotaciones))    
%     errorbarxy( ...
%         0:359, ...
%         nanmean(YY/separacionFranjas), ...
%         ones(1,360)*2, ...
%         nanstd(YY/separacionFranjas)./sqrt(sum(~isnan(YY))), ...
%         {'k.-', 'c', 'm'})
%     title( ...
%         { ...
%             ['Mean of ' int2str(numrotaciones) ' rotations w/o outliers' ' (' num2str(hampel_stderror) ' stddev)'], ...
%             [int2str(rotacionini) ' through ' int2str(rotacionfin) ' out of total ' int2str(size(rotation0_locs,1))], ...
%             ['(session name: ' videoId ')'], ...
%         }, ...
%         'FontSize', 16, ...
%         'Interpreter', 'none' ...
%     )
%     xlabel('Rotation angle (degrees)')
%     ylabel('Displacement of fringe (normalized by fringe width)')
% %     if ~exist('limitesGraficasPromediada')
% %         ylim([-10 10]);
% %     end
% 
%     xlim([0 360])
%     usb2018_saveFigureToFile('rotaciones-promediadas-normalizada-clean')    
% end

% % promedioPicoPicoxVideo = nanmean(max(YY'))-nanmean(min(YY'));
% % errorPromedioPicoPicoxVideo = (nanstd(max(YY'))+nanstd(min(YY')))/sqrt(size(YY',1));
% % promedioDistanciasPP = nanmean( max(YY')-nanmin(YY') );
% % errorPromedioDistanciasPP = nanstd(max(YY')-nanmin(YY') ) /sqrt(size(promedioPicoPicoxVideo,2)) ;

% promedioPicoPicoxVideo = nanmean(max(YY))-nanmean(min(YY));
% errorPromedioPicoPicoxVideo = (nanstd(max(YY))+nanstd(min(YY)))./sqrt(sum(~isnan(YY)));
% promedioDistanciasPP = nanmean( max(YY)-nanmin(YY) );
% errorPromedioDistanciasPP = nanstd(max(YY)-nanmin(YY) ) ./ sqrt(sum(~isnan(YY)));

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
