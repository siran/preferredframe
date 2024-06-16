function writeSummary(varargin)
% write a summary file for session

summary_path = 'D:\Users\an\experimento-usb-interferometro\analysis-summaries\';

% % % % % % % % % % % % % % % % % % % % % % % % % % 
stars = {'HIP54589', 'Sun', 'Moon', 'Jupiter', 'Venus', 'Mars'};
colors = { ...
    [0.0, 0.0, 1.0],    ... % Blue for HIP54589
    [1.0, 1.0, 0.0],    ... % Yellow for Sun
    [0.0, 0.0, 0.0],    ... % Black for Moon
    [0.6, 0.3, 0.0],    ... % Brown for Jupiter
    [0.7, 0.7, 0.7],    ... % Light Gray for Venus
    [1.0, 0.0, 0.0]     ... % Red for Mars
};
masses = {nan, 1.98885E30, 7.3477E22, 1.898E27, 4.867E24, 6.39E23};
G = 0.000000000066743;
% % % % % % % % % % % % % % % % % % % % % % % % % % %

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
    summary(i).datetime = datestr(timeRange(1), 'YYYY-mm-dd HH:MM');
    summary(i).time = datestr(timeRange(1), 'HH:MM');
    [maxv, imaxv] = max(YY(j,:));
    [minv, iminv] = min(YY(j,:));
    summary(i).amplitude =  maxv - minv;
    summary(i).max = maxv;
    summary(i).min = minv;
    summary(i).fringe_separation_session = fringe_separation;    
    if YYstddev ~= 0
        summary(i).amplitude_error = abs(YYstddev(imaxv)) + abs(YYstddev(iminv));
    end

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

    if exist('timeAltitude', 'var') && ~isempty(timeAltitude)
        % Loop though all stellar object       
        for starname_i = 1:length(stars)
            fieldname = ['altitude_' stars{starname_i}];
            disp(['Calculating altitude for: ' fieldname]);
            disp(['timeAltitude size: ' num2str(size(timeAltitude))]);
            disp(['timeAltitude(:,1,starname_i) size: ' num2str(size(timeAltitude(:,1,starname_i)))]);
            summary(i).(fieldname) = pchip(timeAltitude(:,1,starname_i), timeAltitude(:,2,starname_i), XX(j));
            fieldname = ['azimuth_' stars{starname_i}];
            disp(['Calculating azimuth for: ' fieldname]);
            summary(i).(fieldname) = pchip(timeAltitude(:,1,starname_i), timeAltitude(:,3,starname_i), XX(j));
      
            if size(timeAltitude,2) > 3
                fieldname = ['distance_km_' stars{starname_i}];
                distance_km = pchip(timeAltitude(:,1,starname_i), timeAltitude(:,4,starname_i), XX(j));
                summary(i).(fieldname) = distance_km;

                fieldname = ['p_inv_' stars{starname_i}];
                mass_i = masses{starname_i};
                e_density_inv = 1/(G*mass_i^2/(8*pi*(distance_km*1E3)^4));
                summary(i).(fieldname) = e_density_inv;

            end
        end
    end    
end

    
writetable(struct2table(summary), filename);

% return