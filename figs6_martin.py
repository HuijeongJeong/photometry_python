from collections import defaultdict
from multiprocessing import Pool

import numpy as np
from matplotlib import pyplot as plt


class S6AAssociated:
    def __init__(self, p=0.1, x=5, hmm=None):
        # p = probability of cue, x = reward delay
        # hmm is a function that projects from the full environment state space to the state space of the animal
        self.p = p
        self.x = x
        self.hmm = (lambda s: s) if hmm is None else hmm
        self.state_ = (tuple(), 1, self.x + 1)  # (tuple of "open" cue times, time since last rew, time since last cue)

    @property
    def state(self):
        return self.hmm(self.state_)

    def step(self):
        if len(self.state_[0]) > 0 and self.state_[0][0] == self.x - 1:  # a reward is due, remove open cue
            r = 1
            self.state_ = (self.state_[0][1:], -1, self.state_[2])
        else:
            r = 0
        if np.random.rand() < self.p:  # a cue arrived, add it to the list of open cues
            self.state_ = (self.state_[0] + (-1,), self.state_[1], -1)
        self.state_ = (tuple(t + 1 for t in self.state_[0]), self.state_[1] + 1, self.state_[2] + 1)  # advance time
        return self.hmm(self.state_), r


def hmm_csc1(s): return 'c' if s[-1] == 0 else 'r' if s[-2] == 0 else min(s[1], s[2])  # one state CSC
def sf_csc1(s): return s == 'c'  # True if cue else False


def hmm_csc2(s): return s[1:]  # two state CSC
def sf_csc2(s): return s[-1] == 0  # True if cue else False


def no_hmm(s): return s[0]  # env state space
def sf_no(s): return len(s)>0 and s[-1] == 0  # True if cue else False


def hmm_csc3(s): return 'r' if s[-2] == 0 else 'c' if s[-1] == 0 else (
    min(s[1], s[2]), [s[1], s[2]].index(min(s[1], s[2]))
)  # state space in main paper
def sf_csc3(s): return s == 'c'  # True if cue else False


class S6ANonAssociated:
    def __init__(self, p=0.1, hmm=None):
        self.p = p
        self.state_ = ((False, False), int(1 / p), int(1/p))
        self.hmm = (lambda x:x[0]) if hmm is None else hmm

    @property
    def state(self):
        return self.hmm(self.state_)

    def step(self):
        state = tuple(np.random.rand(2)<self.p)
        self.state_ = (state, 0 if state[0] else self.state_[1] + 1, 0 if state[1] else self.state_[2] + 1)
        return self.hmm(self.state_), int(self.state_[0][0])


def td0tabular(i, env, gamma=0.95, ns=int(1.2e5), alpha=.05, state_filter=None):
    np.random.seed(i)
    env = S6ANonAssociated(*env) if len(env) == 2 else S6AAssociated(*env)
    vf, rpes, vc = defaultdict(float), defaultdict(list), defaultdict(int)
    s = env.state
    for i in range(1,ns+1):
        if i >= ns*0.5: vc[s] += 1
        sp, r = env.step()
        delta = r + gamma * vf[sp] - vf[s]  # RPE
        vf[s] = vf[s] + alpha * delta  # TD(0)
        # vf[s] = vf[s] + (alpha if i < ns * 0.5 else alpha / vc[s]**(0.5)) * delta  # TD(0) with LR decay
        if i>ns*0.75:  # Use last quarter of steps for evaluation
            alpha=0.
            rpes[sp].append(delta)
        s = sp

    state_filter = state_filter or (lambda s: True)
    rpes = sum([v for k,v in rpes.items() if state_filter(k)],[])  # combine states for which we want rpe (cue onset)
    return np.array(rpes).mean()


def td0tabular_pool(env, gamma=0.986, ns=int(2e6), alpha=.05, state_filter=None, n=10):  # run 10 repeats
    rpes = list(Pool(n).starmap(td0tabular, [(i, env, gamma, ns, alpha, state_filter) for i in range(n)]))
    return [np.mean(rpes), np.std(rpes)]


