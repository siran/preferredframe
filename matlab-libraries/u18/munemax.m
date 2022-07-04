clc
tipo = ['.' 'o']
ntipo=1;
for n=2:3
    pnew = unemax(p,3);
    hold on;
    plot(pnew,tipo(n))
    ntipo = ntipo+1;
end
