function ret = saveFigureToFile(str)



global pathToFigures
global videoId
global saveFile


    
if ~exist('str', 'var') && fprintf('\nNo str provided, cant save\n') ...
    || ...
   ~exist('pathToFigures', 'var') && fprintf('\nNo path for figures configures\n') 
    ret = false;    
    return
end

if ~exist('videoId', 'var')
    videoId = '';
end

if exist('saveFile', 'var') && saveFile == true
    if strcmp(str, 'init');
        delete([pathToFigures 'datos-' videoId '.txt'])
        return
    end
   fid = fopen([pathToFigures 'datos-' videoId '.txt'],'a+t');
    fprintf(fid,str);
    fprintf(fid,'\n');
    fclose(fid);
end
