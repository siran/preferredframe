% test hello world

a=2.5;
x=1:0.1:360;
prediction = a*cos(x*pi/180);

data = 1.5*a*cos(x*pi/180+pi/3);

plot(x, data, 'rx')
hold on 
plot(x,prediction, 'b--')
xlim([0, 360])

title('hello world')
xlabel('x range')
ylabel('f(x)')
legend({'data', 'prediction'})