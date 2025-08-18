function pnew = unemax(p,n)

clear pnew

pnew = zeros(size(p,1),size(p,2));

verbose = false;
% unificando los maximos en una sola linea

comienzo = 2;
for i=1:size(p,2)
    pnew(comienzo-1,i) = p(comienzo-1,i);
%     pnew(2,i) = p(2,i);    
end


% clean = clean_row(pnew(1,:));
% pnew(1,:) = clean;

offset_pnew = 10;
fprintf('t%4d p :', 1);
print_row(pnew)

maximaDistancia = n;

% pnew = zeros(100,100);
for t=comienzo:size(pnew,1)
    for m=1:size(pnew,2)      
%         if p(t,m) == 0 || isnan(p(t,m))
%             continue
%         end 
%         for i=2:size(pnew,2)
%             pnew(t-1,i) = p(t,i);
%         end
        for nmax=1:size(p,2)
%             fprintf('t:%d m:%d nmax:%d p(t,m) - pnew(t-1,nmax) [%d - %d] <= %d \n ',t, m, nmax, p(t,m), pnew(t-1,nmax), maximaDistancia);
            if (abs(p(t,m) - pnew(t-1,nmax)) <= maximaDistancia)
%                 fprintf('%d - %d <= %d \n',p(t,nmax), pnew(t-1,pnew_max), maximaDistancia);            
                pnew(t,nmax) = p(t,m);
                salte  = true;
                
            end
        end
%         if (salte)
%             salte = false;
%             break
%         end
    end
%     fprintf('t-1%4d p :',t-1);
%     print_row(p(t,:));    
%     fprintf('t  %4d p :',t);
%     print_row(p(t,:));    
%     fprintf('t  %4d pn:',t);
%     print_row(pnew(t,:));

end

figure
plot(pnew,'.')

function print_row(arr)
for i=1:size(arr,2)
    fprintf('%3.0f ', arr(i));
end
fprintf('\n', arr(i));

function ret = clean_row(ret)
for i=1:size(ret,2)
    if ret(i) == 0
        ret(i) = NaN;
    end
end


