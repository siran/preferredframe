%%%%
% TODO:
% - convertir script con una funcion para no repetir codigo
% - hacer las divisiones del dia a 48, 24, 6 horas
% - entender por que se ven muchas medidas con la misma amplitud en la
% grafica donde salen las barras de error, las medidas y el promedio
%   - quizas ayude: pintar cada punto con el color de la sesion
%   - quizas ayude: hacer graficos por sesion a ver que dan individualmente
% - poner leyenda con el nombre de cada sesion asociada al color


clear all

global saveFile
saveFile = true;

global pathToFigures
pathToFigures = 'D:\Users\an\experimento-usb-interferometro\figures-analysis\';    

pathToAnalysis = 'D:\Users\an\experimento-usb-interferometro\analysis-summaries\';

% to save pictures
global analysis_name

divisions_day = 48;
analysis_name = [ ...
%     '180818-181216'...
%     '20191001-20191019'
    '20191101-20191124'
];

for sindex=1:size(analysis_name, 1)
    analisys_summary_filename = [ pathToAnalysis analysis_name '.csv'];

    table = readtable(analisys_summary_filename);

    plotAnalisys(table ...
        , 'divisions_day', divisions_day ...
        , 'figure_type', 'normalized' ...
    )

    plotAnalisys(table ...
        , 'divisions_day', divisions_day ...
        , 'figure_type', 'normalized' ...
        , 'sidereal_correction', false ...
    )    
end



