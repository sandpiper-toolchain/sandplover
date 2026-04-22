import os

os.makedirs("../../../../build/plot_directive/guides/examples/plot/", exist_ok=True)

anim = animation.FuncAnimation(fig, update_field, frames=time_idxs, interval=5)
anim.save('../../../../build/plot_directive/guides/examples/plot/strat_movie.gif', fps=5)

anim = animation.FuncAnimation(
    fig, update_field,
    frames=time_idxs,
    interval=5,
    blit=False)
anim.save('../../../../build/plot_directive/guides/examples/plot/simple_movie.gif', fps=5)

plt.show()