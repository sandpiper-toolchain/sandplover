fig, ax = plt.subplots()
im = ax.imshow(OAP.composite_array)
dm.plot.append_colorbar(im, ax=ax)
plt.show()