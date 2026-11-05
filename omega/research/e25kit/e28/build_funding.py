import zipfile, io, csv, glob, os, numpy as np
Z = np.load('daily_panel.npz'); D0 = int(Z['days'][0]); syms = list(Z['syms']); T = len(Z['days']); FD = np.zeros((T, len(syms)), np.float32); n = 0
for j, s in enumerate(syms):
    for f in sorted(glob.glob(f'fund/{s}/*.zip')):
        z = zipfile.ZipFile(f)
        for r in csv.reader(io.TextIOWrapper(z.open(z.namelist()[0]), 'utf-8')):
            if not r or not r[0][:1].isdigit(): continue
            t = int(r[0]); t = t//1000 if t > 10**14 else t; d = t//86_400_000 - D0
            if 0 <= d < T: FD[d, j] += float(r[-1]); n += 1
np.save('daily_funding.npy', FD); print(n, 'funding payments;', int((FD != 0).any(0).sum()), 'coins with funding; mean daily funding (all coin-days with any):', float(FD[FD != 0].mean()))
