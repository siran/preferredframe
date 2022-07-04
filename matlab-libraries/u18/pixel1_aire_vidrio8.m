% Para analizar las capturas hechas en la universidad 
%  en este archivo se lleva un vector con el timestamp de cada foto

clc

clear p x_timestamp 
fprintf('hola');

path_images = 'C:\Users\Admin\Documents\fisica\experimento usb\lab\capturas-aire-vidrio-8\capturas\';

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

t=0;
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
      
    perfil = imagenbw(49,60:275);
    perfil = double(perfil);
    perfil=smooth(perfil);
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
     
%     if imagenbw(155,120) ~= 0
        t = t + 1;
%         m(i,1) = imagenbw(79,117);
%         m(i,2) = imagenbw(88,129);
%         m(i,3) = imagenbw(95,141);

        m(i,1) = imagenbw(170,117);  
        m(i,2) = imagenbw(152,129);
        m(i,3) = imagenbw(192,141);        
%     end


    if mod(i,50)==0
%          return
%        figure
%        plot(perfil)
%        hold;
%        plot(locs, peaks,'o')
    end

      


      
end
figure
grafico_max_hip54217

hold on

% plot(x_timestamp, smooth(double(m),160)/max(smooth(double(m),160))*250,'-','color',colors{1},'linewidth',2)
% plot(x_timestamp, smooth(double(m),3)/max(smooth(double(m),3))*250,'.','color',colors{1})

colors = {'blue','red','black'};

hold on
for n = 1:size(m,2)
    plot(x_timestamp, smooth(double(m(:,n)),100)/max(smooth(double(m(:,n)),100))*250,'-','color',colors{n},'linewidth',2)
end

% corrige_pendiente

% hace el grafico




