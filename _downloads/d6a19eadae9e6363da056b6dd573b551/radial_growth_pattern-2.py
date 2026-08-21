# make a predictive model
def predict_for_t(t, Qs, hb):
    """Predict the delta shoreline radius.
    """
    return np.sqrt((2*t*Qs) / (hb * np.pi))

# set up the parameters
hb = golf.aux['hb'].data  # basin depth, m
Qs = (golf.aux['h0'].data *
      golf.aux['u0'][0].data *
      golf.aux['N0'].data *
      golf.aux['dx'].data *
      (golf.aux['C0_percent'][0].data / 100))  # sediment input, m3/s
t = np.linspace(0, float(golf.t[time_idxs[-1]]), num=100)

# make the figure
fig, ax = plt.subplots()

ax.plot(
    t, predict_for_t(t, Qs, hb))
ax.errorbar(
    golf.t[time_idxs], shoredist_mean, shoredist_std,
    c='r', ls='none')
ax.plot(
    golf.t[time_idxs], shoredist_mean,
    c='r', marker='o')

ax.set_ylabel('radius (m)')
ax.set_xlabel('time (s)')
plt.show()