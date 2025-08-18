function [XXm, YYm, YYstddev] = plotInGroups(XX, YY, varargin)
% plotInGroups(Y, rotsgroup, options) plots mean(Y) vs 1:length(Y), in groups of rotsgroup
%  Options:
%     groupsize size of grouping
%     groupstep jump this number of elements before next grouping
%     saveFigures = true : whether to save the figure;
%     errorBars = true: whether to plot error bars;
%     errorx = 2: default x errorbar width;
%     hampelParams = nan: if filter the values with hampel, [stddev numpoints]
%       stddev: points exceeding this standard deviation are filtered
%       numpoints: points to consider for the standard deviation
%            (not implemented, defaults to all points)

global videoId
global processing_session

% limits = [-0.4 0.4];
% limitsAbs = [-40 40];
limits = [-1 1];
limitsAbs = [-100 100];
warning('off', 'MATLAB:colon:nonIntegerIndex')

% default values
rotsgroup = 6;
rotsstep =  3;
errorBars = true;
errorx = 2;
hampelParams = nan;
plotGroups = false;
normalizeBy = nan;
showLegend = false;
saveTxtData = false;

saveFigures = false;

nVarargs = length(varargin);
for k = 1:2:nVarargs
    if strcmp(varargin{k}, 'groupsize')
        rotsgroup = varargin{k+1};
    elseif strcmp(varargin{k}, 'groupstep')
        rotsstep =  varargin{k+1};
    elseif strcmp(varargin{k}, 'errorBars')
        errorBars = varargin{k+1};
    elseif strcmp(varargin{k}, 'saveFigures')
        saveFigures = varargin{k+1};        
    elseif strcmp(varargin{k}, 'errorx')
        errorx = varargin{k+1};       
    elseif strcmp(varargin{k}, 'hampelParams')
        hampelParams = varargin{k+1};       
    elseif strcmp(varargin{k}, 'plotGroups')
        plotGroups = varargin{k+1};
    elseif strcmp(varargin{k}, 'normalizeBy')
        normalizeBy = varargin{k+1};
    elseif strcmp(varargin{k}, 'showLegend')
        showLegend = varargin{k+1};
    elseif strcmp(varargin{k}, 'timeAltitude')
        timeAltitude =  varargin{k+1};            
    elseif strcmp(varargin{k}, 'timeRange')
        timeRange =  varargin{k+1};         
    elseif strcmp(varargin{k}, 'xts')
        xts =  varargin{k+1};     
    elseif strcmp(varargin{k}, 'saveTxtData')
        saveTxtData =  varargin{k+1};     
    end
end

% plotGroups = false;

% saveFigures = false;


i = 0;
for r=1:rotsstep:size(YY,1)
    i = i + 1;
    if (r+rotsstep) > size(YY,1)
        rLimit(i) = size(YY,1);
        r = max(1, rLimit(i) - rotsstep +1);
    else
        rLimit(i) = min(size(YY,1), r+rotsgroup-1);    
    end
    YYlim(i, :) = [r rLimit(i)];
    
    y{i} = YY(r:rLimit(i),:);
    x{i} = XX(r:rLimit(i),:);

    hampeled = false;
    hampelStr = [];
    hampelFile = [];
    if ~isempty(hampelParams) && ~isnan(hampelParams) && size(y{i},1) > 1
        hampeled = true;
        y{i} = hampel(y{i}, size(y{i},1), hampelParams(1));
        hampelStr =  [' w/o outliers' ' (' num2str(hampelParams(1)) ' stddev)'];
        hampelFile = ['-clean'];
    end    
    
    YYm(i,:) = mean(y{i}, 1, "omitnan");
    XXm(i) = mean(mean(x{i}, 2, "omitnan"), "omitnan");
    YYstddev(i,:) = std(y{i}, 0, 1, "omitmissing")./sqrt(sum(~isnan(y{i})));
end

normalizedByStr = [];
normalizedByFile = [];
if ~isnan(normalizeBy)
    YYm = YYm/normalizeBy;
    YYstddev = YYstddev/normalizeBy;
    normalizedByStr = [' normalized by ' num2str(normalizeBy) ' [px/fringe]'];
    normalizedByFile = ['-normalized'];
else
    normalizedByStr = [' (px)'];
end

numrotaciones = size(YYm,1);
numRotPromediadas = size(y{1},1);

if plotGroups
    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    % plot groups
    i = 0;
    figure;
    hold on
    clear legends
    
    colorMap = hot(size(YYm,1)*2);
    set(groot,'defaultAxesColorOrder', colorMap )
    for i=1:size(YYm,1)
        if errorBars % && numrotaciones > 1
            fprintf('plot %d/%d, i:%d s:%d\n', i, numrotaciones, i,rLimit(i))
