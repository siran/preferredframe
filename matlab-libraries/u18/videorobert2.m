clear all

xyloObj = VideoReader('C:\Users\an\Documents\fisica\michelson-morley\robert\142809 ensayo2\M2U00216.avi');

% nFrames = xyloObj.NumberOfFrames
% vidHeight = xyloObj.Height
% vidWidth = xyloObj.Width

maxfiles = xyloObj.NumberOfFrames;
p = zeros(maxfiles(1),20);

t=0;
tini=tic;
% frame 15103 corresponde a las 5:57pm del 20/09/2007
for i=1:(maxfiles)
    if ~(mod(i,30)==0)
        continue
    end
    if (mod(i,200)==0)
        elapsed = toc(tini)/60;
        total = (maxfiles(1)*elapsed/i);
        faltante = (total-elapsed);
        fprintf('%d/%d - %6.1f - total est.: %4.2f min, transcurridos: %4.2f min, faltante: %4.2f min \n', i, maxfiles(1), round(i/maxfiles(1)*10000)/100, total, elapsed, faltante);
    end    
    
    imagen = read(xyloObj, i);

    imagen = rgb2gray(imagen);
    imagen = imadjust(imagen);
    imagen = imrotate(imagen, 21);     
    imagen = imfilter(imagen,fspecial('gaussian',80,10));
      
    perfil = imagen(404, 281:560);
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
    clear locs;
    cuentaPicos = 1;
    locs(cuentaPicos) = 0;
    distanciaEntrePicos = 30;
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
    
      p(i,1:cuentaPicos) = locs;
end
