
clear t
syms t 

rad = pi/180;
theta = 0*rad;
Lx = 0;
Ly = 1;
v=350000;
c=3e8;

i=0;

for ang=0:10:90
    i = i+1
    theta = ang*rad;
    eq = ...
    sqrt( ...
        (...
            (1-v*cos(theta))^(-1)*(Lx + v*cos(theta)*t) ...
        )^2 + ( ...
            (1-v*sin(theta))^(-1)*(Ly + v*sin(theta)*t) ...  
        )^2 ...    
    ) - c*t;
    t1 = solve(eq);
    
    Lx = .5;
    Ly = 0;    
end

plot(res,'o')

