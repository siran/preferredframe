function ret = saveFigureToFile(figure_name)

global pathToFigures
global videoId
global saveFile
global frameToTime
    
if ~exist('figure_name', 'var') && fprintf('\nNo name for figure provided, cant save\n') ...
    || ...
   ~exist('pathToFigures', 'var') && fprintf('\nNo path for figures configures\n') 
    ret = false;    
    return
end

if ~exist('videoId', 'var')
    videoId = '';
end

if exist('saveFile', 'var') & saveFile == true
    videodatestr = datestr(frameToTime(1,2), 'yyyymmdd_hhss');
    nowdate = datestr(now, 'yyyymmdd_hhss');
    set(gcf,'units','normalized','outerposition',[0 0 1 1]);
    saveas(gcf,[pathToFigures videodatestr '-' videoId '-' figure_name '-' nowdate '.jpg']);
%     close;
end
