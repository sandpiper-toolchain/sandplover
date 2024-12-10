r = np.linspace(1, 1000, num=50)
R = (np.pi * r) / np.sqrt(0.5 * np.pi * r * r)

fig, ax = plt.subplots()
ax.plot(r, R)
ax.set_xlabel('radius')
ax.set_ylabel('shoreline roughness')
plt.show()