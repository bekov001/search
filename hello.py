def get_size(toponym):
    toponym_size = [[float(j) for j in i.split()] for i in
                    list(toponym["boundedBy"]["Envelope"].values())]

    delta = str(min(abs(toponym_size[0][0] - toponym_size[1][0]),
                    abs(toponym_size[0][1] - toponym_size[1][1])))
    return delta