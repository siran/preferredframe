s_i_temp=smooth(i_temp,40);
s_i_pressure = smooth(i_pressure, 40);
s_i_hum = smooth(i_hum, 40);


mint = min(s_i_temp);
maxt = max(s_i_temp);

minpressures = min(s_i_pressure);
maxpressures = max(s_i_pressure);

minh = min(s_i_hum);
maxh = max(s_i_hum);

scale=1.02;
% heightOfGraph = diff(get(gca,'YLim'))*scale

figure
h1 = subplot(4,1,1)
grafico_max_hip54217  
h2 = subplot(4,1,2)
plot(xts,s_i_temp,'.-','linewidth', 1,'color','red');
xlim(h2, [startDate endDate+1/2]);
set(h2, 'Visible','on',  'YAxisLocation','left', 'YLim',[mint maxt], 'XTick', startDate:endDate+1/2, 'YDir', 'reverse');
datetick('x','dd/mm HH:MM','keepticks')
legend('temperature °C', 'NorthEast')

% figure
% h1 = subplot(2,1,1)
% grafico_max_hip54217  

% % h2 = subplot(4,1,3)
% % plot(xts,s_i_pressure,'.-','linewidth', 1,'color','red');
% % xlim(h2, [startDate endDate+1/2]);
% % set(h2, 'Visible','on',  'YAxisLocation','left', 'YLim',[minpressures maxpressures], 'XTick', startDate:endDate+1/2);
% % datetick('x','dd/mm HH:MM','keepticks')
% % legend('pressure (hPa)', 'NorthEast')

% figure
% h1 = subplot(2,1,1)
% grafico_max_hip54217  
h2 = subplot(4,1,3)
plot(xts,s_i_hum,'.-','linewidth', 1,'color','red');
xlim(h2, [startDate endDate+1/2]);
set(h2, 'Visible','on',  'YAxisLocation','left', 'YLim',[minh maxh], 'XTick', startDate:endDate+1/2);
datetick('x','dd/mm HH:MM','keepticks')
legend('relative humidity (%RH)', 'NorthEast')


h2 = subplot(4,1,3)
plot(xts, p, xts, p - ct*(s_i_temp-meant) + ch*(s_i_hum-meanh), 'green');
xlim(h2, [startDate endDate+1/2]);
set(h2, 'Visible','on',  'YAxisLocation','left', 'YLim',[minh maxh], 'XTick', startDate:endDate+1/2);
datetick('x','dd/mm HH:MM','keepticks')
legend('relative humidity (%RH)', 'NorthEast')
