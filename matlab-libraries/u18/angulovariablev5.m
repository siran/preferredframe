% simulacion a angulo variable

clear ta tv theta_deg

L = 0.58;
v = 350e3;
c = 3e8;
lambda = 532e-9;
dndl = 0.037;
tiempo2franjas = c/lambda;

n_vidrio = 1.52;
n_aire = 1.0003;

% theta_deg = (0:30:360);
rad = pi/180;
% theta = theta_deg*rad;


syms t np %theta v c n_aire n_vidrio real
assume(np>1)
assume(t>0)
% assume(c>0)
% assume(theta>=0)
% assume(theta<=2*pi)
% assume(v>0)
% assume(n_aire>1)
% assume(n_vidrio>1)
% assume(n_aire<1.1)
% assume(n_vidrio<1.6)
% assume(c>v)
% assume(n_aie<n_vidrio)

% t1 = asin(v*sin(theta)/c);
% t2 = asin(n_aire/n_vidrio*sin(t1));

    
i=0;
for ang=0:20:360
    i=i+1;
    theta_deg(i) = ang;
    theta = ang*rad;
    t1 = asin(v*sin(theta)/c);
    t2 = asin(n_aire/n_vidrio*sin(t1));
    
    g = sqrt(1-(v*cos(theta)/c)^2);
%     g=1;

    n = n_vidrio;
    a = g*L*tan(t2);
    % lambdap = (1+v*cos(theta)/(c/n))*lambda;
    
    arrastre = v*cos(theta)*(1-1/n^2);
    doppler = lambda*(1+arrastre/c);
    
    atran = (1-sin(theta));
    along = 0;
    
    b = (1-1/n^2+lambda*doppler/n*dndl)*v*t*(sin(theta) + atran);      
%     b = (1-1/n^2)*v*sin(theta)*t;  
    % b = (1-1/n^2)*v*t;      
    
    eqt = (c/n*t)^2-(g*L + along*v*cos(theta)*(1-1/n^2))^2-(a+b)^2;
  
    sol = solve(eqt, t, 'real', true);
    % eval(subs(a,t,sol))
    % eval(subs(b,t,sol))
    % eval(subs(a+b,t,sol))
    tiempo = sol;
    
    tv(i) = eval(tiempo);
    
    n = n_aire;
    a = g*L*tan(t1);
    b = (1-1/n^2)*v*t*(sin(theta) + atran);  

    eqt = (c/n*t)^2-(g*L+along*v*cos(theta)*(1/n^2))^2-(a+b)^2;
   
    sol = solve(eqt, t, 'real', true);
    tiempo = sol;
    
    ta(i) = eval(tiempo);
%     
%     diff(i) = tv(i)-ta(i);
end
figure('units','normalized','outerposition',[0 0 1 1])
p1 = subplot(2,2,1);
p2 = subplot(2,2,2);
p3 = subplot(2,2,3);

diff = tv-ta;
diff = diff - diff(1);

plot(p1,theta_deg, diff*tiempo2franjas)
title(p1,'Fringe displacement v. angle of rotation')
xlabel(p1,'Angle of rotation (º)')
ylabel(p1,'Fringe displacement')

plot(p2,theta_deg, (tv-tv(1))*tiempo2franjas)
title(p2,'Time of flight glass')
xlabel(p2,'Angle of rotation (º)')
ylabel(p2,'Time of flight - glass')

% figure
plot(p3,theta_deg, (ta-ta(1))*tiempo2franjas)
title(p3,'Time of flight - air')
xlabel(p3,'Angle of rotation (º)')
ylabel(p3,'Time of flight - air')

return

k_theta_vidrio = (sqrt(1 - (v*sin(theta)/(c*n_vidrio)).^2)).^(-1);
k_theta_aire   = (sqrt(1 - (v*sin(theta)/(c*n_aire  )).^2)).^(-1);
g_theta = (sqrt(1-(v*cos(theta)/c).^2)).^(-1);
c_theta_aire   = ((k_theta_aire  *n_aire  )/c).^(-1) - v*cos(theta)./(k_theta_aire  *n_aire  ).^2;
c_theta_vidrio = ((k_theta_vidrio*n_vidrio)/c).^(-1) - v*cos(theta)./(k_theta_vidrio*n_vidrio).^2;
t_theta_aire   = g_theta.^(-1).*(c_theta_aire  /L).^(-1);
t_theta_vidrio = g_theta.^(-1).*(c_theta_vidrio/L).^(-1);

thetam90 = (theta_deg-90)*pi/180;
k_thetam90_vidrio = (sqrt(1 - (v*sin(thetam90)/(c*n_vidrio)).^2)).^(-1);
k_thetam90_aire   = (sqrt(1 - (v*sin(thetam90)/(c*n_aire  )).^2)).^(-1);
g_thetam90 = (sqrt(1-(v*cos(thetam90)/c).^2)).^(-1);
c_thetam90_aire   = ((k_thetam90_aire  *n_aire  )/c).^(-1) - v*cos(thetam90)./(k_thetam90_aire  *n_aire  ).^2;
c_thetam90_vidrio = ((k_thetam90_vidrio*n_vidrio)/c).^(-1) - v*cos(thetam90)./(k_thetam90_vidrio*n_vidrio).^2;
t_thetam90_aire   = g_thetam90.^(-1).*(c_thetam90_aire  /L).^(-1);
t_thetam9090_vidrio = g_thetam90.^(-1).*(c_thetam90_vidrio/L).^(-1);

