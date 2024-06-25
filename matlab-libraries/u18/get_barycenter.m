function coords = get_barycenter(varargin)
% calculates barycenter position of specified stars with mass
% RETURNS array coords = [altitude, lontitude] of barycenter as seen from
% `observer_location`
% varargin: options
%   datetimestr: datetime string REQUIRED in UTC as string 2020-02-20T00:00:00
%   observer_location: defaults to "Caracas, Venezuela" (not implemented)
%   timeAltitude: timeAltitude array with positions of objects
%   star_info: star_info array with arrays of stars and masses (see 

datetimestr = nan;
timeAltitude = nan;
star_info = nan;

nVarargs = length(varargin);
for k = 1:2:nVarargs
    if strcmp(varargin{k}, 'datetimestr')
        datetimestr = varargin{k+1};
    end
    if strcmp(varargin{k}, 'timeAltitude')
        timeAltitude = varargin{k+1};
    end    
    if strcmp(varargin{k}, 'star_info')
        star_info = varargin{k+1};
    end        
end
if isnan(datetimestr)
    error('please specify datetimestr')
end
if isnan(timeAltitude)
    error('please specify timeAltitude')
end
if isnan(star_info)
    error('please specify star_info')
end
coords = [0,0];
end