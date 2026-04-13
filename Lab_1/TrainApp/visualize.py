import matplotlib.pyplot as plt


def visualize(graph, path, stops):

    if not path:
        print("No path to visualize")
        return

    x = []
    y = []
    labels = []

    for item in path:

        # берём только stop_id (первый элемент)
        stop_id = item[0]

        if stop_id in stops:
            x.append(stops[stop_id]["lon"])
            y.append(stops[stop_id]["lat"])
            labels.append(stops[stop_id]["name"])

    plt.figure(figsize=(10, 6))

    plt.plot(x, y, marker='o')

    for i, name in enumerate(labels):
        plt.text(x[i], y[i], name, fontsize=8)

    plt.title("Train route")
    plt.xlabel("Longitude")
    plt.ylabel("Latitude")

    plt.grid()
    plt.show()