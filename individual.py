import random, copy
from problem import *

class Individual:
    '''Class Individual stores information about one individual.
    Each Individual object has its own genotype, which codes the solution to given problem.'''

    def __init__(self, problem):
        '''Object of Indiividual stores information about the problem and genotype, which is a solution to it.
        As arguments takes:
        problem - Problem object containing information about the problem structure'''
        
        self._problem = problem
        self._genotype_length = problem.number_of_variables
        self.genotype = []
    
    @property
    def genotype_length(self):
        '''Returns length of genotype of the Individual object.'''
        return self._genotype_length

    def set_random_values(self):
        '''Assigns random binary values (0 and 1) to genotype of Individual.'''   
        self.genotype = [random.randint(0, 1) for _ in range(self.genotype_length)]
            
    def print_genotype(self):
        '''Prints genotype of Individual.'''        
        print(self.genotype)

    def crossover(self, other, prob_cross, prob_cross_gene):
        '''Returns two children (Individual objects) of Individual as tuple. 
        Childrens' genotypes can be copies of their parents' genotypes or the cross of their genotypes.
        As arguments takes:
        other - second parent of children
        prob_cross - probability of crossover of genotypes of two parents
        prob_cross_gene - probability of taking given gene from another parent'''
        
        child1 = copy.deepcopy(self)
        child2 = copy.deepcopy(other)

        if random.uniform(0.0, 1.0) <= prob_cross:
            for i in range(self.genotype_length):
                if random.uniform(0.0, 1.0) <= prob_cross_gene:
                    child1.genotype[i] = other.genotype[i]
                    child2.genotype[i] = self.genotype[i]

        return child1, child2

    def mutation(self, prob_smart_mut, prob_gene_switch):
        '''Modifies the genotype of the Individual object resembling mutation of organisms in real-life.
        As arguments takes:
        prob_smart_mut - probability of mutation happening only if the mutation will contribute to better
        quality of solution coded in genotype
        prob_gene_switch - probability of mutation of a single gene'''
        
        if random.uniform(0.0, 1.0) <= prob_smart_mut:
            for i in range(self.genotype_length):
                if random.uniform(0.0, 1.0) <= prob_gene_switch:
                    current_state_for_variable = self._problem.check_clauses_with_variable(i, self.genotype)
                    self.switch_gene_value(i)

                    if self._problem.check_clauses_with_variable(i, self.genotype) < current_state_for_variable:
                        self.switch_gene_value(i)
        else:
            for i in range(self.genotype_length):
                if random.uniform(0.0, 1.0) <= prob_gene_switch:
                    self.switch_gene_value(i)


    def switch_gene_value(self, gene_index):
        '''Switches gene value from 0 to 1 and from 1 to 0.
        As arguments takes:
        gene_index - position in genotype of gene to switch'''
        
        if self.genotype[gene_index] == 0:
            self.genotype[gene_index] = 1
        else:
            self.genotype[gene_index] = 0

    def fitness(self):
        '''Returns Integer value telling how many of clauses present in the problem are fullfilled.'''      
        return self._problem.compute(self.genotype)

    def quality(self):
        '''Returns Real value telling percent of fullfilled clauses present in the problem.'''      
        return round(self._problem.evaluate(self.genotype) * 100, 2)

    def code_genotype(self):
        '''Returns String value with genotype as binary code.'''
        
        result = ""

        for gene in self.genotype:
            result += str(gene)

        return result