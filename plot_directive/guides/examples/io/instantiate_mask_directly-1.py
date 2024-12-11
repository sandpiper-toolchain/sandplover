for proportion in [0.1, 0.5, 0.9]:
    anydata = np.zeros((500, 1000), dtype=bool)

    whr = np.random.randint(0, anydata.size, size=int(anydata.size*proportion))
    anydata.flat[whr] = True

    lm = dm.mask.LandMask.from_array(
        anydata)

    fig, ax =  plt.subplots()
    lm.show(ax=ax)
    plt.show()