clear all
clc

% declaro variables simbolicas de tipo real
syms vx vy ...
    t1 t2 t3 t4 ...
    t1V t2V t3V t4V ...
    t1s t2s t3s t4s ...
    r0 r1 r2 r3 ...
    d1 d2 d3 d4 ...
    d ...
    c L1 L2 gx gy bx by    ...
    r0_2 r2_2 d2_2 real


% asumo que algunas son positivas
assume(vx > 0 & vy > 0 & ...
    t1 > 0 &  t2 > 0 &  t3 > 0 & t4 > 0 & ...
    r0 > 0 & r1 > 0 & r2 > 0 & r3 > 0 &  ...
    t1s > 0 &  t2s > 0 &  t3s > 0 & t4s > 0 & ...
    t1V > 0 &  t2V > 0 &  t3V > 0 & t4V > 0 & ...
    d1 > 0 &  d2 > 0 &  d3 > 0 &  d4 & ...
    c > 0 &  L1 > 0 &  L2 > 0 & gx > 0 &  gy > 0)

% dibujito con las dimensiones del interferometro

%     r1         r2 
%      |---------|
%      |         | L1
%      |---------|
%     r0    L2   r3



% las cuentas la hago 
% ademas, considero los tiempor "por fragmento":
%     t0 = el tiempo de r0 a r1
%     t1 = el tiempo de r1 a r2 
%     ...

% rayo 1

% los r se definen de r0 a r, de r1 a r2, y de r2 a r3
% de manera vectorial:
% sumo el movimiento la posicion de la esquina del interferometro, 
% ** con respecto a punto anterior **

r0 = [0,0] %#ok<*NOPTS>
r1 = [vx*t1, vy*t1] + [0,gy*L1]
r2 = [vx*t2, vy*t2] + [gx*L2, 0]
r3 = [vx*t3, vy*t3] + [0, -gy*L1]

% la distancia entre dos 'r' es la norma de la diferencia entre los vectores
d1 = norm(r1 - r0)
d2 = norm(r2 - r0)
d3 = norm(r3 - r0)
d4 = norm(r2 - r0)

% hago qe el computador resuelva el sistema de ecuaciones para calcular el
% tiempo
t1s = solve(d1/c==t1, t1)
t2s = solve(d2/c==t2, t2)
t3s = solve(d3/c==t3, t3)
t4s = solve(d4/c==t2, t2)

% para la sustitucion numerica, tengo que poner algunos valores
% angulos es la rotacion del interferometro, las velocidades son senos y
% cosenos
angulos = 0:pi/400:2*pi;
vxn=cos(angulos)*300;
vyn=sin(angulos)*300;

% aqui evaluo numericamente las expresiones simbolicas. 'subs' es la
% funcion para 'sustituir'
t1V = eval(subs(subs(t1s, {L1, L2, gx, gy}, {.3/1000, .6/1000, 1/abs(sqrt(1-(vx/c)^2)), 1/abs(sqrt(1-(vy/c)^2))}),{vx,vy,c},{vxn,vyn,300000}));
t2V = eval(subs(subs(t2s, {L1, L2, gx, gy}, {.3/1000, .6/1000, 1/abs(sqrt(1-(vx/c)^2)), 1/abs(sqrt(1-(vy/c)^2))}),{vx,vy,c},{vxn,vyn,300000}));
t3V = eval(subs(subs(t3s, {L1, L2, gx, gy}, {.3/1000, .6/1000, 1/abs(sqrt(1-(vx/c)^2)), 1/abs(sqrt(1-(vy/c)^2))}),{vx,vy,c},{vxn,vyn,300000}));
t4V = eval(subs(subs(t4s, {L1, L2, gx, gy}, {.3/1000, .6/1000, 1/abs(sqrt(1-(vx/c)^2)), 1/abs(sqrt(1-(vy/c)^2))}),{vx,vy,c},{vxn,vyn,300000}));


% esto lo hago para quedarme solo con los tiempo positivos
% (debigo a la raiz cuadrada hay tiempo positivos y negativos)
t1V = t1V(t1V>0);
t2V = t2V(t2V>0);
t3V = t3V(t3V>0);
t4V = t4V(t4V>0);


% esto es para graficar...
for n=1:size(t4V)
    d = 300000*t4V(n)./cos(15/360*2*pi:pi/100000:30/360*2*pi);
    w = 632*10^9;
    plot(sin(w*d/300000));
    leyendas{n} = num2str(angulos(n)*360/2/pi);
    drawnow;
    pause(1/40);
end


