% simulacion formulas 2021-01-16

clc

L0 = 0.58; % m
v = 300000; % m/s
c = 300000000; % m/s
lambda = 632.8e-9; %m/s
beta = v/c;
n = 1.6;
D_lambda = -9.05E-5;

theta = [0:360];

L_theta = L0*sqrt(1 - (beta*cos(theta).^2));




%%% vidrio
n = 1.6;
V_n = c/n + v*(1 - n^2 - D_lambda)*cos(theta);
tnum = 2*L_theta*v.*cos(theta) + ...
        sqrt( ...
            (2*v.*cos(theta).*L_theta).^2 + ...
            4*L_theta.^2.*( V_n.^2 - v^2*cos(theta).^2) - v*t*sin(theta)/n^2 ...
        );
    
tden = 2*( V_n.^2 - v^2*cos(theta).^2 - v*t.*sin(theta)/n^2);

tg = tnum / tden;

%%% vidrio
n = 1;
V_n = c/n + v*(1 - n^2 - D_lambda)*cos(theta);
tnum = 2*L_theta*v.*cos(theta) + ...
        sqrt( ...
            (2*v.*cos(theta).*L_theta).^2 + ...
            4*L_theta.^2.*( V_n.^2 - v^2*cos(theta).^2) - v*t*sin(theta)/n^2 ...
        );
    
tden = 2*( V_n.^2 - v^2*cos(theta).^2 - v*t.*sin(theta)/n^2);

ta = tnum / tden;

plot(tg-ta)
