""" analiza los excel los csv"""

import os
import matplotlib
# matplotlib.use('TkAgg')
from matplotlib import pyplot as plt
import pandas as pd

source_path = "../analysis-summaries"

files = [f for f in os.listdir(source_path) if ".xls" in f]

df = pd.read_excel(os.path.join(source_path, files[0]))
df = df[df["figure_type"] == "normalized"]
df.set_index("datetime")
print(df)

dates = df["datetime"]
amplitudes = df["amplitude"]
mavg = df.rolling(3).mean()
# plt.figure(1)


df["amplitude_avg"] = amplitudes.rolling(3).mean()
plt.scatter("datetime", "amplitude", data=df)
plt.plot("datetime", "amplitude_avg", color="orange", data=df)
day_old = None
for i,d in df.iterrows():
    print(i,d)
    if not d or i>0:
        day_old = d.datetime
plt.axvline(x=0.22058956)

# plt.scatter(dates, amplitudes)
ax = plt.gca()
ax.set_ylim([0.3, 0.8])

plt.show()

print(files)
print(df)