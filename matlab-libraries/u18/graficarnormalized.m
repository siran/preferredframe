curva = 14;

markerType = '.-';
[pressure,temp,hum,tt] = importtph();
tm=x2mdate(tt);

plotnorm(xts,p_adjusted(:,14),['r' markerType])
hold on
plotnorm(tm,temp,['b' markerType])
xlim([min(xts) max(xts)])

figure
plotnorm(xts,p_adjusted(:,14),['r' markerType])
hold on
plotnorm(tm,pressure, ['g' markerType])
xlim([min(xts) max(xts)])

figure
plotnorm(xts,p_adjusted(:,14),['r' markerType])
hold on
plotnorm(tm,hum,['k' markerType])

xlim([min(xts) max(xts)])