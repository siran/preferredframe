% radiance

a=1
clear all
syms h c k f T
% syms f

% h = 6.62607015E-34  % J?Hz?1
% c = 3e8             % m/s
% k = 1.380649E-23    % J?K?1
% % % f = 1/(24*60*60)    % 1/s
% T = 2.7             % K

h = 6.62607015  % J?Hz?1
c = 3e8             % m/s
k = 1.380649    % J?K?1
% % f = 1/(24*60*60)    % 1/s
T = 2.7             % K

r = 2*h*f^3 /c^2 / (1/exp(h*f/k/T)-1)

dr = diff(r,'f')

% h = 6.62607015E-34  % J?Hz?1
% c = 3e8             % m/s
% k = 1.380649E-23    % J?K?1
% % % f = 1/(24*60*60)    % 1/s
% T = 2.7             % K

eval(int(dr, f, 1/(24*60), 1e3))







