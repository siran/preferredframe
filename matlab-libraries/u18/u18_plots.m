global processing_session

clear saveFigureToFile
clear functions

clear ratio_fringe_separation
if isfield(processing_session, 'ratio_fringe_separation') && ~isempty(processing_session.ratio_fringe_separation)
    ratio_fringe_separation = processing_session.ratio_fringe_separation;
end
% processing_session
% if ~isfield(processing_session, 'saveTxtData') || (isfield(processing_session, 'saveTxtData') && isempty(processing_session.saveTxtData))
    saveTxtData = processing_session.saveTxtData;
% end

close(gcf)

xts = x_timestamp';

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% setting plot x limits by substracting the fractional part over :00 or :30 min
x_start = xts(1) - mod(xts(1), 1/48);
x_end = x_start + 1/48;

% xlim([x_start x_end])
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% fprintf('Data: %s - %s \n', datestr(x_start), datestr(x_end))


fconf = [path_images videoId '.csv'];
if exist(fconf, 'file')
    conf = readtable(fconf);   
    fields = fieldnames(conf);
    for f=1:length(fields)
        if ~strcmp(fields{f},'Properties')
            eval([fields{f} '=conf.(fields{f});'])
        end
    end
end
rotating_session = 1;
    
% orientacion = mod(orientacion - 12.66, 360);
% [rotation90_pks,rotation90_locs]=findpeaks(sin(orientacion/360*2*pi)       ,x_timestamp,'minpeakdistance',1/24/60*2.5, 'MinPeakHeight', 0.95);
if length(orientacion) ~= length(x_timestamp)
    return
end
[rotation0_pks,rotation0_locs]=  findpeaks(sin(orientacion/360*2*pi + pi/2),x_timestamp,'minpeakdistance',1/24/60*2.5, 'MinPeakHeight', 0.95);

fprintf('%d picos de rotacion encontrados. \n', num_rotations);
numrotaciones = length(rotation0_pks);

% tm=xts;

if min(orientacion) < 150 && max(orientacion) > 250
    rotationsFound = true;
else
    rotationsFound = false;
    fprintf('\nWARNING: no rotations detected. Some plots will not be made.\n\n')
end


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Busqueda de rotaciones
if rotationsFound && (~exist('graficoAzimuth') || graficoAzimuth == true)
    if ~exist('plot_rotations', 'var') || plot_rotations
%         figure
    %     oh = hampel(orientacion);
        oh = orientacion;
        plot(xts, sin(oh*pi/180), 'b.')
        ax = gca;
        ax.XTickLabelRotation = 90;
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

        datetick('x', 'dd/mm HH:MM')
        xlabel('Date-time (dd/mm HH:MM)')
        ax = gca;

        hold on

        config_plot
        ylim([-5 5])    
        usb2018_saveFigureToFile('rotations')

    %     set(gca,'XMinorTick','on')
    %     grid on
    %     datetick('x', 'HH:MM')
    %     xlabel('Date-time (dd/mm HH:MM)')
    %     ax = gca;
    %     ax.XTickLabelRotation = 90;
    %     hold on
    %     ylim([-5 5])   
    %     xlim([xts(1) xts(min(500, length(xts)))])
    %     usb2018_saveFigureToFile('rotations-zoomin')
    end
end
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% clear timeAltitude
readdatetimealt

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Grafico inicial

p = p_orig;

% hold off
% figure



startDate = x_timestamp(1);
endDate = x_timestamp(end); %datenum(files_images(size(p,1)).date);

% yyaxis left
% if length(xts) ~= length(p)
%     stop=1;
% end
plot(xts, p, '.')

title({'Displacement of Interference Maxima vs Time (raw)', ['from ' datestr(x_start) ' to ' datestr(x_end)]},'FontSize', 16);
ylabel('Displacement of Maxima (px)');

% set(gca,'XMinorTick','on')
% grid on
% datetick('x', 'dd/mm HH:MM')
% xlabel('Date-time (dd/mm HH:MM)')
% ax = gca;
% ax.XTickLabelRotation = 90;
% hold on

% continuar = input(['Do you want to continue with other plot? 1/0: ']);
% if continuar == 0
%     return
% end

