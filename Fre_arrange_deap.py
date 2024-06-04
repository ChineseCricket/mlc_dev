'''
下一步：
0. 修正评价函数最后端，考虑其为非同频的噪声电压
1. 改用Geatpy库
2. 设计局部搜索优化函数
3. 使用机器学习：该方法时我们要做的应该是对模型进行预训练，使其泛化到更通用的LC阵列结构。
'''
import numpy as np
import random
import matplotlib.pyplot as plt
from deap import creator, base, tools, algorithms
import multiprocessing
import sys

#统计每个cell收到的串扰
Arangement = np.array([
    1e6, 1.2e6, 1.3e6, 1.4e6, 1.5e6,
    1.6e6, 1.7e6, 1.8e6, 1.9e6, 2.0e6,
    2.1e6, 2.2e6, 2.3e6, 2.4e6, 2.5e6,
    2.6e6, 2.7e6, 2.8e6, 2.9e6, 3.0e6,
    3.1e6, 3.2e6, 3.3e6, 3.4e6, 3.5e6,
    3.6e6, 3.7e6, 3.8e6, 3.9e6, 4.0e6,
    4.1e6, 4.2e6, 4.3e6, 4.4e6, 4.5e6,
    4.6e6, 4.7e6, 4.8e6, 4.9e6, 5.0e6
])
# Arangement = np.array([
#     1e6, 2e6, 3.1e6, 4.1e6, 5e6,
#     1.8e6, 4.2e6, 2.5e6, 1.7e6, 3.2e6,
#     3.3e6, 2.2e6, 4.3e6, 2.9e6, 4.8e6,
#     4.9e6, 3.9e6, 1.2e6, 1.9e6, 3.4e6,
#     1.3e6, 2.1e6, 4.7e6, 3.5e6, 1.6e6,
#     3.6e6, 4.4e6, 1.5e6, 2.3e6, 2.8e6,
#     4.0e6, 2.7e6, 3.7e6, 1.4e6, 4.5e6,
#     4.6e6, 2.4e6, 3.0e6, 2.6e6, 3.8e6
# ])
Position = np.array([
    (1,1),(1,2),(1,3),(1,4),(1,5),
    (3,1),(3,2),(3,3),(3,4),(3,5),
    (5,1),(5,2),(5,3),(5,4),(5,5),
    (7,1),(7,2),(7,3),(7,4),(7,5),
    (9,1),(9,2),(9,3),(9,4),(9,5),
    (11,1),(11,2),(11,3),(11,4),(11,5),
    (13,1),(13,2),(13,3),(13,4),(13,5),
    (15,1),(15,2),(15,3),(15,4),(15,5)
])

# Define the fitness function
def Q_func(f):
    R = 10e-3
    L = 3e-6
    return 2*np.pi*f*L/R

def bode_basic_RLC(f1,f2):
    Q = Q_func(f1)
    # print(Q)
    return (1 + Q*(f2/f1-f1/f2)**2)**(-10)

def Crosstalk(f1,f2,p1,p2):
    '''
    2对1的串扰电压大小。
    '''
    p1 = np.array(p1)
    p2 = np.array(p2)
    # print(f1,f2,p1,p2)
    M = (np.linalg.norm(p1-p2)**(-4))
    I = bode_basic_RLC(f1,f2)
    return I*f2*M

def Ucs(individual):
    Ucs = []
    newArrange = Arangement[individual]
    for i,f1 in enumerate(newArrange):
        Uc = 0
        for j,f2 in enumerate(newArrange):
            if f2 != f1:
                Uc += Crosstalk(f1,f2,Position[i],Position[j])
        Ucs.append(Uc)
    return np.array(Ucs)

def fitness(individual):
    Ucs = []
    newArrange = Arangement[individual]
    for i,f1 in enumerate(newArrange):
        Uc = 0
        for j,f2 in enumerate(newArrange):
            if f2 != f1:
                Uc += Crosstalk(f1,f2,Position[i],Position[j])
        Ucs.append(Uc)
    return np.array(Ucs).max(), #也许max(Ucs)更合适？

def opt(individual, k=2):
    # 该局部搜索算法仅适用于经典TSP问题
    n = len(individual)
    optimizedArrange = individual
    minUc = fitness(optimizedArrange)
    for i in range(1,n-2):
        for j in range(i+k, n):
            if j-i == 1:
                continue
            reversedArrange = individual[:i]+individual[i:j][::-1]+individual[j:]# 部分翻转后的排列
            reversedUc = fitness(reversedArrange)
            # 如果翻转后路径更优，则更新最优解
            if  reversedUc < minUc:
                minUc = reversedUc
                optimizedArrange = reversedArrange
    return optimizedArrange, minUc

