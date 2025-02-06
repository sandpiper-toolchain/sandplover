fig, ax = plt.subplots()
im = ax.imshow(OAP.composite_array)
spl.plot.append_colorbar(im, ax=ax)
plt.show()