% draw_rotations(xts(rotation0_locs), ylim, ax)

% for r=1:length(rotation0_locs)
%     line([xts(rotation0_locs(r)) xts(rotation0_locs(r))], [ax.YLim(1) ax.YLim(2)], ...
%         'Marker','.','LineStyle','--', 'Color', [1 0 0])
%     line([xts(rotation0_locs(r)) xts(rotation0_locs(r))], [ax.YLim(1) ax.YLim(2)], ...
%         'Marker','.','LineStyle','--', 'Color', [1 0 0])
% end
% legend('Maxima displacement - raw', 'Rotation indicator')
if exist('day_session') && day_session
    nothing=0;
else
%     if exist('session_duration_min', 'var')
%        
%         % substracting the fractional part over :00 or :30 min
%         x_start = xts(1) - mod(xts(1), 1/48);
%         x_end = x_start + 1/48;
%         
%         xlim([x_start x_end])
%     end
end
ylimites = ylim();
ylimdiff = diff(ylimites);
if exist('day_session') && day_session
    hours_limits = [0 2 4 6 8 12 14 16 18 20 22 24];
    if y_scale
        yyaxis left
        ymin = max(ylim())/3;
        ymax = ymin*2;
%         ylim([ymin ymax])        
        ylim([600 800])        
    end
    for hl=1:length(hours_limits)-1        
        x_start = floor(xts(1)) + hours_limits(hl)/24;
        
%         x_end = floor(xts(1)) + hours_limits(hl+1)/24
        x_end = x_start + 1/12;
        if ~ length(xts(xts >= x_start & xts < x_end));
            continue
        end
        
        xlim([x_start x_end])
        set(gca,'XTick', [x_start:1/48:x_end])
        datetick('x', 'dd/mm HH:MM', 'keepticks')
        
        fprintf('plot from %s to %s\n', datestr(x_start), datestr(x_end))
        title(['Displacement of Interference Maxima: from ' ...
            datestr(x_start) ' to ' ...
            datestr(x_end)],'FontSize', 16);
        plotheightstar
        closeFigure = hl==(length(hours_limits)-1);
        usb2018_saveFigureToFile(['maxima-displacement' '-' int2str(hours_limits(hl))], ...
            'closeFigure', closeFigure)
    end
            
else
    ax = gca;
    draw_rotations(rotation0_locs, ylim, ax)
    plotheightstar
%     xlim([x_start x_end])
    config_plot
%     ylim([0 1600])
    usb2018_saveFigureToFile('maxima-displacement-raw')
end

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Separar lineas

if ~exist('ajustarDefault')
    ajustar = input('desea unificar en una linea la data? [s]/n: ', 's');
else
    ajustar = ajustarDefault;
end

clear p_adjusted_orig
if ~exist('p_adjusted_orig', 'var') && (exist('ajustar', 'var') && ( ajustar == true || strcmp(ajustar, 's')))
%     if ~exist('backInTime')
%         backInTime = 1;
%     end
%     if ~exist('maxHeightDifference')
%         maxHeightDifference = 80;
%         if ~isfield(table2struct(conf), 'maxHeightDifference')
%             conf.maxHeightDifference = maxHeightDifference ;
%             writetable(conf, fconf);          
%         end
%     end    
%     maxHeightDifference = 25;
%     backInTime = 1;
    if exist('ratio_fringe_separation', 'var')
        p_adjusted_orig = usb2018_adjustdata(p_orig, 'ratio_fringe_separation', ratio_fringe_separation);
    else 
        p_adjusted_orig = usb2018_adjustdata(p_orig);
    end
    p_adjusted = p_adjusted_orig;
    p = p_adjusted;
%     plot(p)
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
% Grafico inicial (lineas separadas)

% figure
% startDate = x_timestamp(1);
% endDate = x_timestamp(end); %datenum(files_images(size(p,1)).date);

% yyaxis left
if length(xts) ~= length(p)
    stop=1;
end
plot(xts, p, '.')

title({'Displacement of Interference Maxima vs Time', ['from ' datestr(x_start) ' to ' datestr(x_end)]},'FontSize', 16);
ylabel('Displacement of Maxima (px)');

