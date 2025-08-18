% stitches pre-analized data
% uses the saved workspaces

% default variables


clc

pictures_base_folder = 'D:\Users\an\experimento-usb-interferometro\tobo-ordenado'
workspace_folder = 'D:\Users\an\experimento-usb-interferometro\u18_workspaces';

workspaces = dir([workspace_folder '\wn2002??_????-adjusted_orig.mat']);

p_struct = struct();
% figure 
% hold on
for wsi = 1:length(workspaces)
    ws = workspaces(wsi);
    % disp("Stitching " + ws.name);
    
    clear p_adjusted_orig lineaPreferida fconf conf;

    load([ws.folder '\' replace(ws.name, '-adjusted_orig', '')]);
    load([ws.folder '\' ws.name]);

    if exist(fconf, "file")
        conf = readtable(fconf);   
        p_struct(wsi).p = p_adjusted_orig(:, conf.lineaPreferida);

        p_struct(wsi).lineaPreferida = conf.lineaPreferida;
        p_struct(wsi).lineaPreferidaAdjunta = conf.lineaPreferidaAdjunta;
        
        p_struct(wsi).p_lineaPreferida = p_adjusted_orig(:, conf.lineaPreferida);
        p_struct(wsi).linea_preferidaAdjunta = p_adjusted_orig(:, conf.lineaPreferidaAdjunta);
    end

    p_struct(wsi).p_all = p_adjusted_orig;
    p_struct(wsi).p_orig = p_orig;
    p_struct(wsi).xts = xts;
    p_struct(wsi).size = length(xts);
    p_struct(wsi).orientacion = orientacion;

    % plot(p_struct(wsi).xts, p_struct(wsi).p_all);

    % refresh
    % a=1:
end

