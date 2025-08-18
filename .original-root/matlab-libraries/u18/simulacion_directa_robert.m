% simulacion directa ec. robert para t

clc

L0 = 0.58; % m
v = 300000; % m/s
c = 300000000; % m/s
lambda = 632.8e-9; %m/s
beta = v/c;

theta_original = [0:0.01:360];

L_theta = L0*sqrt(1 - (beta*cos(theta_original).^2));

%%%% theta = 0..360
theta = theta_original;

%%% vidrio
n = 1.6;
D_lambda = -9.05E-5;

L = L0*sqrt(1 - (beta*cos(theta).^2));
Vn = c/n + v*(1-1/n^2-D_lambda).*cos(theta);
tg2 = ( ...
        2*v.*L.*cos(theta) + ...
        sqrt(  (2*v*L.*cos(theta)).^2 + 4*L.^2.*(  ...
                                                   Vn.^2 - (v*cos(theta)).^2 - (v/n^2*sin(theta)).^2 ...
                                                ) ...
        ) ...
     ) ./ (Vn.^2 - (v*cos(theta)).^2 - (v/n^2*sin(theta)).^2)*2;
    

%%% aire
%%% vidrio
n = 1;
D_lambda = 0;

L = L0*sqrt(1 - (beta*cos(theta).^2));
Vn = c/n + v*(1-1/n^2-D_lambda).*cos(theta);
ta2 = ( ...
        2*v.*L.*cos(theta) + ...
        sqrt(  (2*v*L.*cos(theta)).^2 + 4*L.^2.*(  ...
                                                   Vn.^2 - (v*cos(theta)).^2 - (v/n^2*sin(theta)).^2 ...
                                                ) ...
        ) ...
     ) ./ (Vn.^2 - (v*cos(theta)).^2 - (v/n^2*sin(theta)).^2)*2;


%%%% theta = 0
theta = theta_original*0;

%%% vidrio
n = 1.6;
D_lambda = -9.05E-5;

L = L0*sqrt(1 - (beta*cos(theta).^2));
Vn = c/n + v*(1-1/n^2-D_lambda).*cos(theta);
tg1 = ( ...
        2*v.*L.*cos(theta) + ...
        sqrt(  (2*v*L.*cos(theta)).^2 + 4*L.^2.*(  ...
                                                   Vn.^2 - (v*cos(theta)).^2 - (v/n^2*sin(theta)).^2 ...
                                                ) ...
        ) ...
     ) ./ (Vn.^2 - (v*cos(theta)).^2 - (v/n^2*sin(theta)).^2)*2;

%%% aire
%%% vidrio
n = 1;
D_lambda = 0;

L = L0*sqrt(1 - (beta*cos(theta).^2));
Vn = c/n + v*(1-1/n^2-D_lambda).*cos(theta);
ta1 = ( ...
        2*v.*L.*cos(theta) + ...
        sqrt(  (2*v*L.*cos(theta)).^2 + 4*L.^2.*(  ...
                                                   Vn.^2 - (v*cos(theta)).^2 - (v/n^2*sin(theta)).^2 ...
                                                ) ...
        ) ...
     ) ./ (Vn.^2 - (v*cos(theta)).^2 - (v/n^2*sin(theta)).^2)*2;


N = (c/lambda)*((tg2-ta2)-(tg1-ta1));

plot(N)
% xlim([0 50])