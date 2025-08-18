function plot_summary(varargin);
% makes plot of the summary file
timeAltitude = evalin('base', 'timeAltitude');

if ~exist('timeAltitude')
    readdatetimealt
end

filename = 'C:\Users\an\Documents\megasync-preferredframe\figures\summaryv2-190412-190417.csv';
% filename = 'C:\Users\an\Documents\megasync-preferredframe\figures\summaryv2-190404-190405.csv';
filename = 'C:\Users\an\Documents\megasync-preferredframe\figures\summaryv2-190422_1530-190423_1400.csv';
filename = 'C:\Users\an\Documents\megasync-preferredframe\figures\figures-180914_2030-180915_1730\summaryv2-180914_2030-180915_1730.csv';
% filename = 'C:\Users\an\Documents\megasync-preferredframe\figures\figures-180920_1930-180920_2330\summaryv2-180920_1930-180920_2330.csv';
% filename = 'C:\Users\an\Documents\megasync-preferredframe\figures\figures-180921_0730-180923_1800\summaryv2-180921_0730-180923_1800.csv';
% filename = 'C:\Users\an\Documents\megasync-preferredframe\figures\summaryv2-180914_2030-180915_1730.csv';
% filename = 'C:\Users\an\Documents\megasync-preferredframe\figures\summaryv2-180920_0730-190427_0430.csv';
% filename = 'C:\Users\an\Documents\megasync-preferredframe\figures\figures-181008_1930-181012_0830\summaryv2-181008_1930-181012_0830.csv';
% filename = 'C:\Users\an\Documents\megasync-preferredframe\figures\summaryv2-190422_1530-180927_0430.csv';
filename = 'C:\Users\an\Documents\megasync-preferredframe\figures\figures-181215_1030-181216_1230\summaryv2-181215_1030-181216_1230.csv';

summary = table2struct(readtable(filename));

n=0;
a=0;
for i=1:length(summary)
    if strfind([summary(i).sessionId], 'normalized')
        n = n+1;
        datesn(n) = datenum(summary(i).datetime);
        amplituden(n) = summary(i).amplitude;
        altituden(n) = summary(i).average_altitude;
    else
        a=a+1;
        datesa(a) = datenum(summary(i).datetime);
        amplitudea(a) = summary(i).amplitude;
        altitudea(a) = summary(i).average_altitude;
    end
    
end

[tmp ind]=sort([datesn]);

datesn = datesn(ind);
amplituden = amplituden(ind);
altituden = altituden(ind);



% altituden = altituden/max(altituden) ;
% * ...
%     (max(amplituden) - min(amplituden))/2 
% + ...
%     (max(amplituden) - min(amplituden))/2

amplituden = hampel(amplituden,4,2);

plot(datesn, amplituden, 'x')
ylabel('Displacement of Maxima (normalized)');
set(gca,'XMinorTick','on')
grid on

ax = gca;
ax.XTickLabelRotation = 90;

xtickat = floor(min(datesn)):0.25:max(datesn);
set(gca, 'XTick', xtickat, 'XTickLabel', 'auto')
datetick('x', 'dd/mm HH:MM', 'keepticks')

xlabel('Date-time (dd/mm HH:MM)')


startdate = min(datesn);
enddate = max(datesn);
diffdate = round(enddate - startdate, 2)
title({'Amplitude of fringe movement', 'a point every 1/2 hour ', ...
    ['from ' datestr(startdate) ' to ' datestr(enddate) ' - ' num2str(diffdate) ' days']})
legend('Fringe displacement (normalized)')
xlim([min(datesn) max(datesn)])

yyaxis right
ylim([-190 190])
plot(timeAltitude(:,1), timeAltitude(:,2),'-')
% plot(datesn, altituden/max(altituden)*max(amplituden)*.8,'-')
ylabel('Altitude star (º)');
% title({'Amplitude of fringe movement', 'a point every 1/2 hour'})
legend('Fringe displacement (normalized)', 'Star altitude')


