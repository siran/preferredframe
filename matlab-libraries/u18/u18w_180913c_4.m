clear p x_timestamp xts ps peaks locs p_orig x_timestamp_orig perfiles lineaPreferida puntosSuavizadoPreferido tt azimuth rotationStop

warning('off', 'MATLAB:imagesci:tifftagsread:expectedTagDataFormat')
warning('off', 'images:initSize:adjustingMag')
warning('off', 'MATLAB:audiovideo:VideoWriter:noFramesWritten')

animar = false

global pathToFigures
global saveFile
global frameToTime
global xts
global p_orig
global videoId

path_images = 'C:\Users\an\Documents\megasync-preferredframe\180913c_4\';
videoId = 'w180913c_4'

lineaPreferida=3;
lineaPreferidaAdjunta=4;
suavizar=false;
stepFrames = 1;
ajustarDefault = true;
% saveLogFile('init')
graficoAzimuth = true;
limitesGraficasPromediada = false;
rotacionini = 1;
rotationStop = false;
rotationAngle = 0;
filterDiskSize = 20;
puntosSeparacionFranjas=1000;

pathToFigures = 'C:\Users\an\Documents\megasync-preferredframe\figures\';
saveFile = true;
figureCreated = false;

if exist('onlyLoadConfig') && onlyLoadConfig == true
    return
end

u18_analisis_fotos