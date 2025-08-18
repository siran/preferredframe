clear saveFigureToFile
clear functions

fconf = [path_images videoId '.csv'];
if exist(fconf, 'file')
    conf = readtable(fconf);   
    fields = fieldnames(conf);
    for f=1:length(fields)
        if ~strcmp(fields{f},'Properties')
            eval([fields{f} '=conf.(fields{f})'])
        end
    end
end
    
tm=xts;
x_timestamp = xts';
[rotation90_pks,rotation90_locs]=findpeaks(cos(orientacion/360*2*pi),'minpeakdistance',40);
[rotation0_pks,rotation0_locs]=findpeaks(sin(orientacion/360*2*pi),'minpeakdistance',40);

fprintf('%d picos de rotacion encontrados. \n', size(rotation0_pks,1));
numrotaciones = size(rotation0_pks,1);

tm=xts;

if min(orientacion) < 150 && max(orientacion) > 250
    rotationsFound = true;
else
    rotationsFound = false;
    fprintf('\nWARNING: no rotations detected. Some plots will not be made.\n\n')
end


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Busqueda de rotaciones
if rotationsFound && ~exist('graficoAzimuth') || graficoAzimuth == true
    figure
    oh = hampel(orientacion);
    plot(xts, sin(oh*pi/180), 'b.-')
%     ylim([-2 2])
%     hold on
%     plot(rotation90_locs, rotation90_pks, 'o')
%     line([rotation90_locs rotation90_locs], ylim,'color', 'r')
    title({'Compass angle', [num2str(numrotaciones) ' rotations found']})
    xlabel('Date time (dd/mm HH:MM)')
    ylabel('sin(Compass angle * pi / 180)-9 (rad)')
    legend('Angle of rotation')

    set(gca,'XMinorTick','on')
    grid on
    datetick('x', 'HH:MM')
    xlabel('Date-time (dd/mm HH:MM)')
    ax = gca;
    ax.XTickLabelRotation = 90;
    hold on
    ylim([-5 5])    
    xlim([xts(1) xts(end)])    
    usb2018_saveFigureToFile('rotations', 'closeFigure', false)

    set(gca,'XMinorTick','on')
    grid on
    datetick('x', 'HH:MM')
    xlabel('Date-time (dd/mm HH:MM)')
    ax = gca;
    ax.XTickLabelRotation = 90;
    hold on
    ylim([-5 5])   
    xlim([xts(1) xts(min(500, length(xts)))])
    usb2018_saveFigureToFile('rotations-zoomin')
end
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Separar lineas

if ~exist('ajustarDefault')
    ajustar = input('desea unificar en una linea la data? [s]/n: ', 's');
else
    ajustar = ajustarDefault;
end

clear p_adjusted_orig
if ~exist('p_adjusted_orig', 'var') && (exist('ajustar', 'var') && ( ajustar == true || strcmp(ajustar, 's')))
    if ~exist('backInTime')
        backInTime = 1;
    end
    if ~exist('maxHeightDifference')
        maxHeightDifference = 25;
    end    
%     maxHeightDifference = 25;
%     backInTime = 1;
    p_adjusted_orig = usb2018_adjustdata(p_orig...
        , 'backInTime', backInTime...
        , 'maxHeightDifference', maxHeightDifference...
    );
    p_adjusted = p_adjusted_orig;
    p = p_adjusted;
    padj = p_adjusted;
elseif exist('p_adjusted_orig', 'var')
    p_adjusted = p_adjusted_orig;
    p = p_adjusted;
    padj = p_adjusted;        
else
    p = p_orig;
    p_adjusted = p_orig;
    padj = p_adjusted;
end    

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Grafico inicial

figure
startDate = x_timestamp(1);
endDate = x_timestamp(end); %datenum(files_images(size(p,1)).date);
plot(xts, p, '.')
title(['Displacement of Interference Maxima: from ' datestr(x_timestamp(1)) ' to ' datestr(x_timestamp(size(p,1)))],'FontSize', 16);
ylabel('Displacement of Maxima (pixels)');
set(gca,'XMinorTick','on')
grid on
datetick('x', 'HH:MM')
xlabel('Date-time (dd/mm HH:MM)')
ax = gca;
ax.XTickLabelRotation = 90;
hold on
xlim([xts(1) xts(end)])
for r=1:length(rotation90_locs)
    line([xts(rotation90_locs(r)) xts(rotation90_locs(r))], [ax.YLim(1) ax.YLim(2)], ...
        'Marker','.','LineStyle','--', 'Color', [1 0 0])
    line([xts(rotation90_locs(r)) xts(rotation90_locs(r))], [ax.YLim(1) ax.YLim(2)], ...
        'Marker','.','LineStyle','--', 'Color', [1 0 0])
end
legend('Maxima displacement', 'Rotation indicator')
usb2018_saveFigureToFile('maxima-displacement')

