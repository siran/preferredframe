% simulacion a angulo variable

L = 0.58;
v = 350e3;
c = 3e8;
lambda = 532e-9;
tiempo2franjas = c/lambda;

n_vidrio = 1.52;
n_aire = 1.005;

theta_deg = (0:5:360);
theta = theta_deg*pi/180;

k_theta_vidrio = (sqrt(1 - (v*sin(theta)/(c*n_vidrio)).^2)).^(-1);
k_theta_aire   = (sqrt(1 - (v*sin(theta)/(c*n_aire  )).^2)).^(-1);

g_theta = (sqrt(1-(v*cos(theta)/c).^2)).^(-1);

c_theta_aire   = ((k_theta_aire  *n_aire  )/c).^(-1) - v*cos(theta)./(k_theta_aire  *n_aire  ).^2;
c_theta_vidrio = ((k_theta_vidrio*n_vidrio)/c).^(-1) - v*cos(theta)./(k_theta_vidrio*n_vidrio).^2;

t_theta_aire   = g_theta.^(-1).*(c_theta_aire  /L).^(-1);
t_theta_vidrio = g_theta.^(-1).*(c_theta_vidrio/L).^(-1);

t_theta_aire   = t_theta_aire-t_theta_aire(1);
t_theta_vidrio = t_theta_vidrio - t_theta_vidrio(1);

delta_t = t_theta_vidrio - t_theta_aire;
% delta_t=delta_t-delta_t(1);

sint3 = (k_theta_vidrio*n_vidrio).^2/n_aire * (v/c) .* sin(theta);
theta3 = asin(sint3);
theta1 = asin(v/c);

L1 = 0.02;
L2 = 0.05;



theta90 = theta+pi/2;
k_theta_aire90   = (sqrt(1 - (v*sin(theta90)/(c*n_aire  )).^2)).^(-1);
g_theta90 = (sqrt(1-(v*cos(theta90)/c).^2)).^(-1);
c_theta_aire90   = ((k_theta_aire90  *n_aire  )/c).^(-1) - v*cos(theta90)./(k_theta_aire90  *n_aire  ).^2;

TL1a = g_theta.^(-1).*(c_theta_aire  /L1).^(-1);
TL1a = L1*cos(theta1).^(-1)/c;
TL2a = L2*cos(theta1).^-1*c_theta_aire.^(-1);
TL1v = cos(theta3).^(-1)*L1.*c_theta_aire.^(-1);

TL1a = TL1a-TL1a(1);
TL2a = TL2a-TL2a(1);
TL1v = TL1v-TL1v(1);

figure
hold on
% plot(theta_deg, t_theta_vidrio,'o')
% plot(theta_deg, t_theta_aire,'.')

plot(theta_deg, TL1a)
% plot(theta_deg, TL2a)
plot(theta_deg, TL1v)
legend('vidrio','aire','l1a','l2a','l1v')

figure
plot(theta_deg, TL1a-TL1v)
legend('diff')
% return

figure
plot(t_theta_vidrio-t_theta_aire)
title('vidrio - aire')

correccion = TL1v-(TL1a+TL2a);
% correccion = correccion - correccion(1);

figure
plot(theta_deg, delta_t)
hold on
plot(theta_deg, correccion)
plot(theta_deg, delta_t+correccion)
legend('dt','corr','final')


