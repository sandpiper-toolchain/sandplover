fig, ax = plt.subplots()
im = ax.imshow(MP.composite_array)
dm.plot.append_colorbar(im, ax=ax)
plt.show()