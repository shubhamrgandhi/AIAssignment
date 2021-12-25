from CNF_Creator import *
import time
import numpy as np
import matplotlib.pyplot as plt

def fitness(state, sentence):
    cnt = 0 # variable to store the number of clauses satisfied
    # print('\n', state, '\n')
    for clause in sentence:
        for element in clause:

            if (element < 0):
                element = element*(-1)
                if(state[element-1] == 0):
                    cnt += 1
                    break

            else:
                if(state[element-1] == 1):
                    cnt += 1
                    break
    
    return (cnt/len(sentence))*100


def parSelection(population, fits):
    total_fitness = fits.sum()
    probs = fits/total_fitness

    # Random selection with weighted probabilities according to fitness values
    parsind1 = np.random.choice(list(range(len(population))), len(population), p = probs, replace=True)
    parsind2 = np.random.choice(list(range(len(population))), len(population), p = probs, replace=True)
    # print("\nparSelection\n")
    # print(parsind1)
    # print("\n\n")
    pars1 = population[parsind1]
    pars2 = population[parsind2]
    # for i in range(len(parsind1)):
    #     pars1 = np.concatenate((pars1, [population[parsind1[i]]]), axis = 0)
    #     pars2 = np.concatenate((pars2, [population[parsind2[i]]]), axis = 0)

    return pars1, pars2


def crossover(par1, par2, cross_prob):
    child1 = par1.copy()
    child2 = par2.copy()

    # Crossover with a probability
    if(np.random.rand() < cross_prob):
        cross_pt = np.random.randint(1, 49) # Doesn't make sense to have the crossover point as the first or last index
        child1 = np.append(par1[:cross_pt], par2[cross_pt:]).tolist()
        child2 = np.append(par2[:cross_pt], par1[cross_pt:]).tolist()
    
    # print("\n\n")
    # print(par1)
    # print("\n\n")

    return child1, child2


def mutate(state, mut_prob):
    for i in range(len(state)):
        # Mutation with a probability
        if(np.random.rand() < mut_prob):
            state[i] = 1 - state[i]
    return state


def geneticAlgorithm(sentence, generations = 10000, pop_size = 20, cross_prob = 0.99, mut_prob = 0.01, restart_prob = 0.01):
    start_time = time.time()
    population = np.array([np.random.randint(0, 2, 50).tolist() for _ in range(pop_size)])

    # print('\n', population, '\n')

    best_state = population[0]
    best_fit = fitness(population[0], sentence)
    cnt_plateau = 0 # Variable to count the number of iterations without improvement
    for gen in range(generations):
        fits = np.zeros(pop_size)
        for i in range(pop_size):
            fits[i] = fitness(population[i], sentence)
        new_pop = []
        
        for i in range(pop_size):
          if (fits[i] > best_fit):
              best_state = population[i]
              best_fit = fits[i]
              cnt_plateau = 0
          else:
              cnt_plateau += 1


        pars1, pars2 = parSelection(population, fits)
        # print("\npars1")
        # print(pars1)
        # print("\n\n")
        for i in range(len(pars1)):
            child1, child2 = crossover(pars1[i], pars2[i], cross_prob)
            # print("\nChild 1\n")
            # print(child1, "\n")
            if fitness(child1, sentence) > fitness(child2, sentence):
                child1 = mutate(child1, mut_prob)
                new_pop.append(child1)
            else:
                child2 = mutate(child2, mut_prob)
                new_pop.append(child2)

        # print('\n', population, '\n')
        population = np.array(new_pop)
        # print('\n', population, '\n')
        # if(gen%1000 == 0):
        #     print("Best Fit Yet : ", best_fit)

        # Early stopping    
        if(time.time() - start_time > 45 or best_fit == 100 or (cnt_plateau > 20000 and len(sentence) >= 200)):  
            # print("Best Fit Yet : ", best_fit)
            # print("\nStopping now")
            break

        # Random restart with a probability restart_prob
        if(np.random.rand() < restart_prob):
            population = np.array([np.random.randint(0, 2, 50).tolist() for _ in range(pop_size)])
    return best_state, best_fit

# def plotAvg(cnfC, num_samples = 10):
#     xfit = []
#     yfit = []
#     xtime = []
#     ytime = []

#     for m in range(100, 301, 20):
#         sum_fit = 0
#         sum_time = 0
#         for i in range(num_samples):
#             print(f'\nFor m = {m}')
#             print(f'For sample = {i+1}\n')
#             sentence = cnfC.CreateRandomSentence(m=m)
#             start_time = time.time()
#             best_state, best_fit = geneticAlgorithm(sentence)
#             sum_fit += best_fit
#             sum_time += time.time() - start_time
        
#         avg_fit = sum_fit/num_samples
#         avg_time = sum_time/num_samples
#         xfit.append(m)
#         yfit.append(avg_fit)
#         xtime.append(m)
#         ytime.append(avg_time)

#     return xfit, yfit, xtime, ytime

def main():
    cnfC = CNF_Creator(n=50) # n is number of symbols in the 3-CNF sentence
    # sentence = cnfC.CreateRandomSentence(m=100) # m is number of clauses in the 3-CNF sentence
    # print('Random sentence : ',sentence)

    sentence = cnfC.ReadCNFfromCSVfile()
    print('\nSentence from CSV file : ',sentence)
    
    start_time = time.time()
    
    best_state, best_fit = geneticAlgorithm(sentence)
    time_taken = time.time() - start_time
    best_model = np.zeros(len(best_state), dtype="int")

    # I have represented states as 0's and 1's so converting those states to actual variables for the model.

    for i in range(len(best_state)):
        if(best_state[i] == 1):
            best_model[i] = i+1
        else:
            best_model[i] = (-1)*(i+1)

    print('\n\n')
    print('Roll No : 2019A7PS0086G')
    print('Number of clauses in CSV file : ',len(sentence))
    print('Best model : ', best_model.tolist())
    print('Fitness value of best model : ', best_fit, "%")
    print('Time taken : {:.2} seconds'.format(time_taken))
    print('\n\n')

    # xfit, yfit, xtime, ytime = plotAvg(cnfC, 50)

    # plt.plot(xfit, yfit)
    # plt.xlabel('m')
    # plt.ylabel('Average Fitness Value of Best Model')
    # plt.title('Average Best Fitness Value vs m')
    # plt.show()

    # plt.plot(xtime, ytime)
    # plt.xlabel('m')
    # plt.ylabel('Average Running Time')
    # plt.title('Average Running Time vs m')
    # plt.show()

if __name__=='__main__':
    main()


