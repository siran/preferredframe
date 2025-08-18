function plotAnalisys(table, varargin)
% plots data obtained in the analysis summary

divisions_day = 48;
figure_type = 'normalized';
sidereal_correction = true;

nVarargs = length(varargin);
for k = 1:2:nVarargs
    if strcmp(varargin{k}, 'divisions_day')
        divisions_day = varargin{k+1};
    elseif strcmp(varargin{k}, 'figure_type')
        figure_type = varargin{k+1};     
    elseif strcmp(varargin{k}, 'sidereal_correction')
        sidereal_correction = varargin{k+1};             
    end
end

seconds_sidereal_day = 86164.0905;
seconds_solar_day = 24*60*60;
solar2sideral_ratio = seconds_sidereal_day / seconds_solar_day;

divisions_day_str = int2str(divisions_day);

if sidereal_correction
    divisions_day_str = [int2str(divisions_day) '-div-' 'corregido-sideral-'];
else
    divisions_day_str = [int2str(divisions_day) '-div-' 'no-corregido-sideral-'];
end

datastruct = table2struct(table);
num_sessions = length(datastruct);

%% pick only normalized sessions
count = 0;
for i = 1:num_sessions
    if strcmp(datastruct(i).figure_type, figure_type)
        count = count + 1;
        times(count) = datenum(datastruct(i).datetime);
        amplitudes(count) = datastruct(i).amplitude;
        session_ids{count} = datastruct(i).sessionId;
    end
end

num_sessions = length(times);

[y,i] = hampel(amplitudes);
 
amplitudes = amplitudes(~i);
times = times(~i);
session_ids = session_ids(~i);

% % %% get unique session names
% % l = length(session_ids);
% % unique_session_ids = {};
% % for i=1:length(session_ids)
% %     found = false;
% %     underscore_index = strfind(session_ids{i}, '_');
% %     day_name_session = session_ids{i}(1:underscore_index-1);
% %     for i2=1:length(unique_session_ids)
% %         if strcmp(day_name_session, unique_session_ids{i2})
% %             found = true;
% %             break
% %         end
% %     end
% %     if ~found
% %         unique_session_ids{end+1} = day_name_session;
% %     end
% % end

%% add session count to session_id



plot(times,amplitudes,'.')
title('Cleaned data from sessions (outliers removed)')
xlabel('Fecha (yyyy-mmm-dd HH:MM)')
ylabel('Desplazamiento normalizado de franjas (# franjas)')

% xlim([min(t) max(t)])
datetick('x', 'yyyy-mmm-dd HH:MM', 'keepticks')

usb2018_saveFigureToFile([divisions_day_str '-div-cleaned-data'])


%% sidereal correction

if sidereal_correction
    t_0 = times(1);
    sideral_day_diff = (times - t_0)*solar2sideral_ratio;
    times = t_0 + sideral_day_diff;
    
    plot(times,amplitudes,'.')
    title('Cleaned data from sessions (outliers removed) in Sideral Time')
    xlabel('Fecha (yyyy-mmm-dd HH:MM)')
    ylabel('Desplazamiento normalizado de franjas (# franjas)')

    datetick('x', 'yyyy-mmm-dd HH:MM', 'keepticks')

    usb2018_saveFigureToFile([divisions_day_str  'cleaned-data-sidereal-time'])
    
end

%% datetime to date

times = times - floor(times);


%%

amplitudes_division = nan(divisions_day,20);
for i = 1:length(times)
    particion = floor(times(i)/(1/divisions_day)) + 1;
%     aa(particion,1) = aa(particion,1) + 1;
%     fprintf('%d %f', t, a(i))
    medicion = sum(amplitudes_division(particion,:)>0) + 1;
    amplitudes_division(particion,medicion) = amplitudes(i);
end


amplitudes_division(amplitudes_division==0) = nan;
amplitudes_div_hampeled = hampel(amplitudes_division);
% amplitudes_div_hampeled(i) = nan;

%% removing < 0.2 and > 0.7
% ii = amplitudes_div_hampeled>0.4 & amplitudes_div_hampeled<0.65;
% amplitudes_div_hampeled = amplitudes_div_hampeled .* ii;
% amplitudes_div_hampeled(amplitudes_div_hampeled==0) = nan;

for i = 1:divisions_day
    
    raw_measurements = amplitudes_div_hampeled(i,:);
%     [j,k] = hampel(raw_measurements);
    measurements{i} = raw_measurements;
    measurements_removed{i}  = [];%raw_measurements(k);
    avg(i) = mean(measurements{i}, 'omitnan');
    error_bars(i) = std(measurements{i})/sqrt(length(measurements{i}));
end

% avg = hampel(avg,3,1);

sineFit((1:divisions_day)*(1/divisions_day), avg)
hFigPlotSin = findobj( 'Type', 'Figure', 'Tag', 'Fig$PlotSin' );
hFigPlotFFT = findobj( 'Type', 'Figure', 'Tag', 'Fig$PlotFFT' );

figure(hFigPlotSin)
title({'Ajuste sinusoidal al promedio de sesiones para el día',...
    '(la hora de la sesion se redondea a la media hora más cercana'})
xlabel('Fracción del día')
ylabel('Desplazamiento en # de franjas')
usb2018_saveFigureToFile([divisions_day_str  'ajuste-sinuoidal'])

figure(hFigPlotFFT)
title({'Análisis de Fourier para el ajuste sinusoidal'})
usb2018_saveFigureToFile([divisions_day_str  'analisis-fourier'])


%%

% for i=1:divisions_day
%    
% promedio(i) = mean(amplitudes_div_hampeled(i,:), 'omitnan');
%     barraerror(i) = std(aah(i,:), 'omitnan')/sqrt(sum(~isnan(aah(i,:))));
% end
figure
errorbar((1:divisions_day)*(1/divisions_day),avg, error_bars,'o')
title('Desplazamiento de franjas vs hora del día sideral')
ylabel('Desplazamiento en número de franjas')
xlabel('Hora del día')
hold on 
plot((1:divisions_day)*(1/divisions_day),smooth(avg),'r-')


for i=1:size(amplitudes_div_hampeled,1)
    plot(ones( length(measurements{i})        , 1)*i/divisions_day, measurements{i},        '*', 'Color', [0 .5 0])
    hold on
    plot(ones( length(measurements_removed{i}), 1)*i/divisions_day, measurements_removed{i},'o', 'Color', [.5 .5 .5])
end
% plot((1:divisions_day)*(1/divisions_day),aa','x-')
% plot((1:divisions_day)*(1/divisions_day),aah,'r-')
datetick('x', 'HH:MM', 'keepticks')

legend({'Promedio de medidas', 'Media movil del promedio', 'Amplitud pico-pico en sesion'})
usb2018_saveFigureToFile([divisions_day_str  'fringe-displacement-in-sideral-time'])

