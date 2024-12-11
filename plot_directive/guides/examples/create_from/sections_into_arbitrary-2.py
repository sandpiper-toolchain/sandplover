fig, ax = plt.subplots()

ax.plot(css.s, css['eta'][-1, :])
ax.plot(pss.s, pss['eta'], '--')

plt.show()