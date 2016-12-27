#!/usr/bin/env python3

import random
import math

class GibbsSampler(object):
    def __init__(self, document, V, K, alpha, beta):
        # document[][]
        self.document = document
        # vocabulary size
        self.V = V
        # number of topics
        self.K = K
        # number of documents
        self.M = len(document)

        self.alpha = alpha
        self.beta = beta

    def configure(self, iterations, burn_in, thin_interval, sample_lag):
        self.iterations = iterations
        self.burn_in = burn_in
        self.thin_interval = thin_interval
        self.sample_lag = sample_lag

    def initialisation(self):
        # doc:word-topic
        self.z = []

        # number of words in doc_i assigned to topic_j
        self.n_mk = [[0 for col in range(self.K)] for row in range(self.M)]
        # number of words in doc_i
        self.n_m = [0 for x in range(self.M)]
        # number of word_j assigned to topic_i
        self.n_kt = [[0 for col in range(self.V)] for row in range(self.K)]
        #number of words assigned to topic_i
        self.n_k = [0 for x in range(self.K)]

        for i in range(self.M):
            topics = []
            for j in range(len(self.document[i])):
                topic = math.floor(random.random() * self.K)
                topics.append(topic)

                self.n_mk[i][topic] += 1
                self.n_m[i] += 1
                self.n_kt[topic][self.document[i][j]] += 1
                self.n_k[topic] += 1

            self.z.append(topics)

    def gibbs_sampling(self):
        if self.sample_lag > 0:
            # M*K
            self.theta_sum = [[0 for col in range(self.K)] for row in range(self.M)]
            # K*V
            self.phi_sum = [[0 for col in range(self.V)] for row in range(self.K)]
            # sample counts
            self.num_stats = 0

        # initialisation
        self.initialisation()

        for round in range(self.iterations):
            for i in range(self.M):
                for j in range(len(self.document[i])):
                    # for the current assignment of k to a term t for word w_i,j
                    topic = self.z[i][j]

                    self.n_mk[i][topic] -= 1
                    self.n_m[i] -= 1
                    self.n_kt[topic][self.document[i][j]] -= 1
                    self.n_k[topic] -= 1

                    # multinomial sampling acc. to Eq.78 (decrements from previous step)
                    topic = self.sample_topic(i, j)

                    # for the new assignment of z_i,j to the term t for word w_i,j
                    self.n_mk[i][topic] += 1
                    self.n_m[i] += 1
                    self.n_kt[topic][self.document[i][j]] += 1
                    self.n_k[topic] += 1

                    self.z[i][j] = topic

            if round > self.burn_in and self.sample_lag > 0 and round % self.sample_lag == 0:
                self.update_theta()
                self.update_phi()
                self.num_stats += 1


    def sample_topic(self, m, n):
        distribution = []
        for k in range(self.K):
            p = (self.n_kt[k][self.document[m][n]] + self.beta) / (self.n_k[k] + self.beta * self.V) \
                * (self.n_mk[m][k] + self.alpha) / (self.n_m[m] + self.K * self.alpha)

            distribution.append(p)

        for i in range(1, len(distribution)):
            distribution[i] += distribution[i-1]

        ran_p = random.random() * distribution[-1]

        for i in range(len(distribution)):
            if distribution[i] >= ran_p:
                return i

        return len(distribution)-1 # 如果逻辑正确的话，不应该从这里返回


    def update_theta(self):
        for m in range(self.M):
            for k in range(self.K):
                self.theta_sum[m][k] += (self.n_mk[m][k] + self.alpha) / (self.n_m[m] + self.alpha * self.K)


    def update_phi(self):
        for k in range(self.K):
            for t in range(self.V):
                self.phi_sum[k][t] += (self.n_kt[k][t] + self.beta) / (self.n_k[k] + self.beta * self.V)

# # M*K
# self.theta = [[0 for col in range(self.K)] for row in range(self.M)]
# # K*V
# self.phi = [[0 for col in range(self.V)] for row in range(self.K)]

    def get_theta(self):
        theta = [[0 for col in range(self.K)] for row in range(self.M)]

        if self.sample_lag > 0:
            for i in range(self.M):
                for j in range(self.K):
                    theta[i][j] = self.theta_sum[i][j] / self.num_stats
        else:
            for i in range(self.M):
                for j in range(self.K):
                    theta[i][j] = (self.n_mk[i][j] + self.alpha) / (self.n_m[i] + self.alpha * self.K)

        return theta


    def get_phi(self):
        phi = [[0 for col in range(self.V)] for row in range(self.K)]

        if self.sample_lag > 0:
            for i in range(self.K):
                for j in range(self.V):
                    phi[i][j] = self.phi_sum[i][j] / self.num_stats
        else:
            for i in range(self.K):
                for j in range(self.V):
                    phi[i][j] = (self.n_kt[i][j] + self.beta) / (self.n_k[i] + self.beta * self.V)

        return phi


    def test(self):
        a = 1
        return a

if __name__ == '__main__':
    document = [
        [1, 4, 3, 2, 3, 1, 4, 3, 2, 3, 1, 4, 3, 2, 3, 6],
        [2, 2, 4, 2, 4, 2, 2, 2, 2, 4, 2, 2],
        [1, 6, 5, 6, 0, 1, 6, 5, 6, 0, 1, 6, 5, 6, 0, 0],
        [5, 6, 6, 2, 3, 3, 6, 5, 6, 2, 2, 6, 5, 6, 6, 6, 0],
        [2, 2, 4, 4, 4, 4, 1, 5, 5, 5, 5, 5, 5, 1, 1, 1, 1, 0],
        [5, 4, 2, 3, 4, 5, 6, 6, 5, 4, 3, 2]
    ]

    V = 7
    M = 6
    K = 2
    alpha = 2
    beta = 0.5

    gibbs = GibbsSampler(document, V, K, alpha, beta)
    gibbs.configure(10000, 2000, 100, 10)
    gibbs.gibbs_sampling()

    theta = gibbs.get_theta()
    phi = gibbs.get_phi()

    for row in theta:
        for col in row:
            print(col, end=' ')
        print()

    print()

    for row in phi:
        for col in row:
            print(col, end=' ')
        print()

    gibbs.test()