def main():
    # 初始化多核运行
    pool = multiprocessing.Pool(processes=16)

    # Define the individual and the population
    ngen = 1000
    npop = 400
    cxpb = 0.75
    mutpb = 0.2
    # creator.create("MultiObjMin", base.Fitness, weights=(-1.0,-1.0))
    # creator.create("Individual", list, fitness=creator.MultiObjMin)
    creator.create("ObjMin", base.Fitness, weights=(-1.0,))
    creator.create("Individual", list, fitness=creator.ObjMin)

    toolbox = base.Toolbox()
    toolbox.register("map", pool.map)

    toolbox.register("indices", random.sample, range(len(Arangement)), len(Arangement))
    toolbox.register("individual", tools.initIterate, creator.Individual, toolbox.indices)
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)
    pop = toolbox.population(n=npop)

    # Define the genetic operators
    toolbox.register("mate", tools.cxPartialyMatched)
    toolbox.register("mutate", tools.mutShuffleIndexes, indpb=0.2)
    toolbox.register("select", tools.selTournament, tournsize=2)
    toolbox.register("evaluate", fitness)
    toolbox.register("localOpt", opt) # 优化函数

    #generate statistics recording
    # stats_avg = tools.Statistics(key=lambda ind: ind.fitness.values[0])
    # stats_std = tools.Statistics(key=lambda ind: ind.fitness.values[1])
    # stats = tools.MultiStatistics(avg=stats_avg, std=stats_std)
    stats = tools.Statistics(key=lambda ind: ind.fitness.values)
    stats.register('avg', np.mean)
    stats.register('min', np.min)
    logbook = tools.Logbook()
    logbook.header = ['gen', 'nevals'] + (stats.fields)

    ## 实现遗传算法
    # 评价族群
    invalid_ind = [ind for ind in pop if not ind.fitness.valid]
    fitnesses = toolbox.map(toolbox.evaluate, invalid_ind)
    for ind, fit in zip(invalid_ind, fitnesses):
        ind.fitness.values = fit
    # 记录数据
    record = stats.compile(pop)
    logbook.record(gen=0, nevals=len(invalid_ind), **record)

    for gen in range(1, ngen+1): # 方便输出数据好看
        print("Generation: ", gen, end='\r')
        sys.stdout.flush()
        # 配种选择
        offspring = toolbox.select(pop, 2*npop)
        offspring = [toolbox.clone(_) for _ in offspring] #一定要复制，否则在交叉和突变这样的原位操作中，会改变所有select出来的同个体副本
        # 变异操作 - 交叉
        for child1, child2 in zip(offspring[::2], offspring[1::2]):
            if random.random() < cxpb:
                toolbox.mate(child1, child2)
                del child1.fitness.values
                del child2.fitness.values
        # 变异操作 - 突变
        for mutant in offspring:
            if random.random() < mutpb:
                toolbox.mutate(mutant)
                del mutant.fitness.values
        # 评价当前没有fitness的个体，确保整个族群中的个体都有对应的适应度
        invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
        fitnesses = toolbox.map(toolbox.evaluate, invalid_ind)
        for ind, fit in zip(invalid_ind, fitnesses):
            ind.fitness.values = fit
        # 环境选择 - 保留精英
        pop = tools.selBest(offspring, npop, fit_attr='fitness') # 选择精英,保持种群规模
        # pop[:] = offspring
        
        # # 对族群中的精英进行优化
        # nOpt = int(npop/10)
        # toBeOpt = tools.selBest(pop, nOpt)
        # for ind in toBeOpt:
        #     ind[:], ind.fitness.values = toolbox.localOpt(ind)
        #     # print(ind.fitness.values)
        
        # 记录数据
        record = stats.compile(pop)
        logbook.record(gen=gen, nevals=len(invalid_ind), **record)

    # # Generate the initial population
    # pop = toolbox.population(n=100)
    # hof = tools.HallOfFame(1)

    # # Run the genetic algorithm
    # result, logbook = algorithms.eaSimple(pop, toolbox, cxpb=0.5, mutpb=0.2, ngen=1000, stats = stats, halloffame=hof, verbose=True)

    pool.close()
    
    # 取出最优解
    best_ind = tools.selBest(pop, 1)[0]
    bestUcs = Ucs(best_ind)
    print("Best Arrangement is ", Arangement[best_ind].reshape(8,5),"\n its Ucs are", bestUcs.reshape(8,5), "\n with parameters: std:", bestUcs.std(), "mean:" ,bestUcs.mean())
    # show logbook
    record = stats.compile(pop)
    gen = logbook.select("gen")
    avg_mins = logbook.select("min")
    avg_avgs = logbook.select("avg")
    # avg_mins = logbook.chapters["avg"].select("min")
    # avg_avgs = logbook.chapters["avg"].select("avg")
    # std_mins = logbook.chapters["std"].select("min")
    # std_avgs = logbook.chapters["std"].select("avg")    
    # print(logbook)
    fig, ax1 = plt.subplots(1,1)
    ax1.plot(gen,avg_mins)
    ax1.plot(gen,avg_avgs)
    ax1.set_yscale('log')
    # ax2 = ax1.twinx()
    # ax2.plot(gen,std_mins, 'r')
    # ax2.plot(gen,std_avgs, 'b')
    # ax2.set_yscale('log')
    plt.xscale('log')
    plt.show()

if __name__ == '__main__':
    main()