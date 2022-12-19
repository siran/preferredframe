function ret = saveFigureToFile(figure_name, varargin)
persistent numfig

if isempty(numfig)
    numfig = 1;
else
    numfig = numfig+1;
end

% close(gcf)
% return

warning('off', 'MATLAB:colon:logicalInput')

global pathToFigures
global videoId
global saveFile
global frameToTime
global xts
global textPosition
global timeAltitude
global package_name
global analysis_name

% pathToFigures = 'D:\Users\an\experimento-usb-interferometro\figures\';
% pathToFigures = 'D:\Users\an\Downloads\tmp\basura\';

closeFigure = true;
numFig = true;
useXts = true;
saveTxtData = false;
% closeFigure = false;

nVarargs = length(varargin);
for k = 1:2:nVarargs
    if strcmp(varargin{k}, 'closeFigure')
        closeFigure = varargin{k+1};
    elseif strcmp(varargin{k}, 'numFig')
        numFig = varargin{k+1};     
    elseif strcmp(varargin{k}, 'useXts')
        useXts = varargin{k+1};  
    elseif strcmp(varargin{k}, 'textPosition')
        textPosition = varargin{k+1};  
    elseif strcmp(varargin{k}, 'xts')
        xts = varargin{k+1};  
    elseif strcmp(varargin{k}, 'timeRange')
        timeRange = varargin{k+1};  
    elseif strcmp(varargin{k}, 'saveTxtData')
        saveTxtData = varargin{k+1};          
    end
end

    
if ~exist('figure_name', 'var') && fprintf('\nNo name for figure provided, cant save\n') ...
    || ...
   ~exist('pathToFigures', 'var') && fprintf('\nNo path for figures configures\n') 
    ret = false;    
    return
end

if ~exist('videoId', 'var')
    videoId = '';
end

initial_height = '';
ax = gca;
if ~exist('saveFile', 'var') || (exist('saveFile', 'var') && ~isempty(saveFile) && saveFile == true)
    videodatestr = '';
    if exist('timeRange', 'var') && ~isempty(timeRange)
        date_start = datestr(timeRange(1), 'yyyymmdd_hhMM');
        date_end = datestr(timeRange(end), 'yyyymmdd_hhMM');
        videodatestr = [date_start '-' date_end];
        
        date_start_num = timeRange(1);
    elseif exist('xts') && ~isempty(xts) && useXts == true
        date_start = datestr(ax.XLim(1), 'yyyymmdd_hhMM');
        date_end = datestr(ax.XLim(2), 'yyyymmdd_hhMM');
        videodatestr = [date_start '-' date_end];
        
        date_start_num = ax.XLim(1);
    end
    if exist('timeAltitude', 'var') && ~isempty(timeAltitude)
        if timeAltitude(1,1) < timeAltitude(end,1)
            initial_heights = timeAltitude(timeAltitude(:,1) >= date_start_num,2);
        else
            initial_heights = timeAltitude(timeAltitude(:,1) <= date_start_num,2);           
        end
        if initial_heights
            initial_height = int2str(round(initial_heights(1)/10)*10);
        end
    end
%     nowdate = datestr(now, 'yyyymmdd_hhMM');
    set(gcf,'units','normalized','outerposition',[0 0 1 1]);
    ax = gca;
    if exist('textPosition') && isempty(textPosition)
        textPosition = 'bottom';
        posx = ax.XLim(2);
        posy = ax.YLim(1);
        color = 'red';
    else
        posx = ax.XLim(2);
        posy = ax.YLim(2);
        color = 'red';
    end
    
%     text( ...
%         posx, posy, ...
%         [videoId '-' videodatestr '-' figure_name], ...
%         'color', color, ...
%         'horizontalAlignment','right', ...
%         'fontsize', 14, ...
%         'Interpreter', 'none', ...
%         'verticalalignment', textPosition ...
%     )
    grid on
    

    if ~isempty(analysis_name)
        package_name = analysis_name;
    end
    
%     figurePath = [pathToFigures '\'];
    if package_name
        if ~exist([pathToFigures package_name], 'dir')
            mkdir(pathToFigures, package_name)
        end
        figurePath = [pathToFigures package_name '\'];
    end
    
    if isempty(analysis_name)
        if numFig
            figname = [figurePath videoId '-'  videodatestr '-' num2str(numfig) '-' figure_name '-alt_' initial_height '.jpg'];
        else
            figname = [figurePath videoId '-'  videodatestr '-'                     figure_name '-alt_' initial_height '.jpg'];        
        end
    else
        figname = [figurePath analysis_name '-' figure_name '.jpg'];        
    end

    % testing shorter names
%     if numFig
%         figname = [pathToFigures videodatestr '-' num2str(numfig) '-' figure_name '-alt_' initial_height '.jpg'];
%     else
%         figname = [pathToFigures videodatestr '-' figure_name '-alt_' initial_height '.jpg'];        
%     end    

    saveas(gcf, figname);
    if ~isempty(saveTxtData) && saveTxtData && ~isempty(strfind(figname, 'r10s10-normalized'))
        h = gcf;
        axesObjs = get(h, 'Children');
        dataObjs = get(axesObjs, 'Children');
        xdata = get(dataObjs, 'XData');
        ydata = get(dataObjs, 'YData');
        ldata = get(dataObjs, 'LData');
        udata = get(dataObjs, 'UData');
        
        yyaxis right
        h = gcf;
        axesObjs = get(h, 'Children');
        dataObjs = get(axesObjs, 'Children');
        
        az_line_x = dataObjs(1).XData;
        az_line_y = dataObjs(1).YData;
        
        al_line_x = dataObjs(2).XData;
        al_line_y = dataObjs(2).YData;
        
        datafile = strrep(figname,'.jpg','-data.csv');
        dlmwrite(datafile, [xdata; ydata; ldata; udata]', 'newline', 'pc')        
        
        datafile = strrep(figname,'.jpg','-altitude-data.csv');
        dlmwrite(datafile, [al_line_x; al_line_y]', 'newline', 'pc')
        
        datafile = strrep(figname,'.jpg','-azimuth-data.csv');
        dlmwrite(datafile, [az_line_x; az_line_y]', 'newline', 'pc')
    end
%     saveas(gcf,[pathToFigures videoId '-' videodatestr '-' figure_name '-' nowdate '.jpg']);
    a=1;
    if closeFigure
        close(gcf)
    end
%     close;
    textPosition = '';
end