% set(gca,'XMinorTick','on')
% grid on
% datetick('x', 'dd/mm HH:MM')
% xlabel('Date-time (dd/mm HH:MM)')
% ax = gca;
% ax.XTickLabelRotation = 90;
config_plot

hold on

% continuar = input(['Do you want to continue with other plot? 1/0: ']);
% if continuar == 0
%     return
% end

if exist('day_session') && day_session
    nothing=0;
else
%     if exist('session_duration_min', 'var')
%        
%         % substracting the fractional part over :00 or :30 min
%         x_start = xts(1) - mod(xts(1), 1/48);
%         x_end = x_start + 1/48;
%         
%         xlim([x_start x_end])
%     end
end
% ylimites = ylim();
% ylimdiff = diff(ylimites);
if exist('day_session') && day_session
    hours_limits = [0 2 4 6 8 12 14 16 18 20 22 24];
    if y_scale
        yyaxis left
        ymin = max(ylim())/3;
        ymax = ymin*2;
%         ylim([ymin ymax])        
        ylim([600 800])        
    end
    for hl=1:length(hours_limits)-1

        
%         x_start = floor(xts(1)) + hours_limits(hl)/24
%         
% %         x_end = floor(xts(1)) + hours_limits(hl+1)/24
%         x_end = x_start + 1/12;
%         if ~ length(xts(xts >= x_start & xts < x_end))
%             continue
%         end
        
        xlim([x_start x_end])
        set(gca,'XTick', [x_start:1/48:x_end])
        datetick('x', 'dd/mm HH:MM', 'keepticks')
        
        fprintf('plot from %s to %s\n', datestr(x_start), datestr(x_end))
        title({ ...
            'Displacement of Interference Maxima',  ...
            ['from ' datestr(x_start) ...
               'to ' datestr(x_end)]},'FontSize', 16);
        plotheightstar
        closeFigure = hl==(length(hours_limits)-1);
        usb2018_saveFigureToFile(['maxima-displacement' '-' int2str(hours_limits(hl))], ...
            'closeFigure', closeFigure)
    end
            
else
    plotheightstar
    draw_rotations(rotation0_locs, ylim, ax)
    config_plot
    usb2018_saveFigureToFile('maxima-displacement')
end

if ~exist('ajustar', 'var') || ~ajustar
    fprintf('Curves not being adjusted. End of plotting.')
    close(gcf)
    return
end

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Quitar outliers
if processing_session.removeOutliers
    [p_adjusted_hampel, removed_points] = hampel(p_adjusted,3,1);
else
%     p_adjusted_hampel = p_adjusted;
%     removed_points = zeros(size(p_adjusted));
    [p_adjusted_hampel, removed_points] = hampel(p_adjusted,5,10);
%     removed_points = p_adjusted*0;
%     p_adjusted_hampel = p_adjusted;
end
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Escoger linea
    
% temporal, para la data de septiembre 2019
% clear lineaPreferida lineaPreferidaAdjunta
% lineaPreferida = 8
% lineaPreferidaAdjunta = 9
    
if ~exist('lineaPreferida') || (exist('force_choose_line', 'var') && force_choose_line)
    % find column with more values
    
    % calculating length of lines
    length_lines = length(p_adjusted_hampel) - sum(removed_points);
    
    % sort lines by number of points descending
    [sorted_lines, sorted_lines_indices] = sort(length_lines, 'descend');
    
    % six more populates columns
%     sorted_long_lines_indices = sort(sorted_lines_indices(1:6));

    found_lines = false;
    for i=1:7
        for j=i+1:7
            if abs(sorted_lines_indices(i) - sorted_lines_indices(j)) == 1
                lineaPreferida = sorted_lines_indices(i);
                lineaPreferidaAdjunta = sorted_lines_indices(j);
                adjacency_sign = lineaPreferida-lineaPreferidaAdjunta;
                found_lines = true;
                break
            end
        end
        if found_lines
            break
        end
    end
    if ~found_lines
        fprintf('Did not find adjacent curves. Stop.')
        a=1;
    end
    
%     a=1
    
