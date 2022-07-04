figure
grafico_max_hip54217


figure
grafico_max_hip54217
hold on
graficar_temp_con_ejes

% xlim([min(x_timestamp) max(x_timestamp)+1/2]);
% axes('Position',get(ax1,'Position'),...
% 'Color','none',...
% 'XColor','k','YColor','k','XTick',-1,...
% 'YAxisLocation','right',...
% 'YLim',[mint maxt]);

figure
% if ~exist('p_complete')
%     p_complete = p;
% end
% p = p(:,11);

subplot(2,1,1);

grafico_max_hip54217

subplot(2,1,2);

scale=1;
heightOfGraph = diff(get(gca,'YLim'))*scale



hold on
plot(tm,temps,'.-','linewidth', 1,'color','red');
set(gca,'Visible','on',  'YAxisLocation','right', 'YLim',[mint/scale maxt*scale]);
xlim([startDate endDate+1/2]);
set(gca,'XTick',startDate:12/24:endDate+1/2)
set(gca,'XMinorTick','on')
set(gca,'Box','off');
datetick('x','dd/mm HH:MM','keepticks')
% graficar_temp_con_ejes
% 


