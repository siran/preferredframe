% simulacion directa ec. robert para t

clc

L0 = 0.58; % m
v = 300000; % m/s
c = 300000000; % m/s
lambda = 632.8e-9; %m/s
beta = v/c;

theta_original = [0:1:360];


%%%% theta = 0..360
theta = theta_original;

%%% vidrio
n = 1.61;
D_lambda = lambda/n*(-187500)*(v*(1-1/n^2)/(c/n));
thetap = theta - atan(v*sin(theta)/(c*n));
Vn = c/n + cos(thetap)*v*(1-1/n^2-D_lambda);
f = v*sin(theta)/(n^2);

L = L0*sqrt(1 - (beta*cos(theta).^2));

tg2 = ( ...
        2*L*v.*cos(theta) + ...
        sqrt(  (2*L*v.*cos(theta)).^2 + 4*L.^2.* ... 
            ... (
                Vn.^2 - (v*cos(theta)).^2 - f.^2 ...
            ) ...
      ) ./ (2*(Vn.^2 - (v*cos(theta)).^2 - f.^2));
    

%%% aire
%%% vidrio
n = 1;
D_lambda = lambda/n*(-187500)*(v*(1-1/n^2)/(c/n));
thetap = theta - atan(v*sin(theta)/(c*n));
Vn = c/n + cos(thetap)*v*(1-1/n^2-D_lambda);
f = v*sin(theta)/(n^2);

L = L0*sqrt(1 - (beta*cos(theta).^2));

ta2 = ( ...
        2*L*v.*cos(theta) + ...
        sqrt(  (2*L*v.*cos(theta)).^2 + 4*L.^2.* ... 
            ... (
                Vn.^2 - (v*cos(theta)).^2 - f.^2 ...
            ) ...
      ) ./ (2*(Vn.^2 - (v*cos(theta)).^2 - f.^2));


%%%% theta = 0
theta = theta_original.*0;

%%% vidrio
n = 1.6;
D_lambda = lambda/n*(-187500)*(v*(1-1/n^2)/(c/n));
thetap = theta - atan(v*sin(theta)/(c*n));
Vn = c/n + cos(thetap)*v*(1-1/n^2-D_lambda);
f = v*sin(theta)/(n^2);

L = L0*sqrt(1 - (beta*cos(theta).^2));

tg1 = ( ...
        2*L*v.*cos(theta) + ...
        sqrt(  (2*L*v.*cos(theta)).^2 + 4*L.^2.* ... 
            ... (
                Vn.^2 - (v*cos(theta)).^2 - f.^2 ...
            ) ...
      ) ./ (2*(Vn.^2 - (v*cos(theta)).^2 - f.^2));

%%% aire
%%% vidrio
n = 1;
D_lambda = lambda/n*(-187500)*(v*(1-1/n^2)/(c/n));
thetap = theta - atan(v*sin(theta)/(c*n));
Vn = c/n + cos(thetap)*v*(1-1/n^2-D_lambda);
f = v*sin(theta)/(n^2);

L = L0*sqrt(1 - (beta*cos(theta).^2));

ta1 = ( ...
        2*L*v.*cos(theta) + ...
        sqrt(  (2*L*v.*cos(theta)).^2 + 4*L.^2.* ... 
            ... (
                Vn.^2 - (v*cos(theta)).^2 - f.^2 ...
            ) ...
      ) ./ (2*(Vn.^2 - (v*cos(theta)).^2 - f.^2));


N = (c/lambda/n)*((tg2-ta2)-(tg1-ta1));

plot(N)
% xlim([0 50])