% % % % % % %     % calculate adjacency of the long lines
% % % % % % %     diff_column_indices = diff(sorted_lines_indices);
% % % % % % %     
% % % % % % %     % sort by adjacency
% % % % % % %     % [sorted_diff_column_indices, indices_diff_column_indices] = sort(diff_column_indices);
% % % % % % %     
% % % % % % %     % pick adjacency 1 or -1
% % % % % % %     adjacent_long_lines_indices = (diff_column_indices==-1 | diff_column_indices==1);
% % % % % % %     
% % % % % % %     % find first non-zero value
% % % % % % %     adjacent_long_line_index = find(adjacent_long_lines_indices(1:6)==1);
% % % % % % %     adjacency_sign = diff_column_indices(adjacent_long_line_index);
% % % % % % %     
% % % % % % %     if isempty(adjacency_sign)
% % % % % % %         fprintf('Could not find adjacent lines.')
% % % % % % %         return
% % % % % % %     end
% % % % % % %     
% % % % % % %     
% % % % % % %     
% % % % % % %     len_adjacent_lines = length(adjacent_long_line_index);
% % % % % % % %     if len_adjacent_lines  >= 2 
% % % % % % % %         center_line_index = round(len_adjacent_lines/2);
% % % % % % % %         lineaPreferida = sorted_long_lines_indices(center_line_index);
% % % % % % % %         lineaPreferidaAdjunta = lineaPreferida + adjacency_sign(center_line_index);
% % % % % % % %     else
% % % % % % %         lineaPreferida = sorted_lines_indices(adjacent_long_line_index(1));
% % % % % % %         lineaPreferidaAdjunta = lineaPreferida + adjacency_sign(1);
%     end
    
    
%     figure
%     plot(xts, p_adjusted_hampel)
%     hold on
%     plot(xts, p_adjusted_hampel(:, lineaPreferida),'gx')
%     
%     plot(xts, p_adjusted_hampel(:, lineaPreferidaAdjunta),'rx')
%     STOP=1;
%     choose_lines = input('want to choose lines? 1/0')
%     choose_lines =0;
    
% %     d = diff(posicionCuenta);
% %     elegibles = (abs(d)==1);
% %     indices = find(elegibles == 1 | elegibles == -1);
% %     lineaPreferida = posicionCuenta(indices(1));
% %     if d(indices(1)) == 1
% %         lineaPreferidaAdjunta = lineaPreferida + 1
% %     elseif d(indices(1)) == -1
% %         lineaPreferidaAdjunta = lineaPreferida - 1
% %     else
% %         error=1/0
% %     end
% % 
% % 
% %     if elegibles(indices(2)) && elegibles(indices(3))
% %         lineaPreferida = posicionCuenta(indices(1))
% %         lineaPreferidaAdjunta = lineaPreferida + 1 %posicionCuenta(indices(3))
% %     elseif elegibles(indice(1)) && elegibles(indices(2))
% %         lineaPreferida = posicionCuenta(indices(1))
% %         lineaPreferidaAdjunta = posicionCuenta(indices(2))        
% %     end
%     
% %     lineaPreferida = filasRecomendadas(1+1)
% %     lineaPreferidaAdjunta = filasRecomendadas(2+1)
%     if choose_lines == 1
%         lineaPreferida = input(['Especifique el número de curva que desea usar[' int2str(filasRecomendadas(1)) ']: ']);
%         lineaPreferidaAdjunta = input(['Especifique el número de curva ADJUNTA que desea usar[' int2str(filasRecomendadas(1)) ']: ']);
%     end
    
    conf.lineaPreferida = lineaPreferida;
    conf.lineaPreferidaAdjunta = lineaPreferidaAdjunta;
    if strcmp(class(conf), 'table')
        writetable(conf, fconf);   
    else
        writetable(struct2table(conf), fconf);   
    end
end

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% preferred lines
p_adjusted_hampel_pref = p_adjusted_hampel(:,lineaPreferida);
p_adjusted_pref = p_adjusted(:,lineaPreferida);
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% temporal, para la data de septiembre 2019
% clear lineaPreferida lineaPreferidaAdjunta
% lineaPreferida = 8
% lineaPreferidaAdjunta = 9

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Separacion franjas

