% Para analizar las capturas hechas en la universidad 
%  en este archivo se lleva un vector con el timestamp de cada foto

clc

clear all
fprintf('hola');

path_images = 'C:\Users\Admin\Documents\fisica\experimento usb\lab\capturas-101124-aire-vidrio2\';

fprintf('Procesando directorio %s \n\n', path_images );

% leo archivos
files_images = dir(strcat(path_images,'*.jpg'));

% ordeno por fecha
for t=1:size(files_images)
    files_images(t).datenum = mat2str(datenum(files_images(t).date));
end
[tmp ind]=sort({files_images.datenum});
files_images = files_images(ind);

%  maxfiles =500;
maxfiles = size(files_images);


for i=1:(maxfiles)
    locs = [0];
    peaks= [0];    
    name_image = files_images(i).name;

    full_name_image = strcat(path_images, name_image);
    
    x_timestamp(i) = datenum(files_images(i).date);
   
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
      
    perfil = imagenbw(65,77:263);
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

% corrige_pendiente

% hace el grafico
grafico_max



