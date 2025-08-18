function draw_rotations(x, y, ax)

if length(x)
    for r=1:length(x)
        H = line(ax, [x(r) x(r)], [y(1) y(2)], ...
            'Marker','.','LineStyle','--', 'Color', [1 0 0]);
    %     line([xts(rotation0_locs(r)) xts(rotation0_locs(r))], [ax.YLim(1) ax.YLim(2)], ...
    %         'Marker','.','LineStyle','--', 'Color', [1 0 0])
    end
    % legend(H, 'Rotation indicator')
    
% else
    % fprintf('No rotations found, not drawing rotations.\n')
end
% fprintf('Drawing %d vertical indicators of rotationrotations.\n', length(x))