plot(...
	xts, ...
    p_adjusted_hampel(:, lineaPreferida), ...    
    'gX', ...    
    xts, ...
    p_adjusted_hampel(:, lineaPreferidaAdjunta), ...
    'rX' ...
)
hold on
plot(xts, p_adjusted_hampel, '.', 'Color', [150 150 150]/255)

title({ ...
    ['Interference Maxima displacement with two highlighted fringes, ' ...
      '#' int2str(lineaPreferida) ' and #' int2str(lineaPreferidaAdjunta)], ...
    ['(for calculation of separation between fringes used in normalization)'], ...
    [ 'from ' datestr(x_start) ' to ' datestr(x_end)]})
ylabel('Fringe displacement (px)')
  
% xlabel('Date time (dd/mm HH:MM)')
% datetick('x','dd/mm HH:MM')
% ax = gca;
% ax.XTickLabelRotation = 90;  
% grid(gca,'minor')
% set(gca,'XMinorTick','on')  

config_plot
if exist('day_session') && day_session
    xlim([floor(xts(1)) floor(xts(1))+1])
end
draw_rotations(rotation0_locs, ylim, ax)
usb2018_saveFigureToFile('fringes_for_difference')

% if exist('puntosSeparacionFranjas')
% limiteSeparacionFranjas = min( ...
%     [ 500, ...
%     size(p_adjusted_hampel(:, lineaPreferida       ), 1), ...
%     size(p_adjusted_hampel(:, lineaPreferidaAdjunta), 1) ...
%     ] ...
% );
limiteSeparacionFranjas = length(p_adjusted_hampel);
% puntosSeparacionFranjas, size(p_adjusted_hampel,1);
% else
%     limiteSeparacionFranjas = size(p_adjusted_hampel,1);
% end

try
%     separacionFranjas = abs(nanmean(...
%         hampel(p_adjusted_hampel(1:limiteSeparacionFranjas,lineaPreferida) - p_adjusted_hampel(1:limiteSeparacionFranjas,lineaPreferidaAdjunta)) ...
%     ));
    separacionFranjas = abs(nanmean(...
        p_adjusted_hampel(1:limiteSeparacionFranjas,lineaPreferida) - p_adjusted_hampel(1:limiteSeparacionFranjas,lineaPreferidaAdjunta) ...
    ));
catch
    fprintf('Error en separacion franjas. Abortando operacion.')
    1/0
    return
end


errorSeparacionFranjas = nanstd(hampel( ...
        p_adjusted_hampel(1:limiteSeparacionFranjas,lineaPreferida) - p_adjusted_hampel(1:limiteSeparacionFranjas,lineaPreferidaAdjunta) ...
    )) / ...
    sqrt(length(p_adjusted_hampel(:,lineaPreferida)));

% figure
restaLineas = p_adjusted_hampel(:,lineaPreferida) - p_adjusted_hampel(:,lineaPreferidaAdjunta);
% restaLineas = hampel(restaLineas);
plot(xts, restaLineas,'gX')
hold on
plot(xts, smooth(restaLineas,20),'x')
title({'Separation between fringes ', ...
    ['d=' num2str(separacionFranjas) '+- ' num2str(errorSeparacionFranjas) 'px'], ...
    'standard error given by stddev(points)/sqrt(#points)'} ...
)
% if exist('limiteSeparacionFranjas')
%     legend(['Franja limitada a ' num2str(limiteSeparacionFranjas) 'puntos'])
% end
ylabel('Difference of displacement between two adjacent fringes (px)')
if isnan(restaLineas)
    return
end
ylim([min(restaLineas)-5 max(restaLineas)+5])


% xlabel('Date time (dd/mm HH:MM)')
% datetick('x','dd/mm HH:MM')
% 
% ax.XTickLabelRotation = 90;  
% grid(gca,'minor')
% set(gca,'XMinorTick','on')  
% if exist('day_session') && day_session
%     xlim([floor(xts(1)) floor(xts(1))+1])
% else
% %     xlim([xts(1) xts(end)])
%     xlim([x_start x_end])
% end
ax = gca;
draw_rotations(rotation0_locs, ylim, ax)
config_plot
usb2018_saveFigureToFile('separacion-franjas')
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

