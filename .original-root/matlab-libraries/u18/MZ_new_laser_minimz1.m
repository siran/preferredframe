% Para analizar las capturas hechas en la universidad 
%  en este archivo se lleva un vector con el timestamp de cada foto

% clc

clear p x_timestamp 
fprintf('\n');

path_images = 'C:\Users\an\Documents\fisica\michelson-morley\2014-09-23 mini mz 2\capturas\';

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
tini=tic;
for i=1:(maxfiles)
    
    locs = [0];
    peaks= [0];    
    name_image = files_images(i).name;

    full_name_image = strcat(path_images, name_image);
    
    x_timestamp(i) = datenum(files_images(i).date);
   
    if (mod(i,200)==0)
        elapsed = toc(tini)/60;
        total = (maxfiles(1)*elapsed/i);
        faltante = (total-elapsed);
        fprintf('%d/%d - %6.1f - total est.: %4.2f min, transcurridos: %4.2f min, faltante: %4.2f min \n', i, maxfiles(1), round(i/maxfiles(1)*10000)/100, total, elapsed, faltante);
    end
    
    [imagen map]= imread(full_name_image);
     imagen = rgb2gray(imagen);
     imagen = imadjust(imagen);
%      imagen = imrotate(imagen, -50);     
    imagen = imfilter(imagen,fspecial('gaussian',20,5));

       
% if i==1020
% 	fprintf('%d ', i);
% end
    
%     imagen = imagen.' ;
      
    perfil = imagen(200, 76:312);
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

if ~exist('p_orig')
    p_orig = p;
end
if ~exist('x_timestamp_orig')
    x_timestamp_orig = x_timestamp;
end

xts = x_timestamp';


fprintf('Deberia ejecutar los programas: \n - recortar \n - findbettercol\n - pminusslope\n');

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