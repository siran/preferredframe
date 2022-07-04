xo = x_timestamp(1);
xf = x_timestamp(size(sig,1));

slope = 100*(77-48)/(735733.9434143519 - 735736.5059027778);
slope = (77-48)/(16550-9240);

sig2 = zeros(size(sig));

for i = 1:size(sig,1)
    sig2(i) = sig(i)-slope*(x_timestamp(i)-xo);
    sig2(i) = sig(i)-slope*(i-1);
end

figure
% plot(x_timestamp, sig2, 'x')
plot(x_timestamp, sig2, 'x')