def task6a(y=60.):  # generates the data for s6
    p = 1/y  # y is the ICI (inter cue interval), measured in time bins.
    xovery = np.array([0.05, 0.1, 0.2, 0.5, 1., 2., 5.])  # values of cue-reward-delay (X) / ICI for which we want RPE
    xs = [round(xy/p) for xy in xovery]  # compute the X's corresponding to the above x-over-y

    nas = [td0tabular_pool((p, hmm), state_filter=sf) for hmm, sf in
           zip([hmm_csc3, hmm_csc1, hmm_csc2, no_hmm], [sf_csc3, sf_csc1, sf_csc2, sf_no])]
    all_res = [[na[0] for na in nas]]
    all_res += [[td0tabular_pool((p, x, hmm), state_filter=sf) for x in xs] for hmm, sf in
                zip([hmm_csc3, hmm_csc1, hmm_csc2, no_hmm], [sf_csc3, sf_csc1, sf_csc2, sf_no])]

    import pickle
    with open("./s6data.pickle", "wb") as fp:
        pickle.dump((all_res, p, xovery), fp)


def task6atheory():
    pgs = [(0.05,0.95), (0.05,0.99), (0.5,0.95), (0.5,0.99)]
    xs = list(range(1,17,2))

    all_res = [[td0tabular_pool((p, x, no_hmm), gamma, state_filter=sf_no) for x in xs] for p, gamma in pgs]

    theories = [[[gamma**x*(1-p*gamma), 0.] for x in xs] for p, gamma in pgs]  # exact formula

    import pickle
    with open("./s6theory.pickle", "wb") as fp:
        pickle.dump(((all_res, theories), pgs, xs), fp)


def task6atheoryshort():
    xpg = [(2, 0.5, 0.98),(10, 0.1, 0.98),(50, 1/50, 0.98)]

    all_res = [td0tabular_pool((p, x, no_hmm), gamma, state_filter=sf_no) for x, p, gamma in xpg]

    theories = [gamma**(x)*(1-p) for x, p, gamma in xpg]  # exact formula

    import pickle
    with open("./s6theorys.pickle", "wb") as fp:
        pickle.dump(((all_res, theories), xpg), fp)


def plot6a(all_res="./s6data.pickle"):  # plots the data to PDF
    import pickle
    with open(all_res, "rb") as fp:
        all_res, p, xovery = pickle.load(fp)
    print(all_res)
    nas, ress = all_res[0], all_res[1:]

    plt.rcParams['axes.titlesize'] = 10
    plt.rcParams['axes.labelsize'] = 8
    plt.rcParams['xtick.labelsize'] = 8
    plt.rcParams['ytick.labelsize'] = 8
    plt.rcParams['legend.fontsize'] = 8
    plt.rcParams['legend.labelspacing'] = 0.2
    plt.rcParams['axes.labelpad'] = 2
    plt.rcParams['axes.linewidth'] = 0.35
    plt.rcParams['xtick.major.size'] = 1
    plt.rcParams['xtick.major.width'] = 0.35
    plt.rcParams['xtick.major.pad'] = 3
    plt.rcParams['ytick.major.size'] = 1
    plt.rcParams['ytick.major.width'] = 0.35
    plt.rcParams['ytick.major.pad'] = 2
    plt.rcParams['lines.scale_dashes'] = False
    plt.rcParams['lines.dashed_pattern'] = (2, 1)
    plt.rcParams['font.sans-serif'] = ['Helvetica']
    plt.rcParams['pdf.fonttype'] = 42
    plt.rcParams['text.color'] = 'k'

    fig = plt.figure(figsize=(5,3))
    ax = fig.add_subplot()

    for k,i in ax.spines.items():  i.set_linewidth(0.5)
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)

    ax.set_xscale('log')

    for name, color, res, na in zip(
            ['CSC1', 'CSC2', 'CSC3', 'Full'], ['b','r','g', 'y'], ress, nas
    ):
        ax.axhline(y=na, color=color, linestyle='--', linewidth=.5)
        ax.errorbar(xovery, [r[0] for r in res],
                    yerr=[r[1] for r in res], fmt='_-', label=name, color=color, linewidth=.5)

    ax.set_xlabel('reward delay / inter cue interval')
    ax.set_ylabel('RPE')
    ax.legend()
    plt.savefig('./s6_rpes.pdf')


