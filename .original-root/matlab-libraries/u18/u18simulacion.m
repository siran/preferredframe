theta_ang = 0:10:360;
rad = pi/180;
theta = theta_ang*rad;

% plot(sin(theta))


L=1;
lambda = 532e-9;
c = 3e8;
n_a = 1;
n_v = 1.6;
dndl = -4.3e-5;
v=350e3;

beta = v*cos(theta)/c;
alfa2 = sqrt(1-beta.^2);
alfa = sqrt(1-(v/c)^2);




cpar2 = L*(c/n_v+v*cos(theta)*(1/n_v^2 + lambda/n_v*dndl));
cper2 = L*(sqrt(c^2/n_v^2 - (v.*sin(theta).^2/n_v^4)));
d = (alfa2.*cpar2.^(-1) + cper2.^(-1))*c/lambda;
d = d-d(1);

% plot(theta_ang,cpar2)
% hold on
% plot(theta_ang,cper2)

dpar = L*alfa*(c/n_v + sign(-cos(theta))*v*(1/n_v^2 + lambda/n_v*dndl)).^(-1);
dper = L/(sqrt(c^2/n_v^2 - (v^2/n_v^4)));
franjas = ...
    sqrt( ...
        (dpar.*cos(theta)).^2 + ...
        (dper.*sin(theta)).^2 ...
    )*c/lambda;

franjas = franjas - franjas(1);
plot(theta_ang, franjas)

% figure
% hold on