if ~exist('rotating_session', 'var') || ~rotating_session
    fprintf('\nWARNING: This is not a rotating session.\n\n')

    writeSummary( ...
         'sessionId', [videoId '-no-rotation']...
        ,'XX', xts ...
        ,'YY', p_adjusted_hampel_pref' ...
        ,'YYstddev', 0 ...
        ,'rotations', 0 ...
        ,'separation', 0 ...
        ,'fringe_separation', separacionFranjas ...
        ,'xts', xts ...
        ,'timeAltitude', timeAltitude ...
    );    
    
    return    
end

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Ajuste
% [fitresult, gof] = fit((1:size(p_adjusted_hampel_pref,1))',p_adjusted_hampel_pref,'smoothingspline');
fitresult = smooth(p_adjusted_hampel_pref, 11.25*20);
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% figure
% [fitresult, gof] = fit((1:size(p_adjusted_hampel_pref,1))',p_adjusted_hampel_pref,'poly2');
% [fitresult, gof] = fit((1:size(p_adjusted_hampel_pref,1))',p_adjusted_hampel_pref,'poly1')
plot(xts, p_adjusted_hampel_pref,'.')
hold on
plot(xts, fitresult(1:size(p_adjusted_hampel_pref,1)), 'rx')
xlabel('Date time (dd/mm HH:MM)')
ylabel('Fringe displacement (px)')
title({...
    'Displacement of interference fringes and Fit', ...
    ['from ' datestr(x_start) ' to ' datestr(x_end)] ...
})
legend('Original data', 'Moving average fit (120 points, 2 rotations')

% set(gca,'XMinorTick','on')
% grid on
% datetick('x', 'dd/mm HH:MM')
% ax = gca;
% ax.XTickLabelRotation = 90;
% hold on
% xlim([x_start x_end])
% ylim([ylimites(1) ylimites(2) ]);
% ylimites = ylim();
% ylimdiff = diff(ylimites);
config_plot
plotheightstar
draw_rotations(rotation0_locs, ylim, ax)
usb2018_saveFigureToFile('ajuste')

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Resta de ajuste

if ~isempty(processing_session.remove_drift) && processing_session.remove_drift
    pfit=p_adjusted_hampel_pref - fitresult(1:size(p_adjusted_hampel_pref));    
else
    pfit=p_adjusted_hampel_pref;    
end


% figure
plot(xts, pfit,'x');
% if exist('locs') & exist('tm')
%     line([tm(rotation90_locs) tm(rotation90_locs)], ylim,'color', 'k', 'linewidth', 1)
% end
% set(gca,'XLim', [startDate endDate])
% datetick('x','dd/mm HH:MM','keepticks')
% title({...
%     'Corrected fringe displacement', ...
%     ['from ' datestr(x_timestamp(1)) ' to ' datestr(x_timestamp(size(p,1)))] ...
% }) % , 'with smoothed curve' , 'with indicators of rotation'
% xlabel('Date time (dd/mm HH:MM)')
% ylabel('Corrected fringe displacement (px)')

xlabel('Date-time (dd/mm HH:MM)')
ylabel('Fringe displacement (px)')
title({...
    'Corrected Displacement of interference maxima', ...
    ['from ' datestr(x_start) ' to ' datestr(x_end)] ...
%     ,'(First 30m)' ...
}) % , 'with smoothed curve' , 'with indicators of rotation'
legend(['Displacement of maxima', char(10), 'Compass at 0ºN (laser 90ºN)'])



% grid on
% set(gca,'XMinorTick','on')
% datetick('x', 'dd/mm HH:MM')
% ax = gca;
% ax.XTickLabelRotation = 90;

config_plot

plotheightstar


% set(gca, 'XTickMode', 'auto', 'XTickLabelMode', 'auto')
% xlim([x_start x_end])
% set(gca,'XMinorTick','on')
% datetick('x', 'dd/mm HH:MM','keeplimits')
% ax = gca;
% ax.XTickLabelRotation = 90;


% config_plot
if ~isempty(processing_session.remove_drift) && processing_session.remove_drift
    ylim([-100 100])
end
draw_rotations(rotation0_locs, ylim, ax)
usb2018_saveFigureToFile('ajustada')
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Analisis de rotaciones

if ~rotationsFound
    fprintf('\nWARNING: no rotations detected. No analysis of rotation will be done.\n\n')
    writeSummary( ...
         'sessionId', [videoId '-no-rotation']...
        ,'XX', [(x_start + x_end)/2] ...
        ,'YY', pfit' ...
        ,'YYstddev', [] ...
        ,'rotations', 0 ...
        ,'separation', 0 ...
        ,'fringe_separation', separacionFranjas ...
        ,'xts', xts ...
        ,'timeRange', [x_start x_end] ...
        ,'timeAltitude', timeAltitude ...
        ,'filename', processing_session.name ...
    );    
    return
end

clear legends

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Rotaciones independientes

colors = {'r' 'b' 'g' 'y' 'k'};


clear XX YY
[XX, YY] = divideInChunks(xts, pfit, rotation0_locs, 360, orientacion);

if isempty(YY)
    fprintf('Empty YY, not enough rotation data. Neext !\n')
    return
end

errorsBars=true;

rotsgroup = 10;
rotsstep = 10;
[XXm, YYm, YYstddev] = plotInGroups(XX, YY ...
    ,'groupsize', rotsgroup ...
    ,'groupstep', rotsstep ...
    ,'saveFigures', true ...
    ,'errorBars', errorsBars ...
    ,'plotGroups', true ...
    ,'hampelParams', nan ...
    ,'normalizeBy', separacionFranjas ...
    ,'xts', xts ...
    ,'timeRange', [x_start x_end] ...
    ,'timeAltitude', timeAltitude ...       
    ,'saveTxtData', saveTxtData ...
);

writeSummary( ...
     'sessionId', [videoId '-normalized']...
    ,'XX', XXm ...
    ,'YY', YYm ...
    ,'YYstddev', YYstddev ...
    ,'rotations', rotsgroup ...
    ,'separation', rotsstep ...
    ,'fringe_separation', separacionFranjas ...
    ,'xts', xts ...
    ,'timeRange', [x_start x_end] ...
    ,'timeAltitude', timeAltitude ...
    ,'filename', processing_session.name ...
);

[XXm, YYm, YYstddev] = plotInGroups(XX, YY ...
    ,'groupsize', rotsgroup ...
    ,'groupstep', rotsstep ...
    ,'saveFigures', true ...
    ,'errorBars', errorsBars ...
    ,'plotGroups', true ...
    ,'hampelParams', nan ...
    ,'xts', xts ...
    ,'timeRange', [x_start x_end] ...
    ,'timeAltitude', timeAltitude ...
    ,'saveTxtData', saveTxtData ...
);

writeSummary( ...
     'sessionId', videoId ...
    ,'XX', XXm ...
    ,'YY', YYm ...
    ,'YYstddev', YYstddev ...
    ,'rotations', rotsgroup ...
    ,'separation', rotsstep ...
    ,'fringe_separation', separacionFranjas ...
    ,'xts', xts ...
    ,'timeRange', [x_start x_end] ...
    ,'timeAltitude', timeAltitude ...
    ,'filename', processing_session.name ...
);

errorsBars=false;
rotsgroup = 1;
rotsstep = 1;
[XXm, YYm, YYstddev] = plotInGroups(XX, YY ...
    ,'groupsize', rotsgroup ...
    ,'groupstep', rotsstep ...
    ,'saveFigures', true ...
    ,'errorBars', errorsBars ...
    ,'plotGroups', true ...
    ,'hampelParams', nan ...
    ,'xts', xts ...
    ,'timeRange', [x_start x_end] ...
    ,'timeAltitude', timeAltitude ...        
    ,'saveTxtData', saveTxtData ...
);

writeSummary( ...
     'sessionId', [videoId '-independientes'] ...
    ,'XX', XXm ...
    ,'YY', YYm ...
    ,'YYstddev', YYstddev ...
    ,'rotations', rotsgroup ...
    ,'separation', rotsstep ...
    ,'fringe_separation', separacionFranjas ...
    ,'xts', xts ...
    ,'timeRange', [x_start x_end] ...
    ,'timeAltitude', timeAltitude ...
    ,'filename', processing_session.name ...
);