def plot6atheory(all_res="./s6theory.pickle"):  # plots the data to PDF
    import pickle
    with open(all_res, "rb") as fp:
        all_res, pgs, xs = pickle.load(fp)
    print(all_res)
    ress, theories = all_res

    plt.rcParams['axes.titlesize'] = 10
    plt.rcParams['axes.labelsize'] = 8
    plt.rcParams['xtick.labelsize'] = 8
    plt.rcParams['ytick.labelsize'] = 8
    plt.rcParams['legend.fontsize'] = 8
    plt.rcParams['legend.labelspacing'] = 0.2
    plt.rcParams['axes.labelpad'] = 2
    plt.rcParams['axes.linewidth'] = 0.35
    plt.rcParams['xtick.major.size'] = 1
    plt.rcParams['xtick.major.width'] = 0.35
    plt.rcParams['xtick.major.pad'] = 3
    plt.rcParams['ytick.major.size'] = 1
    plt.rcParams['ytick.major.width'] = 0.35
    plt.rcParams['ytick.major.pad'] = 2
    plt.rcParams['lines.scale_dashes'] = False
    plt.rcParams['lines.dashed_pattern'] = (2, 1)
    plt.rcParams['font.sans-serif'] = ['Helvetica']
    plt.rcParams['pdf.fonttype'] = 42
    plt.rcParams['text.color'] = 'k'

    fig = plt.figure(figsize=(5,3))
    ax = fig.add_subplot()

    for k,i in ax.spines.items():  i.set_linewidth(0.5)
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)

    ax.axhline(y=0., color='black', linestyle='--', linewidth=.5)

    for name, color, res, theory in zip(
            ['p=%.2f, gamma=%.2f'%pg for pg in pgs], ['b','r','g', 'y'], ress, theories
    ):
        ax.errorbar(xs, [r[0] for r in res],
                    yerr=[r[1] for r in res], fmt='_-', label=name, color=color, linewidth=.5)
        ax.plot(xs, [r[0] for r in theory], '--', color=color, linewidth=.5)

    ax.set_xlabel('reward delay (measured in time bins)')
    ax.set_ylabel('RPE')
    ax.legend()
    plt.savefig('./s6_rpes_theory.pdf')


def plot6atheoryshort(all_res="./s6theorys.pickle"):  # plots the data to PDF
    import pickle
    with open(all_res, "rb") as fp:
        all_res, xpg = pickle.load(fp)
    print(all_res)
    ress, theories = all_res

    plt.rcParams['axes.titlesize'] = 10
    plt.rcParams['axes.labelsize'] = 8
    plt.rcParams['xtick.labelsize'] = 8
    plt.rcParams['ytick.labelsize'] = 8
    plt.rcParams['legend.fontsize'] = 8
    plt.rcParams['legend.labelspacing'] = 0.2
    plt.rcParams['axes.labelpad'] = 2
    plt.rcParams['axes.linewidth'] = 0.35
    plt.rcParams['xtick.major.size'] = 1
    plt.rcParams['xtick.major.width'] = 0.35
    plt.rcParams['xtick.major.pad'] = 3
    plt.rcParams['ytick.major.size'] = 1
    plt.rcParams['ytick.major.width'] = 0.35
    plt.rcParams['ytick.major.pad'] = 2
    plt.rcParams['lines.scale_dashes'] = False
    plt.rcParams['lines.dashed_pattern'] = (2, 1)
    plt.rcParams['font.sans-serif'] = ['Helvetica']
    plt.rcParams['pdf.fonttype'] = 42
    plt.rcParams['text.color'] = 'k'

    fig = plt.figure(figsize=(3,4))
    ax = fig.add_subplot()

    for k,i in ax.spines.items():  i.set_linewidth(0.5)
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)

    xs = [x[0] for x in xpg]
    inds = list(range(len(xs)))
    ax.set_xticks(inds, xs)
    ax.set_xlim([-1, len(xs)])

    means = [r[0] for r in ress]
    stds = [r[1] for r in ress]

    ax.bar(inds, means, color='b', alpha=0.5)
    ax.errorbar(inds, means, yerr=stds, color='black', fmt='_', label='TD(0)')
    ax.scatter(inds, theories, color='r', label='Theory', marker='x')

    ax.set_xlabel('X=Y (measured in time bins)')
    ax.set_ylabel('RPE')
    ax.legend()
    plt.savefig('./s6_rpes_theory_short.pdf')


if __name__ == '__main__':
    task6a()
    task6atheory()
    task6atheoryshort()
    plot6a()
    plot6atheory()
    plot6atheoryshort()