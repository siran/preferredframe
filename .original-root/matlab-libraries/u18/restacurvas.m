padj = p_adjusted;

c=[3;4;5;6];
colors={'red','blue', 'green', 'black'};
% figure
% title('lineas normalizadas');
% for n=1:size(c)
%     i = c(n);
%     padjs(i,:) = smooth(padj(:,i), 30);
%     mins(i) = min(padjs(i,:));
%     scales(i) = max(padjs(i,:) - mins(i));
%     hold on
%     plot(xts, (padjs(i,:)-mins(i))/scales(i), 'color', colors{n})
% end
% 
% figure
% title('lineas indivuduales');
% for n=1:size(c)
%     i = c(n);
%     hold on
%     plot(xts, padjs(i,:), 'color', colors{n})
% end

% hold off
% figure
% title('diferencias entre lineas con la negra --Y lineas normalizadas--');
% for n=1:size(c)-1
%     i = c(n);
%     hold on
% %     plot(xts,  (padjs(6,:) - padjs(i,:) - min(padjs(6,:) - padjs(i,:)))/max(padjs(6,:) - padjs(i,:)), 'color', colors{n})
% %     plot(xts, (padjs(i,:))/scales(i), 'color', colors{n})
%     plot(xts, padjs(6,:)- padjs(i,:), 'color', colors{n})
% %     plot(xts, (padjs(6,:)- padjs(i,:)-max(padjs(6,:)- padjs(i,:))), 'color', colors{n})
% end
% plot(xts, padjs(6,:), 'color', 'red')
hold on
% plot(xts, padjs(6,:)- padjs(3,:)-min(padjs(3,:)), 'color', 'green')
hold on
plot(xts, padjs(6,:)+(padjs(6,:)- padjs(3,:)-min(padjs(3,:))), 'color', 'blue')



