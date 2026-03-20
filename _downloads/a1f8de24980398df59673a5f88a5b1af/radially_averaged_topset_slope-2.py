nums = np.arange(1, 31)
means = np.zeros(len(nums))
stds = np.zeros(len(nums))

for i, num in enumerate(nums):
    means[i], stds[i] = spl.plan.compute_topset_slope(
        golf["eta"][-1, :, :], num=num,
        origin=origin
    )


fig, ax = plt.subplots()
ax.errorbar(nums, means, yerr=stds, marker="none", linestyle="none", color="k")
ax.plot(nums, means, marker="o", linestyle="none", color="k")
ax.set_xlabel('number of sections [-]')
ax.set_ylabel('topset slope [-]')
plt.show()