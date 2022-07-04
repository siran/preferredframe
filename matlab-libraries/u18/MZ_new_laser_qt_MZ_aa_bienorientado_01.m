% Para analizar las capturas hechas en la universidad 
%  en este archivo se lleva un vector con el timestamp de cada foto

% clc

clear p x_timestamp 
fprintf('\n');

path_images = 'C:\Users\AMR\Documents\fisica\20140520-mz-aa-bienorientado-01\capturas\';

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
p = zeros(maxfiles(1),10);

t=0;
for i=1:(maxfiles)
    
    locs = [0];
    peaks= [0];    
    name_image = files_images(i).name;

    full_name_image = strcat(path_images, name_image);
    
    x_timestamp(i) = datenum(files_images(i).date);
   
    if (mod(i,10)==0) 
        fprintf('- %d/%d (%6.2f) ', i, maxfiles(1), round(i/maxfiles(1)*10000)/100);
    end
    if (mod(i,50)==0) 
        fprintf('\n');
    end    
    
    [imagen map]= imread(full_name_image);
     imagen = rgb2gray(imagen);
     imagen = imadjust(imagen);
     imagen = imrotate(imagen, -50);     
    imagen = imfilter(imagen,fspecial('gaussian',20,5));

       
% if i==1020
% 	fprintf('%d ', i);
% end
    
%     imagen = imagen.' ;
      
    perfil = imagen(300, 112:343);
    perfil = double(perfil);
    perfil=smooth(perfil);
% 
    perf = perfil;
%     show = round(maxfiles/20);
%     if (mod(i,show(1,1))==0)
%         figure;
%         plot(perfil)
%         a=2
%     end     
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
    perfiles(i,:,:) = perfil;

% hold off;
%     plot(perfil);
%     hold on
%     plot(locs,peaks,'o')
%     hold off
    

%     [peaks locs] = findpeaks(perfil);
%  
%     fprintf('\n');
%     for m=1:cuentaPicos
%         fprintf('%d ', locs(m));
%     end
%     fprintf('\n');


%      perfil(locs) = 200;
     
      p(i,1:cuentaPicos) = locs;
     
%     if imagenbw(155,120) ~= 0
        t = t + 1;
%         m(i,1) = imagenbw(79,117);
%         m(i,2) = imagenbw(88,129);
%         m(i,3) = imagenbw(95,141);

%         m(i,1) = imagenbw(170,117);  
%         m(i,2) = imagenbw(152,129);
%         m(i,3) = imagenbw(192,141);        
%     end


    if mod(i,50)==0
%          return
%        figure
%        plot(perfil)
%        hold;
%        plot(locs, peaks,'o')
    end

      


      
end

p_complete = p;
x_timestamp_complete = x_timestamp;

% p_adjusted=adjustdata(p_complete);
% p = p_adjusted;

figure
grafico_max_hip54217

ti = nan;
ti = input('si lo desea, especifique el punto de comienzo con un datatip, exportela como ti y presione [enter]');
if ~isempty(ti)
    p = p(ti,DataIndex:size(p,1), :);
    x_timestamp = x_timestamp(1,ti.DataIndex:size(x_timestamp,2));
end

xts = x_timestamp';

hold off
grafico_max_hip54217


[tt temp] = importtemp;

if size(tt,1)>1 && size(tt,1)>1
    graficar_temp_con_ejes
end

% hold on
% 
% % plot(x_timestamp, smooth(double(m),160)/max(smooth(double(m),160))*250,'-','color',colors{1},'linewidth',2)
% % plot(x_timestamp, smooth(double(m),3)/max(smooth(double(m),3))*250,'.','color',colors{1})
% 
% colors = {'blue','red','black'};
% 
% hold on
% for n = 1:size(m,2)
%     plot(x_timestamp, smooth(double(m(:,n)),100)/max(smooth(double(m(:,n)),100))*250,'-','color',colors{n},'linewidth',2)
% end

% corrige_pendiente

% hace el grafico

clear path_images tmp ind maxfiles locs peaks name_image full_name_image 
clear imagen