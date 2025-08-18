    x=-4:5;
    y=1+2*(sin(2*pi*0.1*x+2)+0.3*randn(size(x)));%Sine + noise
    tic;
    [SineP]=sineFit(x,y) %Offset, amplitude, frquency, phase, MSE
    toc
%uncomment following line if you want to save y=f(x) and run it sineFitDemo
% save('xy.mat','x','y');