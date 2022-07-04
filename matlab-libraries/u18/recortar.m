%recortar data de la dereiva inicial

figure
grafico_max_hip54217

ti = nan;
input('si lo desea, especifique el punto de comienzo con un datatip, exportela como ti y presione [enter]');
if isstruct(ti)
    p = p_orig(ti.DataIndex:size(p_orig,1),:);
    x_timestamp = x_timestamp_orig(1,ti.DataIndex:size(x_timestamp_orig,2));
end

xts = x_timestamp';

figure
grafico_max_hip54217

ajustar = input('desea ajustar la data (unificar en una linea)? [s]/n', 's');
if ajustar == 's'
    p_adjusted = adjustdata(p);
    p = p_adjusted;
end

hold off
grafico_max_hip54217

importart = input('desea importar la temperatura? s/n', 's');
if importart == 's'
    [tt temp_orig] = importtemp;
    temp = temp_orig;
end
if exist('tt') && exist('temp') && size(tt,1)>1 && size(temp,1)>1
    figure
    grafico_max_hip54217        
    graficar_temp_con_ejes
end
    

resp = input('desea escoger la mejor fila y suavizar? s/n', 's');
if resp == 's'
    figure
    findbettercol
end

resp = input('desea restar efecto de temperatura? s/n', 's');
if resp == 's'
    figure
    pminusslope
end