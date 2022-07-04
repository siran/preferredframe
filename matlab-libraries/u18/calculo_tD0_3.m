clc
clear all
format long

g = 0.2;
s = 0.2;
h = 0.585;
c = 3*10^8;
v = 370*10^3;
n = 1.591;
o = 633*10^-9;

a = sqrt(1-v^2/c^2);

tF10 = (g/c)/a;
alfa = atan(v*tF10/g)

c = (c/n)*sqrt(sin(alfa)^2 + cos(alfa)^2);
nc = (c/n)*sqrt((sin(alfa)+v*(1-1/n^2))^2 + cos(alfa)^2);

nc/c

% fprintf('g = %e\n', g);
% fprintf('s = %e\n', s);
% fprintf('h = %e\n', h);
% fprintf('c = %e\n', c);
% fprintf('v = %e\n', v);
% fprintf('n = %e\n', n);
% fprintf('o = %e\n', o);
% fprintf('a = %e\n', a);
% fprintf('\n');
% 
% % tF10 = (g/c)/a;
% % dF10 = tF10*c;
% 
% tD30 = (h/a)*(1/sqrt((c/n)^2-v^2))
% 
% tF30 = h/(c*a^2)
% dF30 = tF30*c
% 
% tFarr = v*(1-1/n^2)*tD30/c
% 
% dT30 = tF30 - tD30
% 
% N = dT30*c/o
% 
% 
% 
% % tF30 = (g/c)/a;
% % dF30 = tF10*c;
% % 
% % alfa = atan(v*tF10/g)
% % alfaAngular = alfa*180/pi
% 
% % angulos = solve('dF20 = h*sin(kapa)','kapa = asin(sin(atan(dF20/h))/n)','kapa')
% % 
% % dDdiff20 = dF20/n
% % dD20 = sqrt(dDdiff20^2 + h^2)
% % 
% % dD = dF20 - dD20
% % 
% % tD20 = dD20/(c/n)
% % 
% % N = (tD20 - tF20)*c/o
% 
% 
% 
% % sinatan(dF20/h)*180/pi
% % 
% % sin(atan(dF20/h))
% % 
% % n*sin(atan(dF20/h))
% % 
% % kapa = asin(n*sin(atan(dF20/h)))*180/pi
% 
% % alfa = atan(v*tF10/g)
% % alfaAngular = alfa*180/pi
% % 
% % gama = eval(angulos.gama)
% % kapa = eval(angulos.kapa)
% % 
% % 
% % 
% % gamaAngular=gama*180/pi
% % kapaAngular=kapa*180/pi
% 
% % 2*sin(gama)*g+h*sin(kapa)
% % 3*dF10
% 
% % dD10 = sin(gama)*g-g
% % dF10-g
% 
% % kappa = asin(sin(gamma)/n)
% % 
% % dD10 = sin(gamma)*g
% % dD20 = sin(kappa)*h
% % dD30 = sin(gamma)*g
% 
% 
% 
% 
% 
% % alfa = atan(v*tF10/g);
% % gamma = asin(n*sin(alfa));
% % 
% % dFv02 = g/cos(alfa);
% % 
% % dDa0 = g/cos(gamma);
% % 
% % tDa0 = dDa0/c;
% % 
% % dtFDa0 = tF0-tDa0;
% % 
% % fprintf('tF0 = %e\n', tF0);
% % fprintf('alfa = %e\n', alfa);
% % fprintf('gamma = %e\n', gamma);
% % 
% % % lado del vidrio, parte de afuera
% % fprintf('tDa0 = %e\n', tDa0);
% % fprintf('dDa0 = %e\n', dDa0);
% % fprintf('dDa0 = %e\n', Da0);
% % 
% % % fuera del vidrio
% % fprintf('tFv0 = %e\n', tFv0);
% % fprintf('dFv0 = %e\n', dFv0);
% % fprintf('dFv02 = %e\n', dFv02);
% % 
% % 
% % fprintf('dtFDa0 = %e\n', dtFDa0);
% % fprintf('dtFDa0(franjas) = %f\n', dtFDa0*c/o);
% 
% 
% 
% % syms tD0 positive
% 
% % tDv0 = solve('v*tF0 = sqrt((sqrt((tDv0*c/n)^2 - h^2) + v*(1 - 1/n^2)*tDv0)^2 - h^2)', 'tDv0')
% % 
% % d
% 
% 
