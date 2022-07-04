path ='C:\Users\an\Documents\megasync-preferredframe\figures';
fname= 'summary.csv';
data = readtable([path '\' fname]);

tipo = {sdata.grouping_type};
t = {sdata.time};
a = [sdata.amplitude]

i = strcmp(tipo, 'r10s6');

t = [datenum(t(i))]
a = a(i)

plot(t,a)


