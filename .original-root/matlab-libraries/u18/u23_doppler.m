% doppler analysis

path_workspaces = 'D:\Users\an\experimento-usb-interferometro\u18_workspaces';
workpace_name = 'wn200321_0600';

if ~exist('loaded_workspace','var') || ~loaded_workspace
    workspace_files = dir([path_workspaces '\' workpace_name '*']);
    for i = 1:length(workspace_files)
        fname = workspace_files(i).name;
        load([path_workspaces '\' fname]);
        fprintf('Workspace loaded %s\n', fname)
    end
    processing_session.ajustar = true;
    ajustarDefault = true;
    
    u18_plots

    errorBars = processing_session.error_bars;
    a=1;
       
    rotsgroup = 10;
    rotsstep = 10;
    [XXm, YYm, YYstddev] = plotInGroups(XX, YY ...
        ,'groupsize', rotsgroup ...
        ,'groupstep', rotsstep ...
        ,'saveFigures', true ...
        ,'errorBars', errorBars ...
        ,'plotGroups', true ...
        ,'hampelParams', nan ...
        ,'normalizeBy', separacionFranjas ...
        ,'xts', xts ...
        ,'timeRange', [x_start x_end] ...
        ,'timeAltitude', timeAltitude ...       
        ,'saveTxtData', saveTxtData ...
    );    


    loaded_workspace = true;
end

f = 632E-9;
c = 3e8;

x= 1:360;
y = YYm*f;
% v=30;

% dop = @(x) c./(c-v*cos((x+phi)*pi/180));
% g1 = fittype( @(a,v,x)c./(c-v*cos((a*x)*pi/180)) )

% ft = fittype( @(phi, v, x) c./(c-v*cos((x+phi)*pi/180)), ...
    % 'problem', 'v' )

ft = fittype('((1-v/c*sin(x+phi)))')

% myfittype = fittype("k*c./(c-v*cos(x + phi*pi/180))-k",...
%     dependent="y",independent="x",...
%     coefficients=["k","c","v","phi"])

myfit = fit(x',y',ft,'StartPoint', [3e8, 0, 4999999845000])

plot(myfit,x,y)

s=1;

