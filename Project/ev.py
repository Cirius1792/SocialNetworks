import random
import pygmo as pg
from Project.OptNetworkModels import *
import os
import tempfile
from Project.network_analysis import avg_degree

class WS_problem:

    def __init__(self, n, clustering, deg):
        self._n = n
        self.__clustering = clustering
        self._deg = deg

    def fitness(self, x):
        """

        :param x:
        -x[0] = radius
        -x[1] = k
        :return: fitness
        """

        r = round(x[0])
        k = round(x[1])
        fd, path = tempfile.mkstemp()
        try:
            with os.fdopen(fd, 'w') as tmp:
                # do stuff with temp file
                g  = WSGridG_opt()
                c = nx.average_clustering(g)
                deg = avg_degree(g)
                ret = abs(self._deg - deg)
                if (deg > 85 and deg < 95):
                    ret +=10*abs(c-self.__clustering)
        finally:
            os.remove(path)
        return ret
    def get_bounds(self):
        return ([5,15],[5,20])


if __name__ == '__main__':
    mp = WS_problem(25000,0, )
    prob = pg.problem()