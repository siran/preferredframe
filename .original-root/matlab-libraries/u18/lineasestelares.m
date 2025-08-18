% dibujo las lineas de HIP54255
fechaEste = datenum('2010-11-18 1:37'); %aqui esta en el oeste
fechaCenitP = datenum('2010-11-18 7:12'); %aqui esta en el oeste
fechaOeste = datenum('2010-11-18 12:52'); %aqui esta en el oeste
fechaCenitN = datenum('2010-11-18 19:15'); %aqui esta en el oeste


diaSideral = 23.9344696/24; % dias

hold on
xo = fechaOeste:diaSideral:endDate;
xcn = fechaCenitN:diaSideral:endDate;
xe = fechaEste:diaSideral:endDate;
xcp = fechaCenitP:diaSideral:endDate;

% p = p + abs(min(p(:)));
maxp = max(max(p));
fontsize = 12;
color = 'magenta';
linewidth = 1;
pos = max(max(p))*.97;
backgroundcolor = 'white';
fontweight='bold';
rotation=90;
for s=1:size(xe,2)

    try
    punto = xe(s);
    if punto > startDate && punto < endDate    
        plot([punto punto], [1 maxp], '-.', 'linewidth', linewidth, 'color',color)
        text(punto, pos, 'EAST', ...  
            'color',color,...
            'fontsize',fontsize,...
            'backgroundcolor', backgroundcolor,...
            'fontweight', fontweight,...
            'rotation',rotation)    
    end
    
    punto = xcp(s);
    if punto > startDate && punto < endDate    
        plot([punto punto], [1 maxp], '-.', 'linewidth', linewidth, 'color',color)
        text(punto, pos, 'CENIT+', ...      
            'color',color,...
            'fontsize',fontsize,...
            'backgroundcolor', backgroundcolor,...
            'fontweight', fontweight,...
            'rotation',rotation)
    end
    
    punto = xo(s);    
    if punto > startDate && punto < endDate    
        plot([punto punto], [1 maxp], '-.', 'linewidth', linewidth, 'color',color)
        text(punto, pos, 'WEST', ...
            'color',color,...
            'fontsize',fontsize,...
            'backgroundcolor', backgroundcolor,...
            'fontweight', fontweight,...
            'rotation',rotation)    
    end
    
    punto = xcn(s);
    if punto > startDate && punto < endDate    
        plot([punto punto], [1 maxp], '-.', 'linewidth', linewidth, 'color',color)
        text(punto, pos, 'CENIT-', ...
            'color',color,...
            'fontsize',fontsize,...
            'backgroundcolor', backgroundcolor,...
            'fontweight', fontweight,...
            'rotation',rotation)        
    end
    catch
        fprintf('fin')
    end
end


% % Se dibujan lineas correspondiente a las horas del día

% fechaEste = datenum('2010-11-18 6:00'); %aqui esta en el oeste
% fechaCenitP = datenum('2010-11-18 12:00'); %aqui esta en el oeste
% fechaOeste = datenum('2010-11-18 18:00'); %aqui esta en el oeste
% fechaCenitN = datenum('2010-11-18 00:00'); %aqui esta en el oeste
% 
% 
% diaSideral = 1; % dias
% 
% hold on
% xo = fechaOeste:diaSideral:endDate+1;
% xcn = fechaCenitN:diaSideral:endDate+1;
% xe = fechaEste:diaSideral:endDate+1;
% xcp = fechaCenitP:diaSideral:endDate+1;
% 
% % p = p + abs(min(p(:)));
% maxp = max(max(p));
% fontsize = 12;
% color = 'black';
% linewidth = 1;
% pos = max(max(p))*.97;
% backgroundcolor = 'white';
% fontweight='bold';
% rotation=90;
% for s=1:size(xe,2)
%     if xe(s) < (startDate) || xe(s) > (endDate)
%         continue
%     end    
%     try
%     punto = xe(s);
%     plot([punto punto], [1 maxp], '-.', 'linewidth', linewidth, 'color',color)
%     text(punto, pos, '6.00h', ...  
%         'color',color,...
%         'fontsize',fontsize,...
%         'backgroundcolor', backgroundcolor,...
%         'fontweight', fontweight,...
%         'rotation',rotation)    
%     
%     punto = xcp(s);
%     plot([punto punto], [1 maxp], '-.', 'linewidth', linewidth, 'color',color)
%     text(punto, pos, '12.00h', ...      
%         'color',color,...
%         'fontsize',fontsize,...
%         'backgroundcolor', backgroundcolor,...
%         'fontweight', fontweight,...
%         'rotation',rotation)    
%     
%     punto = xo(s);    
%     plot([punto punto], [1 maxp], '-.', 'linewidth', linewidth, 'color',color)
%     text(punto, pos, '18.00h', ...
%         'color',color,...
%         'fontsize',fontsize,...
%         'backgroundcolor', backgroundcolor,...
%         'fontweight', fontweight,...
%         'rotation',rotation)    
%     
%     punto = xcn(s);
%     plot([punto punto], [1 maxp], '-.', 'linewidth', linewidth, 'color',color)
%     text(punto, pos, '00.00h', ...
%         'color',color,...
%         'fontsize',fontsize,...
%         'backgroundcolor', backgroundcolor,...
%         'fontweight', fontweight,...
%         'rotation',rotation)        
%     catch
%         fprintf('fin')
%     end
% end