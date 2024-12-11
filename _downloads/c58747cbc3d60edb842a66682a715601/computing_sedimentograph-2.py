GM = dm.mask.GeometricMask(
    golfcube['eta'][-1],
    angular=dict(
        theta1=np.pi/8,
        theta2=np.pi/2-(np.pi/8))
    )
GM_mask_strat = np.tile(GM.mask, (golfstrat.shape[0], 1, 1))  # a mask with same dimensions as stratigraphy
frozen_sand_mask = frozen_sand.where(GM_mask_strat, np.nan)

(sedimentograph2,
    section_radii2,
    sediment_bins2) = dm.strat.compute_sedimentograph(
    frozen_sand_mask,
    num_sections=50,
    # last_section_radius=2750,
    sediment_bins=None,
    background=background,
    origin_idx=[3, 100])

# add this line to the same plot as above
ax.plot(
    section_radii2,
    sedimentograph2[:, 1],  # plot only the second bin (sandfrac > 0.5)
    'o-')
plt.show()