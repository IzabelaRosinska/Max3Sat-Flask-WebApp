import random
from individual import *
from problem import *

class Optimizer:
    '''Class Optimizer creates at least one population (list) of Individuals.
    Individual interact only in the scope of their population.
    Stores information about populations and allows their evolution.
    Manages optimization of solutions to the problem.'''

    def __init__(self, problem, size_of_population, number_of_populations, probability_of_smart_mutation, probability_of_gene_mutation, probability_of_crossover, probability_of_cross_gene, number_of_parents_considered):
        '''Object manages optimization of solutions to the problem. 
        As arguments takes:
        problem - Problem object containing information about the problem structure
        size_of_population - number of Individuals creating one population
        number_of_populations - number of separated lists of Individuals
        probability_of_smart_mutation - probability of mutation happening only if the mutation will contribute to better
        quality of solution coded in Individual's genotype
        probability_of_gene_mutation - probability of mutation of a single gene
        probability_of_crossover - probability of crossover of genotypes of two parents
        probability_of_cross_gene - probability of taking given gene from another parent
        number_of_parents_considered - number of Individuals taken into consideration to become parent to new
        pair of Individuals. Only one Individual with best quality solution coded in genotype is chosen to be a parent.'''
        
        self._problem = problem
        self._best_found = None
        self._size_of_population = size_of_population
        self._number_of_populations = number_of_populations
        self._current_best_individual_fitness = 0

        self._probability_of_smart_mutation = probability_of_smart_mutation
        self._probability_of_gene_mutation = probability_of_gene_mutation

        self._probability_of_cross = probability_of_crossover
        self._probability_of_cross_gene = probability_of_cross_gene

        self._parent_candidate_number = number_of_parents_considered
        self._populations = []

    @property
    def best_found(self):
        '''Returns Individual object with best quality of solution coded in genotype found by Optimizer'''     
        return self._best_found
    
    @property
    def current_best_individual_fitness(self):
        '''Returns number of fullfiled clauses by Individual object with best quality 
        of solution coded in genotype found by Optimizer'''     
        return self._current_best_individual_fitness

    def initialize(self):
        '''Prepares newly created Optimizer object to work (optimization).'''
        
        for _ in range(self._number_of_populations):
            population = []
            for _ in range(self._size_of_population):
                population.append(Individual(self._problem))
                population[-1].set_random_values()

            self.find_best(population)
            self._populations.append(population)

    def run_iteration(self):
        '''Runs one iteration of optimization in each population stored in Optimizer object.'''
        
        for i in range(self._number_of_populations):
            self.run_iteration_one_population(self._populations[i])

    def run_iteration_one_population(self, population):
        '''Runs one iteration of optimization in given population stored in Optimizer object.
        As arguments takes:
        population - list of Individual objects creating one separated population'''
        
        new_population = []

        while len(new_population) < self._size_of_population:
            index_parent_1 = self.choose_parent(population)
            index_parent_2 = self.choose_parent(population)

            child1, child2 = population[index_parent_1].crossover(population[index_parent_2], self._probability_of_cross, self._probability_of_cross_gene)

            child1.mutation(self._probability_of_smart_mutation, self._probability_of_gene_mutation)
            child2.mutation(self._probability_of_smart_mutation, self._probability_of_gene_mutation)

            new_population.append(child1)
            new_population.append(child2)

        population = new_population
        self.find_best(population)

    def choose_parent(self, population):
        '''Returns Integer value being the index of Individual with best quality solution coded in genotype. 
        Considers number of Individuals speficied in self._parent_candidate_number.
        As arguments takes:
        population - list of Individual objects creating one separated population'''
        
        index_of_fittest_parent = 0
        fitness_of_fittest_parent = 0 

        for _ in range(self._parent_candidate_number):
            current_parent = random.randint(0, self._size_of_population - 1)
            current_fitness = population[current_parent].fitness()

            if current_fitness > fitness_of_fittest_parent:
                fitness_of_fittest_parent = current_fitness
                index_of_fittest_parent = current_parent

        return index_of_fittest_parent

    def find_best(self, population):
        '''Finds Individual with best quality solution coded in genotype in given population. 
        As arguments takes:
        population - list of Individual objects creating one separated population'''
        
        index_of_fittest = 0
        fitness_of_fittest = 0

        for i in range(self._size_of_population):
            current_fitness = population[i].fitness()

            if current_fitness > fitness_of_fittest:
                fitness_of_fittest = current_fitness
                index_of_fittest = i

        if fitness_of_fittest > self._current_best_individual_fitness:
            self._current_best_individual_fitness = fitness_of_fittest
            self._best_found = population[index_of_fittest]