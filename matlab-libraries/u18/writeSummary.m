function writeSummary(varargin)
% write a summary file for session

summary_path = 'D:\Users\an\experimento-usb-interferometro\analysis-summaries\';

nVarargs = length(varargin);
for k = 1:2:nVarargs
    if strcmp(varargin{k}, 'sessionId')
        sessionId = varargin{k+1};
    elseif strcmp(varargin{k}, 'XX')
        XX = varargin{k+1};        
    elseif strcmp(varargin{k}, 'YY')
        YY = varargin{k+1};        
    elseif strcmp(varargin{k}, 'YYstddev')
        YYstddev = varargin{k+1};        
    elseif strcmp(varargin{k}, 'rotations')
        rotations = varargin{k+1};        
    elseif strcmp(varargin{k}, 'separation')
        separation = varargin{k+1};        
    elseif strcmp(varargin{k}, 'fringe_separation')
        fringe_separation =  varargin{k+1};        
    elseif strcmp(varargin{k}, 'timeRange')
        timeRange =  varargin{k+1};                 
    elseif strcmp(varargin{k}, 'timeAltitude')
        timeAltitude =  varargin{k+1};            
    elseif strcmp(varargin{k}, 'xts')
        xts =  varargin{k+1};       
    elseif strcmp(varargin{k}, 'filename')
        filename =  varargin{k+1};          
   
    end
end

filename = [summary_path filename '.csv'];

grouping_type = ['r' num2str(rotations) 's' num2str(separation)];

if exist(filename, 'file')
    table = readtable(filename);
    summary = table2struct(table);

    for i=length(summary):-1:1
        % old values
        if strcmp(summary(i).sessionId, sessionId) && strcmp(summary(i).grouping_type, grouping_type)
            summary(i) = [];
        end
    end    
end

summary_length = 0;
if exist('summary', 'var')
    summary_length = length(summary);
end

if size(YY) > 1
    stop=1;
end


for j=1:size(YY,1)
    i = j + summary_length;
    summary(i).sessionId = sessionId;
    summary(i).grouping_type = grouping_type;
    summary(i).rotations = rotations;
    summary(i).separation = separation;
    summary(i).group = j;
%     summary(i).datetime = datestr(XX(j), 'YYYY-mm-dd HH:MM');
%     summary(i).time = datestr(XX(j), 'HH:MM');
    summary(i).datetime = datestr(timeRange(1), 'YYYY-mm-dd HH:MM');
    summary(i).time = datestr(timeRange(1), 'HH:MM');
    [maxv, imaxv] = max(YY(j,:));
    [minv, iminv] = min(YY(j,:));
    summary(i).amplitude =  maxv - minv;
    summary(i).max = maxv;
    summary(i).min = minv;

    if exist('timeAltitude', 'var') && ~isempty(timeAltitude)
        % Loop though all stellar object
        stars = {'HIP54589', 'Sun', 'Moon'};
        for starname_i = 1:length(stars)
            fieldname = ['altitude_' stars{starname_i}];
            summary(i).(fieldname) = pchip(timeAltitude(:,1,starname_i), timeAltitude(:,2,starname_i), XX(j));
            if size(timeAltitude,2) > 3
                fieldname = ['distance_km_to_' stars{starname_i}];
                summary(i).(fieldname) = pchip(timeAltitude(:,1,starname_i), timeAltitude(:,4,starname_i), XX(j));                
            end
            % timeAltitude(t,1,starname_i)=datenum(datetime(rawData{r,1},'InputFormat','yyyy-MM-dd''T''HH:mm:ss'))-1/24*4;
            % timeAltitude(t,2,starname_i)=rawData{r,5}; % equatorial altitude
            % timeAltitude(t,3,starname_i)=rawData{r,4}; % equatorial azimuth
            % 
            % star_altitude = pchip(timeAltitude(:,1), timeAltitude(:,2), XX(j));
        end
    end

    summary(i).fringe_separation_session = fringe_separation;    
    if YYstddev ~= 0
        summary(i).amplitude_error = abs(YYstddev(imaxv)) + abs(YYstddev(iminv));
    end
    % summary(i).average_altitude = star_altitude;
    
    if contains(sessionId,'norm')
        summary(i).figure_type = 'normalized';
    elseif contains(sessionId,'inde')
        summary(i).figure_type = 'independientes';
    elseif contains(sessionId,'-no-rotation')
        summary(i).figure_type = 'no-rotation';        
    else 
        summary(i).figure_type = '';
    end
    summary(i).average_position = (maxv + minv)/2;
end
    
writetable(struct2table(summary), filename);

return