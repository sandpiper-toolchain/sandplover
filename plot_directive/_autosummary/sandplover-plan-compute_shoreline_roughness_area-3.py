from sandplover.plan import compute_shoreline_roughness_area
rgh0 = compute_shoreline_roughness_area(sm0, lm0)
rgh1 = compute_shoreline_roughness_area(sm1, lm1)
#
fig, ax = plt.subplots(1, 2, figsize=(6, 3))
golf.quick_show("eta", idx=15, ax=ax[0])
_ = ax[0].set_title("roughness = {:.2f}".format(rgh0))
golf.quick_show("eta", idx=-1, ax=ax[1])
_ = ax[1].set_title("roughness = {:.2f}".format(rgh1))
