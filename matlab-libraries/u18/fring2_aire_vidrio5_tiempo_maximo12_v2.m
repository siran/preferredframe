% Para analizar las capturas hechas en la universidad 
%  en este archivo se lleva un vector con el timestamp de cada foto

clc

clear p x_timestamp 
fprintf('hola');

path_images = 'C:\Users\Admin\Documents\fisica\experimento usb\lab\capturas-101219-vidrio5\capturas\';

fprintf('Procesando directorio %s \n\n', path_images );

if (~exist('files_images'))
    % leo archivos
    files_images = dir(strcat(path_images,'*.jpg'));

    % ordeno por fecha
    for t=1:size(files_images)
        files_images(t).datenum = mat2str(datenum(files_images(t).date));
    end
    [tmp ind]=sort({files_images.datenum});
    files_images = files_images(ind);
end

%  maxfiles =500;
maxfiles = size(files_images);


for i=1:(maxfiles)
%     if ~(mod(i,20)==0) 
%         continue
%     end     
    locs = [0];
    peaks= [0];    
    name_image = files_images(i).name;

    full_name_image = strcat(path_images, name_image);
    
    x_timestamp(i) = datenum(files_images(i).date);
   
    if (mod(i,10)==0) 
        fprintf('%d ', i);
    end
    if (mod(i,200)==0) 
        fprintf('\n');
    end    
    
    [imagen map]= imread(full_name_image);
     imagenbw = rgb2gray(imagen);
%     imagenbw = imrotate(imagenbw, -90);
       

    
%     imagen = imagen.' ;
      
    perfil = imagenbw(95,25:317);
    perfil = double(perfil);
    perfil=smooth(perfil.^5,3);
% 
    perf = perfil;
%     xd = 1:size(perfil);
%     [curve, goodness] = fit(xd', perfil, 'sin8');
%     perfil = double(curve(1:size(perfil)));
    cuentaPicos = 1;
    locs(cuentaPicos) = 0;
    distanciaEntrePicos = 3;
    for k=2+distanciaEntrePicos:size(perfil)-1-distanciaEntrePicos
        if perfil(k)>=perfil(k-1) && perfil(k)>=perfil(k+1)
            if (perfil(k) >= max(perfil(k-distanciaEntrePicos:k+distanciaEntrePicos)) ) %&& k-locs(cuentaPicos)>distanciaEntrePicos
                cuentaPicos = cuentaPicos + 1;
                locs(cuentaPicos) = k;
                peaks(cuentaPicos) = perfil(k);
            end
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
grafico_max_hip54217



