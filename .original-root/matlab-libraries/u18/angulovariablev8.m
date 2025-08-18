% simulacion a angulo variable

clear all
% clear ta tv theta_deg
syms t np %theta v c n_aire n_vidrio real
assume(t>0)

L = 0.000585;
v = 330;
c = 3e5;
lambda = 632E-9/1000;
tiempo2franjas = c/lambda;

n_vidrio = 1.601;
n_aire = 1.0003;

rad = pi/180;

for tipo=1:2
    i=0;
    if tipo==1
        n = n_vidrio;
        dis = 0.037462055;        
    else
        n = n_aire;
        dis=0;
    end    
    for ang=1:30:360
        i=i+1;
        theta_deg(i) = ang;
        theta = ang*rad;
        t1 = asin(v*sin(theta)/c);
        t2 = asin(n_aire/n_vidrio*sin(t1));        
        
        g = sqrt(1-(v*cos(theta)/c)^2);
        a = g*L         + v*cos(theta)*t;
        b = g*L*tan(t2) + v*sin(theta)*t;  
        
        eqt = (c/n*t + v*(1/n^2-dis)*t )^2 - (g*L)^2 - b^2;
        tiempo = solve(eqt, t, 'real', true);
        
        if tipo==1
            tv(i) = eval(tiempo);
        else
            ta(i) = eval(tiempo);
        end
    end
end
figure('units','normalized','outerposition',[0 0 1 1])
p1 = subplot(2,2,1);
p2 = subplot(2,2,2);
p3 = subplot(2,2,3);

diff = tv-ta;
diff = diff - diff(1);

plot(p1,theta_deg, diff*c/lambda)
% hold(p1,'on')
% plot(p1,theta_deg(1:end-shift), sin(theta_deg*rad))
% plot(p1,theta_deg(1:end-shift), 0.6*sin(theta_deg*rad) + diff*tiempo2franjas)
title(p1,'Fringe displacement v. angle of rotation')
xlabel(p1,'Angle of rotation (º)')
ylabel(p1,'Fringe displacement')



plot(p2,theta_deg, (tv-tv(1))*tiempo2franjas)
title(p2,'Time of flight in glass')
xlabel(p2,'Angle of rotation (º)')
ylabel(p2,'Time of flight in glass')

% figure
plot(p3,theta_deg, (ta-ta(1))*tiempo2franjas)
title(p3,'Time of flight in air')
xlabel(p3,'Angle of rotation (º)')
ylabel(p3,'Time of flight in air')

drawnow