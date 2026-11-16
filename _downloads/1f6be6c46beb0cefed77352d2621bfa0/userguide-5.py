fig, ax = plt.subplots(1, 2, figsize=(7, 3))
ax[0].imshow(
    final["velocity"], cmap="plasma"
)  # display directly with plasma colormap for velocity
final.show("velocity", ax=ax[1], cmap="plasma")  # use the built-in show()
plt.show()