%             errorbarxy( ...
%                 0:size(YYm,2)-1, ...
%                 YYm(i,:), ...
%                 ones(1,360)*errorx, ...
%                 YYstddev(i,:), ...
%                 {'k.-', 'c', 'm'})
            errorbar(...
                0:size(YYm,2)-1, ...
                YYm(i,:), ...
                YYstddev(i,:) ...
            )
        else
            plot(1:size(YYm,2), YYm, '.-', 'markersize', 5)
        end
        
        if ~isempty(processing_session.remove_drift) && processing_session.remove_drift
            ylim(limits)
        end        

        legends{i} = [ ...
            num2str(i) ': rot: ' num2str(YYlim(i,1)) '->' num2str(YYlim(i,2)) ......
            ', hora: ' datestr(XX(i,1), 'HH:MM') '->' ...
            datestr(XX(rLimit(i), size(XX,2)), 'HH:MM') ...
        ];          %#ok<AGROW>
    end
    reset(groot)
    
    totalGroups = size(YYm, 1);
    

    title( ...
        { ...
            ['Fringe displacement for rotations'], ...
            ['Mean of ' int2str(numRotPromediadas) ' rotations' normalizedByStr hampelStr ' every ' num2str(rotsstep) 'rotations'], ...
            ['Start: ' datestr(timeRange(1)) ' - End: ' datestr(timeRange(end))], ...
            ['(session name: ' videoId ')'], ...
        }, ...
        'FontSize', 16, ...
        'Interpreter', 'none' ...
    )                
    
    xlim([0 360])
    
    if ~isempty(processing_session.remove_drift) && processing_session.remove_drift
        ylim(limits)
    end            
    
    xlabel('Angle (º)')
    ylabel(['Maximum displacement ' normalizedByStr])
    
    if ~isempty(processing_session.remove_drift) && processing_session.remove_drift
        if ~isnan(normalizeBy)
            ylim(limits)
        else
            ylim(limitsAbs)
        end
    end        

    if rLimit(i) == size(YY,1)
%         legend(legends, 'Location', 'northeastoutside')
    end
    plotheightstar
    figname = ['mean-group-r' num2str(rotsgroup) 's' num2str(rotsstep) normalizedByFile hampelFile];

    saveData = false;
    if saveFigures 
        if rotsgroup == 10 && rotsstep == 10
            saveData = true;
        end
        usb2018_saveFigureToFile(figname, 'timeRange', timeRange, 'saveTxtData', saveTxtData)
    end    
end

% % %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% % % plot absolute displacement vs time
% % if size(YYm,1) > 1
% %     figure
% %     % [Y,I] = max(X,[],DIM) operates along the dimension DIM.
% %     [Ymax,Imax] = max(YYm, [], 2);
% %     [Ymin,Imin] = min(YYm, [], 2);
% %     Y = Ymax-Ymin;
% %     plot(XXm(1:size(Y,1)), Y, 'o-')
% %     xlim([XXm(1) XXm(size(Y,1))])
% %     ylim([0 1.1])
% %     xlabel('Timestamp of Average of (Average timestap of rotation) of group of rotations (DD/MM HH:MM)')
% %     ylabel(['Absolute displacement' normalizedByStr hampelStr ])
% %     title({ ...
% %         ['Absolute displacement of maxima' normalizedByStr hampelStr] ...
% %         , ['Start: ' datestr(xts(1)) ' - End: ' datestr(xts(end))] ...
% %         , ['Mean of ' int2str(numRotPromediadas) ' rotations' normalizedByStr hampelStr ' every ' num2str(rotsstep) 'rotations'] ...        
% %         , ['(r' num2str(rotsgroup) 's' num2str(rotsstep) ')'] ...
% %     })
% % %     legend({ ...
% % %         'Each rotation has an average timestamp' ...
% % %         ,'each group of rotations has an average timestamp' ...
% % %     })
% %     datetick('x','dd/mm HH:MM','keepticks')
% %     ax = gca;
% %     ax.XTickLabelRotation = 90;
% %     plotheightstar
% %     if saveFigures 
% %         usb2018_saveFigureToFile(['abs-displacement-r' num2str(rotsgroup) 's' num2str(rotsstep) normalizedByFile hampelFile])
% %     end
% % end

% YL = ylim;
% i=0;
% for r=1:rotsstep:size(YY,1)
%     i = i + 1;
%     text(size(XX,2)/5, i*5 + YL(1), num2str(i))
% end

