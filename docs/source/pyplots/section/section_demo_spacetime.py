import matplotlib.pyplot as plt

import sandplover as spl

golfcube = spl.sample_data.golf()


fig, ax = plt.subplots(figsize=(8, 2))
golfcube.register_section("demo", spl.section.StrikeSection(distance_idx=5))
golfcube.sections["demo"].show("velocity")
