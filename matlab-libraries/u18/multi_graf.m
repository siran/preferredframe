clear inicio fin
puntosPor4Horas = 1*24*60*2;

ptemp = p;
x_timesamp_temp = x_timestamp;
for i=1:floor(size(ptemp,1)/puntosPor4Horas)

    inicio = (i-1)*puntosPor4Horas+1;
    if (size(ptemp,1) - i*puntosPor4Horas) < puntosPor4Horas
        fin = size(p,1);
    else
        fin = inicio + puntosPor4Horas - 1;
    end
    p = ptemp(inicio:fin, :);
    x_timestamp = x_timesamp_temp(inicio:fin);
    
    grafico_max_hip54217
% figure
% plot(x_timestamp, p,'.')
% datetick('x','dd_HH:MM','keepticks')
end
p=ptemp;
x_timestamp = x_timesamp_temp;