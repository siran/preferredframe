% find column with more values

if min(rotation0_pks) < 10 && max(rotation0_pks) > 350
    rotationsFound = true
else
    rotationsFound = false
    fprintf('\nWARNING: no rotations detected. Some plots will not be made.\n\n')
end

% ordeno las dimensiones del arreglo en las que tengan mayor cantidad de puntos
[cuentaPuntos, posicionCuenta] = sort(sum(~isnan(p_adjusted),1),2,'DESCEND');

filasRecomendadas = posicionCuenta(1:5);
legend(int2str(filasRecomendadas'))

if exist('lineaPreferida')
    curvaNum = lineaPreferida;
else
    figure
    hold off
    plot(p_adjusted(:, posicionCuenta(1:5)))
    legend(int2str(posicionCuenta(1:5)'))
    curvaNum = input(['Especifique el número de curva que desea usar[' int2str(filasRecomendadas(1)) ']: ']);
end

ph = hampel(p_adjusted);
ps = ph(:,curvaNum);
pu = p_adjusted(:,curvaNum);


plot(pu,'o','color','blue','linewidth',1,'markersize',4) 
hold on
plot(ps,'-','color','red','linewidth',1,'markersize',2);
t = title({'Movement of Interference Maxima:',[' from ' datestr(x_timestamp(1)) ' to ' datestr(x_timestamp(size(p,1)))]},'FontSize', 12);
% datetick('x','dd/mm HH:MM','keepticks')
legend('Original', 'W/o outliers', 'Location', 'NorthEast');
usb2018_saveFigureToFile('wo_outliers')


if sum(isnan(ps)) > 0
    plot(isnan(ps))
    xlim([-20 length(ps)+20])
    input('No puede haber NaNs en los datos. Revise y presione enter para continuar.')
    ps(1)=ps(2);
end
[fitresult, gof] = fit((1:size(ps,1))',ps,'smoothingspline');
[peaks_extremes, locs_extremes] = findpeaks(ps*-1, 'MinPeakDistance',30);  

figure
plot(fitresult(1:size(ps,1)))
hold on
[ps_peaks_extremes I] = hampel(peaks_extremes);
plot(locs_extremes(I==false), ps(locs_extremes(I==false)), 'o');
% plot(ps(I==false), ps_extremes, 'o')
% plot(ps_extremes, 'o')
xlabel('Photo #')
ylabel('Fringe displacement at fringe extremes')
title('Minima of fringe movement')
usb2018_saveFigureToFile('minima')

orientacion_extremes = hampel(orientacion(locs_extremes));

% Difference in minutes between minima
xts_extreme_diff = hampel(diff(xts(locs_extremes)))*24*60;

figure
plot(orientacion_extremes,'o-')
title('Angle of Minima')
ylabel('Angle (º)')
xlabel('Minima #')
usb2018_saveFigureToFile('angle_minima')

figure
plot(xts_extreme_diff,'o-')
title('Differece in minutes between minima')
ylabel('Minutes')
xlabel('Minima #')
usb2018_saveFigureToFile('min_difference_minima')

if rotationsFound
    figure
    plot(ps(1:size(ps,1)))
    hold on
    plot(rotation_locs, ps(rotation_locs), 'o')
    xlabel('Photo #')
    ylabel('Position of fringe maxima (px)')
    title({...
        'Position of fringe at ~90º', ...
        ['from ' datestr(x_timestamp(1)) ' to ' datestr(x_timestamp(size(p,1)))] ...
    })    
    
    usb2018_saveFigureToFile('maxima_at_90angle')

    figure
    plot(ps(rotation_locs),'o-')
    title({...
        'Position of maxima for ~90º angle of rotation', ...
        ['from ' datestr(x_timestamp(1)) ' to ' datestr(x_timestamp(size(p,1)))] ...
    })        
    ylabel('Position of maxima (px)')
    xlabel('Minima #')
    usb2018_saveFigureToFile('maxima_90angle')
end


figure
[fitresult, gof] = fit((1:size(ps,1))',ps,'poly2');
% [fitresult, gof] = fit((1:size(ps,1))',ps,'poly1')
plot(ps)
hold on
plot(fitresult(1:size(ps,1)))
xlabel('Photo #')
ylabel('Fringe displacement (px)')
title({...
    'Adjusted Movement of interference fringes', ...
    ['from ' datestr(x_timestamp(1)) ' to ' datestr(x_timestamp(size(p,1)))] ...
})
usb2018_saveFigureToFile('ajuste')

% pfit = p-fitresult(1:size(p));
pfit=ps - fitresult(1:size(ps));
% p=pfit;


figure
plot(1:size(pfit,1),pfit,'.-');
% if exist('locs') & exist('tm')
%     line([tm(rotation_locs) tm(rotation_locs)], ylim,'color', 'k', 'linewidth', 1)
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

if rotationsFound
    figure
    plot(pfit(1:size(ps,1)))
    hold on
    plot(rotation_locs, pfit(rotation_locs), 'o')
    title('Corrected fringe displacement at ~90º angle of each rotation')
    legend('Corrected fringe displacement', 'Displacement at ~90º angle of rotation')
    xlabel('Photo #')
    ylabel('Corrected fringe displacement (px)')
    usb2018_saveFigureToFile('90_angle_rotation_corrected')

    figure
    plot(pfit(rotation_locs),'o-')
    title('Corrected fringe displacement at ~90º angle of each rotation')
    legend('Corrected fringe displacement at ~90º angle of rotation')
    xlabel('Rotation Maxima #')
    ylabel('Corrected fringe displacement at ~90º angle of rotation (px)')
    usb2018_saveFigureToFile('maxima_90_angle_rotation_corrected')
end


% veo cuales cuentas son adyacentes
% adyacentes = diff(posicionCuenta(1:15));

if ~exist('lineaPreferidaAdjunta') || ~isnumeric(lineaPreferidaAdjunta)
    lineaPreferidaAdjunta = input('Select an adyecent fringe and press enter');
end

figure
plot(ph,'g.')
hold on
plot(...
	1:length(ph(:, lineaPreferida)), ...
    ph(:, lineaPreferida), ...    
    'rX', ...    
    1:length(ph(:, lineaPreferidaAdjunta)), ...
    ph(:, lineaPreferidaAdjunta), ...
    'rX' ...
)

title({['Interference Maxima displacement with two highlighted fringes, #' int2str(lineaPreferida) ' and #' int2str(lineaPreferidaAdjunta)], ...
    'the separation between fringes is the mean difference between highlighted fringes'})
xlabel('photo #')
ylabel('Fringe displacement (px)')
usb2018_saveFigureToFile('fringes_for_difference')

separacionFranjas = abs(nanmean(...
    hampel(ph(:,lineaPreferida) - ph(:,lineaPreferidaAdjunta)) ...
));


errorSeparacionFranjas = nanstd(hampel( ...
        ph(:,lineaPreferida) - ph(:,lineaPreferidaAdjunta) ...
    )) / ...
    sqrt(length(ph(:,lineaPreferida)));


figure
restaLineas = hampel(ph(:,lineaPreferida) - ph(:,lineaPreferidaAdjunta));
plot(restaLineas,'.')
title({'Separation between fringes la "separacion entre franjas"', 'is the mean of these values', ...
    ['d=' num2str(separacionFranjas) '+- ' num2str(errorSeparacionFranjas) 'px'], ...
    'standard error given by stddev(points)/sqrt(#points)'} ...
)
ylabel('Difference of displacement between two adjacent fringess (px)')
xlabel('Photo #')
usb2018_saveFigureToFile('separacion-franjas')





