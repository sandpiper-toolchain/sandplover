# check out the data before we save it into a netcdf file
print("eta shape:", eta.shape)
fig, ax = plt.subplots(2, len(t), figsize=(8, 3))
for i, _t in enumerate(t):
    ax[0, i].imshow(eta[i, :, :])
    ax[1, i].imshow(velocity[i, :, :])
plt.show()