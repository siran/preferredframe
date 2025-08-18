% corrigiendo pendiente
% m = -43.053227635975283;
% ptemp = zeros(size(p));
% ptemp = p;
% 
% for t=1:size(p,1)
%     if (mod(t,10)==0) 
%         fprintf('%d ', t);
%     end
%     if (mod(t-1,200)==0) 
%         fprintf('\n');
%     end      
%     p(t, :) = p(t,:) - (x_timestamp(t)- x_timestamp(1))*m;
% end
clear pendiente pendientex pendientey
for i=1:size(puntos,2)
%     puntos(i).Position(1)
    pendiente(2,i) = puntos(i).Position(1);
    pendiente(1,i) = puntos(i).DataIndex(1);
    
end
fprintf('fin')