title(['Displacement of Interference Maxima: from ' datestr(x_timestamp(1)) ' to ' datestr(x_timestamp(size(p,1)))],'FontSize', 16);
ylabel('Displacement of Maxima (pixels)');
set(gca,'XMinorTick','on')
grid on
datetick('x', 'HH:MM')
xlabel('Date-time (dd/mm HH:MM)')
ax = gca;
ax.XTickLabelRotation = 90;
hold on
xlim([xts(1) xts(end)])
usb2018_saveFigureToFile('maxima-displacement')
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%



%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Escoger linea

if ~exist('lineaPreferida')
        % find column with more values
        % ordeno las dimensiones del arreglo en las que tengan mayor cantidad de puntos
        [cuentaPuntos, posicionCuenta] = sort(sum(~isnan(p_adjusted),1),2,'DESCEND');

        filasRecomendadas = posicionCuenta(1:min(size(posicionCuenta,1),5));
        legend(int2str(filasRecomendadas'))

        figure
        hold off
        plot(p_adjusted(:, posicionCuenta(1:5)))
        legend(int2str(posicionCuenta(1:5)'))
        lineaPreferida = input(['Especifique el número de curva que desea usar[' int2str(filasRecomendadas(1)) ']: ']);
        lineaPreferidaAdjunta = input(['Especifique el número de curva ADJUNTA que desea usar[' int2str(filasRecomendadas(1)) ']: ']);
end
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Quitar outliers
p_adjusted_hampel = hampel(p_adjusted);
p_adjusted_hampel_pref = p_adjusted_hampel(:,lineaPreferida);
p_adjusted_pref = p_adjusted(:,lineaPreferida);
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Plot w/o outliers
% plot(xts, p_adjusted_pref,'o','color','blue','linewidth',1,'markersize',4) 
% hold on
% plot(xts, p_adjusted_hampel_pref,'-','color','red','linewidth',1,'markersize',2);
% t = title({'Movement of Interference Maxima:',[' from ' datestr(x_timestamp(1)) ' to ' datestr(x_timestamp(size(p,1)))]},'FontSize', 12);
% xlabel('Date time (dd/mm HH:MM)')
% datetick('x','dd/mm HH:MM')
% ax = gca;
% ax.XTickLabelRotation = 90;  
% grid(gca,'minor')
% set(gca,'XMinorTick','on')  
% xlim([xts(1) xts(length(xts))])
% legend('Original', 'W/o outliers', 'Location', 'NorthEast');
% usb2018_saveFigureToFile('wo_outliers')
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% 
% if sum(isnan(p_adjusted_hampel_pref)) > 0
%     plot(isnan(p_adjusted_hampel_pref))
%     xlim([-20 length(p_adjusted_hampel_pref)+20])
%     input('No puede haber NaNs en los datos. Revise y presione enter para continuar.')
%     p_adjusted_hampel_pref(1)=p_adjusted_hampel_pref(2);
% end

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Ajuste
% [fitresult, gof] = fit((1:size(p_adjusted_hampel_pref,1))',p_adjusted_hampel_pref,'smoothingspline');
fitresult = smooth(p_adjusted_hampel_pref, 11.25*20);
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
% [fitresult, gof] = fit((1:size(p_adjusted_hampel_pref,1))',p_adjusted_hampel_pref,'poly2');
% [fitresult, gof] = fit((1:size(p_adjusted_hampel_pref,1))',p_adjusted_hampel_pref,'poly1')
plot(xts, p_adjusted_hampel_pref)
hold on
plot(xts, fitresult(1:size(p_adjusted_hampel_pref,1)), 'r-')
xlabel('Date time (dd/mm HH:MM)')
ylabel('Fringe displacement (px)')
title({...
    'Displacement of interference fringes and Fit', ...
    ['from ' datestr(x_timestamp(1)) ' to ' datestr(x_timestamp(size(p,1)))] ...
})
legend('Original data', 'Moving average fit (120 points, 2 rotations')

set(gca,'XMinorTick','on')
grid on
datetick('x', 'HH:MM')
xlabel('Date-time (dd/mm HH:MM)')
ax = gca;
ax.XTickLabelRotation = 90;
hold on
xlim([xts(1) xts(end)])
ylimites = ylim();
usb2018_saveFigureToFile('ajuste')

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Resta de ajuste
pfit=p_adjusted_hampel_pref - fitresult(1:size(p_adjusted_hampel_pref));

figure
plot(xts, pfit,'.-');
% if exist('locs') & exist('tm')
%     line([tm(rotation90_locs) tm(rotation90_locs)], ylim,'color', 'k', 'linewidth', 1)
% end
% set(gca,'XLim', [startDate endDate])
% datetick('x','dd/mm HH:MM','keepticks')
title({...
    'Corrected fringe displacement', ...
    ['from ' datestr(x_timestamp(1)) ' to ' datestr(x_timestamp(size(p,1)))] ...
}) % , 'with smoothed curve' , 'with indicators of rotation'
xlabel('Date time (dd/mm HH:MM)')
ylabel('Corrected fringe displacement (px)')

set(gca,'XMinorTick','on')
grid on
datetick('x', 'HH:MM')
xlabel('Date-time (dd/mm HH:MM)')
ax = gca;
ax.XTickLabelRotation = 90;
hold on
xlim([xts(1) xts(end)])
ylimdiff = diff(ylimites);
ylim([-ylimdiff/2 ylimdiff/2 ]);
usb2018_saveFigureToFile('ajustada', 'closeFigure', false)

for r=1:length(rotation90_locs)
    line([xts(rotation90_locs(r)) xts(rotation90_locs(r))], [ax.YLim(1) ax.YLim(2)], ...
        'Marker','.','LineStyle','--', 'Color', [1 0 0])
    line([xts(rotation90_locs(r)) xts(rotation90_locs(r))], [ax.YLim(1) ax.YLim(2)], ...
        'Marker','.','LineStyle','--', 'Color', [1 0 0])
end
legend('Displacement of maxima','Compass at 0ºN (laser 90ºN)')
xlim([xts(1) min(xts(1)+1/24/2, xts(end))])
datetick('x','dd/mm HH:MM')
xlim([xts(1) xts(end)])

title({...
    'Corrected Displacement of interference maxima', ...
    ['from ' datestr(x_timestamp(1)) ' to ' datestr(x_timestamp(size(p,1)))] ...
    ,'(First 30m)' ...
}) % , 'with smoothed curve' , 'with indicators of rotation'
usb2018_saveFigureToFile('ajustada-30m')
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

plot(...
	xts, ...
    p_adjusted_hampel(:, lineaPreferida), ...    
    'rX', ...    
    xts, ...
    p_adjusted_hampel(:, lineaPreferidaAdjunta), ...
    'rX' ...
)
hold on
plot(xts, p_adjusted_hampel,'g.')
% hold on
title({['Interference Maxima displacement with two highlighted fringes, #' int2str(lineaPreferida) ' and #' int2str(lineaPreferidaAdjunta)], ...
    'the separation between fringes is the mean difference between highlighted fringes'})
xlabel('Date time (dd/mm HH:MM)')
datetick('x','dd/mm HH:MM')
ax = gca;
ax.XTickLabelRotation = 90;  
grid(gca,'minor')
set(gca,'XMinorTick','on')  
xlim([xts(1) min(xts(1)+1/24/2, xts(end))])
ylabel('Fringe displacement (px)')
usb2018_saveFigureToFile('fringes_for_difference')

% if exist('puntosSeparacionFranjas')
limiteSeparacionFranjas = min( ...
    [ 500, ...
    size(p_adjusted_hampel(:, lineaPreferida       ), 1), ...
    size(p_adjusted_hampel(:, lineaPreferidaAdjunta), 1) ...
    ] ...
);
% puntosSeparacionFranjas, size(p_adjusted_hampel,1);
% else
%     limiteSeparacionFranjas = size(p_adjusted_hampel,1);
% end

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
ylim([min(restaLineas)-5 max(restaLineas)+5])
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
% [XXm, YYm, YYstddev] = plotInGroups(XX, YY ...
%     ,'groupsize', rotsgroup ...
%     ,'groupstep', rotsstep ...
%     ,'saveFigures', true ...
%     ,'errorBars', false ...
%     ,'plotGroups', true ...
%     ,'hampelParams', nan ...
%     ,'normalizeBy', nan ...
% );
% 
% rotsgroup = 10;
% rotsstep = 6;
% [XXm, YYm, YYstddev] = plotInGroups(XX, YY ...
%     ,'groupsize', rotsgroup ...
%     ,'groupstep', rotsstep ...
%     ,'saveFigures', true ...
%     ,'errorBars', true ...
%     ,'plotGroups', true ...
%     ,'hampelParams', nan ...
%     ,'normalizeBy', nan ...
% );

if ~exist('separacionFranjas') || ~isnumeric(separacionFranjas)
    fprintf('No existe separacion entre franjas!')
else
    
    rotsgroup = 1;
    rotsstep = 1;
    [XXm, YYm, YYstddev] = plotInGroups(XX, YY ...
        ,'groupsize', rotsgroup ...
        ,'groupstep', rotsstep ...
        ,'saveFigures', true ...
        ,'errorBars', false ...
        ,'plotGroups', true ...
        ,'hampelParams', nan ...
        ,'normalizeBy', separacionFranjas ...
    );

    writeSummary( ...
         'sessionId', videoId ...
        ,'XX', XXm ...
        ,'YY', YYm ...
        ,'YYstddev', YYstddev ...
        ,'rotations', rotsgroup ...
        ,'separation', rotsstep ...
        ,'fringe_separation', separacionFranjas ...        
    );

    rotsgroup = 10;
    rotsstep = 6;
    [XXm, YYm, YYstddev] = plotInGroups(XX, YY ...
        ,'groupsize', rotsgroup ...
        ,'groupstep', rotsstep ...
        ,'saveFigures', true ...
        ,'errorBars', true ...
        ,'plotGroups', true ...
        ,'hampelParams', nan ...
        ,'normalizeBy', separacionFranjas ...
    );

    writeSummary( ...
         'sessionId', videoId ...
        ,'XX', XXm ...
        ,'YY', YYm ...
        ,'YYstddev', YYstddev ...
        ,'rotations', rotsgroup ...
        ,'separation', rotsstep ...
        ,'fringe_separation', separacionFranjas ...
    );

end


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
