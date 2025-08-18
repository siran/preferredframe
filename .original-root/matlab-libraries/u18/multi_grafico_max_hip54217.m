startDate = datenum(files_images(1).date)+1;
endDate = datenum(files_images(size(p,1)).date);
step=7;
for tiempo=floor(startDate):step:floor(endDate)

    figure
    plot(x_timestamp, p,'.',...
        'color','black',...
        'markersize', 5 ...
    )
    grid on

    set(gca,'Position', [0.05 0.05 0.93 0.88])
    set(gca,'XLim', [tiempo tiempo+1])
    set(gca,'YLim', [50 250])
    set(gca,'XTick',tiempo:6/24:tiempo+1)

    set(gca,'XMinorTick','on')

    datetick('x','dd_HH:MM','keepticks')




    t = title(['Movement of Interference Maxima: from ' files_images(1).date ' to ' files_images(size(p,1)).date],'FontSize', 16);
    titleposition = get(t,'Position')

    xlabel('Time (HH:MM)');
    ylabel('Position of Maxima (pixels)');

    % dibujo las lineas de HIP54255
    fechaEste = datenum('2010-11-18 1:37'); %aqui esta en el oeste
    fechaCenitP = datenum('2010-11-18 7:12'); %aqui esta en el oeste
    fechaOeste = datenum('2010-11-18 12:52'); %aqui esta en el oeste
    fechaCenitN = datenum('2010-11-18 19:15'); %aqui esta en el oeste


    diaSideral = 23.9344696/24; % dias

    hold on
    xo = fechaOeste:diaSideral:endDate+1;
    xcn = fechaCenitN:diaSideral:endDate+1;
    xe = fechaEste:diaSideral:endDate+1;
    xcp = fechaCenitP:diaSideral:endDate+1;

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
        plot([punto punto], [1 maxp], '-.', 'linewidth', linewidth, 'color',color)
        text(punto, pos, 'EAST', ...  
            'color',color,...
            'fontsize',fontsize,...
            'backgroundcolor', backgroundcolor,...
            'fontweight', fontweight,...
            'rotation',rotation)    

        punto = xcp(s);
        plot([punto punto], [1 maxp], '-.', 'linewidth', linewidth, 'color',color)
        text(punto, pos, 'CENIT+', ...      
            'color',color,...
            'fontsize',fontsize,...
            'backgroundcolor', backgroundcolor,...
            'fontweight', fontweight,...
            'rotation',rotation)    

        punto = xo(s);    
        plot([punto punto], [1 maxp], '-.', 'linewidth', linewidth, 'color',color)
        text(punto, pos, 'WEST', ...
            'color',color,...
            'fontsize',fontsize,...
            'backgroundcolor', backgroundcolor,...
            'fontweight', fontweight,...
            'rotation',rotation)    

        punto = xcn(s);
        plot([punto punto], [1 maxp], '-.', 'linewidth', linewidth, 'color',color)
        text(punto, pos, 'CENIT-', ...
            'color',color,...
            'fontsize',fontsize,...
            'backgroundcolor', backgroundcolor,...
            'fontweight', fontweight,...
            'rotation',rotation)        
        catch
            fprintf('fin')
        end
    end
    hold off    
end
