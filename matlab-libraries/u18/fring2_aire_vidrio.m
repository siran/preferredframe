clc

clear all
fprintf('hola');

path_images = 'C:\Users\Admin\Documents\fisica\experimento usb\lab\capturas-101116-aire-vidrio-5-nuevo\';
fprintf('Procesando directorio %s \n\n', path_images );

% leo archivos
files_images = dir(strcat(path_images,'*.jpg'));

% ordeno por fecha
[tmp ind]=sort({files_images.date});
files_images = files_images(ind);

%  maxfiles =500;
maxfiles = size(files_images);


for i=1:(maxfiles)
    locs = [0];
    peaks= [0];    
    name_image = files_images(i).name;

    full_name_image = strcat(path_images, name_image);
   
    if (mod(i,10)==0) 
        fprintf('%d ', i);
    end
    if (mod(i-1,200)==0) 
        fprintf('\n');
    end    
    
    [imagen map]= imread(full_name_image);
     imagenbw = rgb2gray(imagen);
%     imagenbw = imrotate(imagenbw, -90);
       

    
%     imagen = imagen.' ;
      
    perfil = imagenbw(175,100:250);
    perfil = double(perfil);
    perfil=smooth(perfil.^5,3);
% 
    perf = perfil;
%     xd = 1:size(perfil);
%     [curve, goodness] = fit(xd', perfil, 'sin8');
%     perfil = double(curve(1:size(perfil)));
    cuentaPicos = 0;
    distanciaEntrePicos = 6;
    for k=2:size(perfil)-1
        if perfil(k)>=perfil(k-1) && perfil(k)>=perfil(k+1) && (k - locs(size(locs,1)) >= distanciaEntrePicos)
            cuentaPicos = cuentaPicos + 1;
            locs(cuentaPicos) = k;
            peaks(cuentaPicos) = perfil(k);
%             fprintf('%4d ', locs(size(locs, 2)));
        end
    end
%      fprintf('\n');
    
    perfil=perf;


%     [peaks locs] = findpeaks(perfil);
%  
%     fprintf('\n');
%     for m=1:cuentaPicos
%         fprintf('%d ', locs(m));
%     end
%     fprintf('\n');


%      perfil(locs) = 200;
     
      p(i,1:cuentaPicos) = locs;
    if mod(i,50)==0
%          return
%        figure
%        plot(perfil)
%        hold;
%        plot(locs, peaks,'o')
    end

      


      
end

figure

startDate = datenum(files_images(1).date);
endDate = datenum(files_images(size(p,1)).date);
xData = linspace(startDate,endDate,size(p,1));

plot(xData, p,'.')

set(gca,'Position', [0.05 0.05 0.93 0.85])
set(gca,'XLim', [startDate endDate+4/24])
set(gca,'XTick',startDate:(2/24):endDate+2/24)
datetick('x','HH:MM','keepticks')



 
title(['Movimiento de Máximos de Interferencia: del ' files_images(1).date ' al ' files_images(size(p,1)).date],'FontSize', 16)
xlabel('Hora (HH:MM)');
ylabel('Posicion del Maximo (pixels)');

puntosPor4Horas = 480;

% ptemp = p;
% for i=1:floor(size(ptemp,1)/puntosPor4Horas)
%     figure
%     inicio = (i-1)*puntosPor4Horas+1;
%     if (size(ptemp,1) - i*puntosPor4Horas) < puntosPor4Horas
%         fin = size(p,1);
%     else
%         fin = inicio + puntosPor4Horas - 1;
%     end
%     p = ptemp(inicio:fin, :);
%     
%     startDate = datenum(files_images(inicio).date);
%     endDate = datenum(files_images(fin).date);
%     xData = linspace(startDate,endDate,size(p,1));
% 
%     plot(xData, p,'.')
% 
%     set(gca,'XTick',startDate:(4/24):endDate)
%     datetick('x','HH:MM','keepticks')
% 
%     set(gca,'XLim', [startDate-1/60 endDate+1/60])
%     set(gca,'Position', [0.02 0.05 0.98 0.85])
% 
%     title(['Movimiento de Máximos de Interferencia: del ' files_images(inicio).date ' al ' files_images(fin).date],'FontSize', 16)
%     xlabel('Hora (HH:MM)');
%     ylabel('Posicion del Maximo (pixels)');
% end
% p=ptemp;

