% clc
clear all
format long


% % % % constantes

g = 0.2;
s = 0.2;
w = 0.585;
c = 3*10^8;
v = 370*10^3;
n = 1.591;
o = 633*10^-9;



%%%% cuenta del paper
fprintf('cuenta del paper:')

a = sqrt(1-v^2/c^2);

tAB = s/(c*a);
tCD = s/(c*a);

tLM = a*w/(c-v);

tFE = a*w/(c/n - (v/(n^2)));

tAB2 = a*s/(c+v);
tCD2 = a*s/(c-v);

tLM2 = w/(c*a);

% tFE2 = w*n/(c^2 - (v/n)^2);

tFE2 = w/(sqrt((c/n)^2 - (v/n^2)^2));

dT10 = (tAB+tCD+tLM-tFE);
dT20 = (tAB2+tCD2+tLM2-tFE2);
dT0 = dT10-dT20;



N = dT0*c/o


%%%%%%% cuenta con un ap tomando en cuenta el arrastre !

fprintf('cuenta del paper con contraccion tomando en cuenta el n y el arrastre:')

a = sqrt(1-v^2/c^2);
ap = sqrt(1-(v)^2/(c*n)^2);


tAB = s/(c*a);
tCD = s/(c*a);

tLM = a*w/(c-v);

tFE = ap*w/(c/n - (v/(n^2)));

tAB2 = a*s/(c+v);
tCD2 = a*s/(c-v);

tLM2 = w/(c*a);

tFE2 = w/sqrt((c/n)^2 - (v/n^2)^2);

dT0 = (tAB+tCD+tLM-tFE)-(tAB2+tCD2+tLM2-tFE2);


N = dT0*c/o

%%%%%%% cuenta de shamir, con un ap tomando en cuenta el arrastre !

fprintf('cuenta de shamir con contraccion tomando en cuenta el n y el arrastre:')

a = sqrt(1-v^2/c^2);
ap = sqrt(1-(v)^2/(c*n)^2);
ap=a;

tABC = 2*w/(c/n*ap);

tADC = 2*w/((c/n)*ap);

dT = tABC - tADC;

N=dT*c/o