theta90 = (theta_deg+90)*pi/180;
k_theta90_vidrio = (sqrt(1 - (v*sin(theta90)/(c*n_vidrio)).^2)).^(-1);
k_theta90_aire   = (sqrt(1 - (v*sin(theta90)/(c*n_aire  )).^2)).^(-1);
g_theta90 = (sqrt(1-(v*cos(theta90)/c).^2)).^(-1);
c_theta90_aire   = ((k_theta90_aire  *n_aire  )/c).^(-1) - v*cos(theta90)./(k_theta90_aire  *n_aire  ).^2;
c_theta90_vidrio = ((k_theta90_vidrio*n_vidrio)/c).^(-1) - v*cos(theta90)./(k_theta90_vidrio*n_vidrio).^2;
t_theta90_aire   = g_theta90.^(-1).*(c_theta90_aire  /L).^(-1);
t_theta9090_vidrio = g_theta90.^(-1).*(c_theta90_vidrio/L).^(-1);

delta_t = t_theta_vidrio - t_theta_aire;
delta_t=delta_t-delta_t(1);

% % doble chepa
% plot(theta_deg, delta_t*tiempo2franjas, '.')
% title('Doble chepa perfecta')
% ylabel('Franjas')
% xlabel('Angulo rotación de isla (º)')
% xlim([0 360])

% efecto
% figure
% sint3 = (k_theta_vidrio*n_vidrio).^2/n_aire * (v/c) .* sin(theta);
% plot(theta_deg, sint3)
% title('sin(\theta_3)')
% ylabel('sin(\theta_3) (rad)')
% xlabel('Angulo rotación de isla (º)')
% xlim([0 360])



sint3 = (k_theta_vidrio*n_vidrio).^2/n_aire * (v/c) .* sin(theta);
t3 = asin(sint3);
t1 = acos(v*sin(theta)/c);

L1 = 0.1e-2; %cm
L2 = 0.20e-2;

% ta1 = (g_theta^(-1))*L1*((c_theta_aire)^(-1));
% tv1 = (g_theta^(-1))*L1*((c_theta_aire)^(-1));
% 
% %%% aumentando 90º para calcular L2 %%%%%%%%%%%%%%%%%%%%%%%%
% theta_deg = (0:5:360)+90;
% theta = theta_deg*pi/180;
% 
% k_theta_vidrio = (sqrt(1 - (v*sin(theta)/(c*n_vidrio)).^2)).^(-1);
% k_theta_aire   = (sqrt(1 - (v*sin(theta)/(c*n_aire  )).^2)).^(-1);
% 
% g_theta = (sqrt(1-(v*cos(theta)/c).^2)).^(-1);
% 
% c_theta_aire   = ((k_theta_aire  *n_aire  )/c).^(-1) - v*cos(theta)./(k_theta_aire  *n_aire  ).^2;
% c_theta_vidrio = ((k_theta_vidrio*n_vidrio)/c).^(-1) - v*cos(theta)./(k_theta_vidrio*n_vidrio).^2;
% 
% t_theta_aire   = g_theta.^(-1).*(c_theta_aire  /L).^(-1);
% t_theta_vidrio = g_theta.^(-1).*(c_theta_vidrio/L).^(-1);
% 
% ta2
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

h = L1*cos(t3).^(-1);

t1 = asin(v*sin(theta)/c);
h1   = g_theta.^(-1).*(c_theta_aire  /L1).^(-1);
% h1 = L1*cos(t1).^(-1);
h2 = L2-h1.*sin(t1)+h.*sin(t3);

figure
correccion = (h - h2 - h1)/c;
correccion = correccion - correccion(1);
plot(theta_deg, correccion - correccion(1))
title('dT ultimo segmento')

% delta = tan(t3);
% efecto = (delta + d) - sqrt(d^2 + delta.^2)/c;

figure
plot(theta_deg, delta_t)
title('doble chepa original')


% figure
% hold on
m=1
for m=-0.5:.1:0.5
    figure
    plot(theta_deg, (delta_t + m*correccion) * tiempo2franjas)
    title(['m=' num2str(m)])
%     plot(theta_deg, delta_t -min(delta_t))
end
title('doble chepa + efecto')
% figure
% plot(theta_deg, efecto - efecto(1))
return

figure
m = 5e-13;
plot(theta_deg, (m*sint3))
title('m*sin(t3)')

figure
m = 5e-13;
plot(theta_deg, (m*sint3)/correccion/max(sint3*m)*max(correccion))
title('m*sin(t3)')

return

% efecto
figure
% plot(theta_deg, sint3)
% hold on
plot(theta_deg, t3*180/pi)
% % % % hold on
% % % plot(theta_deg, cos(t3))
% % % ylim([-2 2])
% % % title('Angulo de salida del vidrio: \theta_3')
% % % ylabel('\theta_3 (º)')
% % % xlabel('Angulo rotación de isla (º)')
% % % xlim([0 360])

% suma
n=0;
figure
hold on
m = 5e-13;
legends{1}=num2str(m);
plot(theta_deg, (delta_t + m*sint3)*tiempo2franjas)
legend(legends)
title({'Movimiento de franjas esperado', 'considerando efecto de variación de ángulo de salida \theta_3'})
ylabel('Franjas')
xlabel('Angulo rotación de isla (º)')
xlim([0 360])
% % % 
% % % % figure
% % % % plot(theta_deg, (delta_t))
% % % % figure
% % % % plot(theta_deg, (cos(t3)))
% % % 
% % % 
% % % figure
% % % m=0.995666222748381e-9;
% % % plot(theta_deg, (delta_t - a(1)))