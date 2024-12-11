hcirc = np.zeros((500, 1000), dtype=bool)
dx = 10
x, y = np.meshgrid(
    np.linspace(0, dx*hcirc.shape[1], num=hcirc.shape[1]),
    np.linspace(0, dx*hcirc.shape[0], num=hcirc.shape[0]))
center = (0, 5000)

dists = (np.sqrt((y - center[0])**2 +
                 (x - center[1])**2))
dists_flat = dists.flatten()

# apply the landscape change inside the domain
in_idx = np.where(dists_flat <= 3000)[0]
hcirc.flat[in_idx] = True

fig, ax = plt.subplots()
ax.imshow(hcirc, extent=[x.min(), x.max(), y.max(), y.min()])
plt.show()