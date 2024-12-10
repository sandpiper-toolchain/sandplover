fig, ax = plt.subplots(1, 2, figsize=(7, 3))
ax[0].imshow(circular['velocity'])   # display directly
circular.show('velocity', ax=ax[1])  # use the built-in show()
plt.show()
