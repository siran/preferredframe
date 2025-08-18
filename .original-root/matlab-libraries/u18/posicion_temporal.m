i=0;
fprintf('\n\nExtraccion de puntos de la gráfica (usa variable fechas_max_min):\n');


    for t=1:size(fechas_max_min,2)
        fechas_max_min(t).datenum = mat2str(datenum(fechas_max_min(t).Position(1)));
    end
    [tmp ind]=sort({fechas_max_min.datenum});
    fechas_max_min = fechas_max_min(ind);
    
for j=1:size(fechas_max_min,2)
    i=i+1;
    fprintf(' - punto: %i fecha hora: %s altura: %i \n',i, datestr(fechas_max_min(i).Position(1)),fechas_max_min(i).Position(2))
    maxmin(j,1) = fechas_max_min(i).Position(1);
    maxmin(j,2) = fechas_max_min(i).Position(2);
end
% figure;
% plot(diff(maxmin(:,1)));
% figure;
% plot(maxmin(:,2));