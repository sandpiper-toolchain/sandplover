import os

os.makedirs("../../../../build/plot_directive/guides/examples/plot/", exist_ok=True)

anim = animation.FuncAnimation(
    fig, update_field,
    frames=golf.shape[0]-1,
    interval=20,
    blit=False)
anim.save('../../../../build/plot_directive/guides/examples/plot/simple_movie.gif', fps=30)

plt.show()